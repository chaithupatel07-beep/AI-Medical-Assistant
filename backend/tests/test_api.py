"""End-to-end API integration tests for AI Medical Assistant."""

from io import BytesIO
from pathlib import Path
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient
from PIL import Image
import pytest

from app.core.config import get_settings
from app.database.session import Base, engine
from app.main import app


@pytest.fixture(autouse=True)
def reset_database(tmp_path, monkeypatch):
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    settings = get_settings()
    monkeypatch.setattr(settings, "upload_dir", str(tmp_path / "uploads"))
    monkeypatch.setattr(settings, "openai_api_key", "your_openai_api_key_here")
    monkeypatch.setattr(settings, "gemini_api_key", "")
    yield
    Base.metadata.drop_all(bind=engine)


client = TestClient(app)


def _register_user(email: str, name: str = "Test Patient", password: str = "StrongPass!123"):
    res = client.post(
        "/api/auth/register",
        json={"email": email, "full_name": name, "password": password},
    )
    assert res.status_code == 201, res.text
    return res.json()


def _auth_header(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _make_png_bytes() -> bytes:
    buf = BytesIO()
    img = Image.new("RGB", (24, 24), color=(37, 99, 235))
    img.save(buf, format="PNG")
    return buf.getvalue()


def _make_minimal_pdf_bytes() -> bytes:
    # Minimal valid PDF with embedded text "Hemoglobin 13.5 g/dL (12.0 - 16.0)"
    stream = b"BT /F1 12 Tf 72 720 Td (Hemoglobin 13.5 g/dL (12.0 - 16.0)) Tj ET"
    objects = [
        b"1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj\n",
        b"2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj\n",
        b"3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >> endobj\n",
        f"4 0 obj << /Length {len(stream)} >> stream\n".encode() + stream + b"\nendstream endobj\n",
        b"5 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> endobj\n",
    ]
    pdf = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for obj in objects:
        offsets.append(len(pdf))
        pdf.extend(obj)
    xref_pos = len(pdf)
    pdf.extend(f"xref\n0 {len(offsets)}\n0000000000 65535 f \n".encode())
    for off in offsets[1:]:
        pdf.extend(f"{off:010d} 00000 n \n".encode())
    pdf.extend(
        f"trailer << /Size {len(offsets)} /Root 1 0 R >>\nstartxref\n{xref_pos}\n%%EOF\n".encode()
    )
    return bytes(pdf)


def test_health_and_library():
    health = client.get("/api/health")
    assert health.status_code == 200
    assert health.json()["status"] == "ok"
    assert health.json()["ai_configured"] is False

    cats = client.get("/api/library/categories")
    assert cats.status_code == 200
    assert len(cats.json()["categories"]) == 6

    articles = client.get("/api/library/articles", params={"category": "Nutrition", "q": "fiber"})
    assert articles.status_code == 200
    assert articles.json()["total"] >= 1


def test_auth_flow_password_validation_and_recovery():
    weak = client.post(
        "/api/auth/register",
        json={"email": "weak@example.com", "full_name": "Weak User", "password": "password"},
    )
    assert weak.status_code == 422

    reg = _register_user("alice@example.com", "Alice Smith")
    token = reg["access_token"]

    dup = client.post(
        "/api/auth/register",
        json={"email": "alice@example.com", "full_name": "Alice", "password": "StrongPass!123"},
    )
    assert dup.status_code == 409

    me = client.get("/api/auth/me", headers=_auth_header(token))
    assert me.status_code == 200
    assert me.json()["email"] == "alice@example.com"

    forgot = client.post("/api/auth/forgot-password", json={"email": "alice@example.com"})
    assert forgot.status_code == 200
    reset_token = forgot.json()["reset_token"]

    reset = client.post(
        "/api/auth/reset-password",
        json={"token": reset_token, "new_password": "NewStrongPass!456"},
    )
    assert reset.status_code == 200

    login = client.post(
        "/api/auth/login",
        json={"email": "alice@example.com", "password": "NewStrongPass!456"},
    )
    assert login.status_code == 200


def test_user_isolation_and_profile_activity():
    alice = _register_user("alice2@example.com", "Alice Two")
    bob = _register_user("bob@example.com", "Bob Builder")
    alice_h = _auth_header(alice["access_token"])
    bob_h = _auth_header(bob["access_token"])

    prof = client.put(
        "/api/users/profile",
        headers=alice_h,
        json={"age": 30, "blood_type": "O+", "allergies": "Penicillin", "preferred_units": "metric"},
    )
    assert prof.status_code == 200
    assert prof.json()["profile"]["blood_type"] == "O+"

    sess = client.post("/api/chat/sessions", headers=alice_h, json={"title": "Alice Private Chat"})
    assert sess.status_code == 201
    session_id = sess.json()["id"]

    # Bob cannot read or delete Alice's chat session
    assert client.get(f"/api/chat/sessions/{session_id}", headers=bob_h).status_code == 404
    assert client.delete(f"/api/chat/sessions/{session_id}", headers=bob_h).status_code == 404


def test_chat_unconfigured_503_and_mocked_ai_turn():
    alice = _register_user("chat@example.com")
    headers = _auth_header(alice["access_token"])
    sess_id = client.post("/api/chat/sessions", headers=headers, json={}).json()["id"]

    # Without OPENAI_API_KEY, returns honest 503 instead of fake AI text
    unconfigured = client.post(
        f"/api/chat/sessions/{sess_id}/messages",
        headers=headers,
        json={"content": "What does HbA1c mean?"},
    )
    assert unconfigured.status_code == 503

    # With mocked AI service, message + emergency detection + clear + delete work cleanly
    with patch(
        "app.routes.chat.generate_chat_reply",
        new=AsyncMock(return_value=("Emergency care guidance: please seek immediate medical care.", "gpt-4o-mini")),
    ):
        turn = client.post(
            f"/api/chat/sessions/{sess_id}/messages",
            headers=headers,
            json={"content": "I have severe chest pain and shortness of breath"},
        )
        assert turn.status_code == 200
        body = turn.json()
        assert body["emergency_detected"] is True
        assert "Chest pain or pressure" in body["emergency_reasons"]

    cleared = client.post(f"/api/chat/sessions/{sess_id}/clear", headers=headers)
    assert cleared.status_code == 200
    assert cleared.json()["messages"] == []


def test_report_upload_validation_markers_and_isolation():
    alice = _register_user("rep_alice@example.com")
    bob = _register_user("rep_bob@example.com")
    alice_h = _auth_header(alice["access_token"])
    bob_h = _auth_header(bob["access_token"])

    # Invalid file signature rejected
    bad = client.post(
        "/api/reports/upload",
        headers=alice_h,
        files={"file": ("fake.pdf", b"not-a-real-pdf", "application/pdf")},
    )
    assert bad.status_code == 400

    # Valid PDF uploaded and parsed
    pdf_bytes = _make_minimal_pdf_bytes()
    upload = client.post(
        "/api/reports/upload",
        headers=alice_h,
        files={"file": ("cbc_panel.pdf", pdf_bytes, "application/pdf")},
    )
    assert upload.status_code == 201
    report_id = upload.json()["id"]
    assert "Hemoglobin" in (upload.json()["extracted_text"] or "")

    markers = client.get(f"/api/reports/{report_id}/parsed-markers", headers=alice_h)
    assert markers.status_code == 200
    parsed = markers.json()["markers"]
    assert len(parsed) == 1
    assert parsed[0]["status"] == "normal"
    assert parsed[0]["reference_range"] == "12.0 - 16.0"

    # Bob cannot access Alice's report file
    assert client.get(f"/api/reports/{report_id}/file", headers=bob_h).status_code == 404

    # Mock AI summary + Markdown download + Dashboard count
    mock_summary = {
        "plain_summary": "Hemoglobin is within the printed reference range.",
        "lab_markers": [
            {
                "name": "Hemoglobin",
                "value": "13.5",
                "unit": "g/dL",
                "reference_range": "12.0 - 16.0",
                "status": "normal",
                "explanation": "Protein in red blood cells that carries oxygen.",
            }
        ],
        "medical_terms": [{"term": "Hemoglobin", "simple_explanation": "Oxygen-carrying protein"}],
        "questions_for_doctor": ["Are any follow-up labs needed?"],
        "warnings": [],
        "disclaimer": "Educational use only.",
    }
    with patch(
        "app.routes.reports.generate_report_summary",
        new=AsyncMock(return_value=(mock_summary, "gpt-4o-mini")),
    ):
        summarized = client.post(f"/api/reports/{report_id}/summarize", headers=alice_h)
        assert summarized.status_code == 200
        assert summarized.json()["status"] == "summarized"

    dl = client.get(f"/api/reports/{report_id}/summary/download", headers=alice_h)
    assert dl.status_code == 200
    assert "Hemoglobin" in dl.text

    dash = client.get("/api/dashboard/overview", headers=alice_h)
    assert dash.status_code == 200
    assert dash.json()["stats"]["total_reports"] == 1
    assert dash.json()["stats"]["summarized_reports"] == 1


def test_image_upload_and_delete():
    alice = _register_user("img_alice@example.com")
    alice_h = _auth_header(alice["access_token"])

    png_bytes = _make_png_bytes()
    upload = client.post(
        "/api/images/upload",
        headers=alice_h,
        data={"image_context": "Forearm skin check"},
        files={"file": ("sample.png", png_bytes, "image/png")},
    )
    assert upload.status_code == 201
    image_id = upload.json()["id"]

    view = client.get(f"/api/images/{image_id}/file", headers=alice_h)
    assert view.status_code == 200
    assert view.headers["content-type"] == "image/png"

    delete = client.delete(f"/api/images/{image_id}", headers=alice_h)
    assert delete.status_code == 200
    assert client.get(f"/api/images/{image_id}", headers=alice_h).status_code == 404


def test_multilingual_telugu_hindi_english():
    for code, expected_cat in [("en", "Nutrition"), ("te", "పోషకాహారం"), ("hi", "पोषण")]:
        lib = client.get("/api/library/articles", params={"lang": code, "category": "Nutrition"})
        assert lib.status_code == 200
        data = lib.json()
        assert data["category_labels"]["Nutrition"] == expected_cat
        assert data["total"] >= 1

        qs = client.get("/api/chat/suggested-questions", params={"lang": code})
        assert qs.status_code == 200
        assert len(qs.json()["questions"]) >= 5

    user = _register_user("lang_user@example.com", "Language User")
    h = _auth_header(user["access_token"])
    prof = client.put("/api/users/profile", headers=h, json={"preferred_language": "te"})
    assert prof.status_code == 200
    assert prof.json()["profile"]["preferred_language"] == "te"


def test_production_database_url_normalization():
    settings = get_settings()
    orig = settings.database_url
    orig_pg = settings.postgres_url
    try:
        settings.database_url = "postgres://user:pass@host:5432/dbname"
        assert settings.normalized_database_url == "postgresql+psycopg://user:pass@host:5432/dbname"
        settings.database_url = "postgresql://user:pass@host:5432/dbname"
        assert settings.normalized_database_url == "postgresql+psycopg://user:pass@host:5432/dbname"
        settings.database_url = "sqlite:////tmp/test.db"
        settings.postgres_url = "postgres://neon:pass@ep-cool.aws.neon.tech/neondb?sslmode=require"
        assert settings.normalized_database_url == "postgresql+psycopg://neon:pass@ep-cool.aws.neon.tech/neondb?sslmode=require"
    finally:
        settings.database_url = orig
        settings.postgres_url = orig_pg


def test_gemini_api_key_autodetection_and_sanitization():
    settings = get_settings()
    orig_oai = settings.openai_api_key
    orig_gem = settings.gemini_api_key
    orig_prov = settings.ai_provider
    orig_base = settings.openai_base_url
    orig_chat = settings.openai_chat_model
    orig_vis = settings.openai_vision_model
    try:
        settings.openai_api_key = ""
        settings.gemini_api_key = ' "AIzaSyTestGeminiKey123" '
        settings.ai_provider = "openai"
        settings.openai_base_url = "https://api.openai.com/v1"
        settings.openai_chat_model = "gpt-4o-mini"
        settings.openai_vision_model = "gpt-4o-mini"
        assert settings.is_ai_configured is True
        assert settings.effective_api_key == "AIzaSyTestGeminiKey123"
        assert settings.effective_provider == "gemini"
        assert settings.effective_base_url == "https://generativelanguage.googleapis.com/v1beta/openai/"
        assert settings.effective_chat_model == "gemini-2.5-flash"
        assert settings.effective_vision_model == "gemini-2.5-flash"
    finally:
        settings.openai_api_key = orig_oai
        settings.gemini_api_key = orig_gem
        settings.ai_provider = orig_prov
        settings.openai_base_url = orig_base
        settings.openai_chat_model = orig_chat
        settings.openai_vision_model = orig_vis



