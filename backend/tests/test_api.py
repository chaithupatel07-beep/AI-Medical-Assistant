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


def test_chat_offline_engine_and_mocked_ai_turn():
    alice = _register_user("chat@example.com")
    headers = _auth_header(alice["access_token"])
    sess_id = client.post("/api/chat/sessions", headers=headers, json={}).json()["id"]

    # Without external API keys or Ollama, built-in offline engine responds with 200
    with patch("app.services.ai_service.detect_ollama_model", new=AsyncMock(return_value=None)):
        offline = client.post(
            f"/api/chat/sessions/{sess_id}/messages",
            headers=headers,
            json={"content": "What does HbA1c mean?"},
        )
        assert offline.status_code == 200
        offline_body = offline.json()
        assert offline_body["ai_model"] == "built-in-educational-engine"
        assert "HbA1c" in offline_body["assistant_message"]["content"]

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


def test_report_upload_validation_markers_and_isolation(tmp_path):
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

    # Even if ephemeral local disk file disappears, DB file_data fallback serves the original file
    for f in (tmp_path / "uploads" / "reports").rglob("*"):
        if f.is_file():
            f.unlink()
    dl_orig = client.get(f"/api/reports/{report_id}/file", headers=alice_h)
    assert dl_orig.status_code == 200
    assert dl_orig.content.startswith(b"%PDF-")

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


def test_v1_endpoints_and_pymupdf():
    assert client.get("/health").status_code == 200
    v1_health = client.get("/api/v1/health")
    assert v1_health.status_code == 200
    assert v1_health.json()["status"] == "ok"

    user = _register_user("v1_user@example.com", "V1 Tester")
    token = user["access_token"]
    headers = _auth_header(token)

    verify = client.post("/api/v1/auth/verify", json={"token": token})
    assert verify.status_code == 200
    assert verify.json()["valid"] is True

    me = client.get("/api/v1/auth/me", headers=headers)
    assert me.status_code == 200
    assert me.json()["email"] == "v1_user@example.com"

    dash = client.get("/api/v1/dashboard", headers=headers)
    assert dash.status_code == 200
    assert dash.json()["stats"]["total_reports"] == 0

    pdf_bytes = _make_minimal_pdf_bytes()
    upload = client.post(
        "/api/v1/reports/upload",
        headers=headers,
        files={"file": ("pymupdf_test.pdf", pdf_bytes, "application/pdf")},
    )
    assert upload.status_code == 201
    assert upload.json()["extraction_method"] == "pymupdf"
    assert "Hemoglobin" in (upload.json()["extracted_text"] or "")

    articles = client.get("/api/v1/health/articles", params={"lang": "te"})
    assert articles.status_code == 200
    assert articles.json()["total"] == 12


def test_offline_symptoms_report_image_and_v1_auth():
    # Register/login/logout via /api/v1/auth/*
    reg = client.post(
        "/api/v1/auth/register",
        json={
            "email": "v1_offline@example.com",
            "password": "Password123!",
            "full_name": "Offline Tester",
        },
    )
    assert reg.status_code == 201
    login_res = client.post(
        "/api/v1/auth/login",
        json={"email": "v1_offline@example.com", "password": "Password123!"},
    )
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    headers = _auth_header(token)

    with patch("app.ai.local_engine.detect_ollama_model", new=AsyncMock(return_value=None)):
        health = client.get("/health")
        assert health.status_code == 200
        assert health.json()["ai_ready"] is True
        assert health.json()["ai_mode"] == "built_in_offline"

    with patch("app.services.ai_service.detect_ollama_model", new=AsyncMock(return_value=None)):
        sym = client.post(
            "/api/symptoms/check",
            headers=headers,
            json={
                "age": 30,
                "main_symptom": "fever and headache",
                "duration": "2 days",
                "severity": "moderate",
                "severity_score": 6,
            },
        )
        assert sym.status_code == 200
        assert sym.json()["ai_model"] == "built-in-rules-engine"
        assert sym.json()["severity_score"] == 6
        assert len(sym.json()["questions_for_doctor_en"]) >= 1
        assert len(sym.json()["possible_explanations"]) >= 1

        pdf_bytes = _make_minimal_pdf_bytes()
        rep = client.post(
            "/api/reports/upload",
            headers=headers,
            files={"file": ("offline_cbc.pdf", pdf_bytes, "application/pdf")},
        )
        assert rep.status_code == 201
        rep_id = rep.json()["id"]
        summary = client.post(f"/api/reports/{rep_id}/summarize", headers=headers)
        assert summary.status_code == 200
        assert summary.json()["summary"]["ai_model"] == "local-deterministic-parser"

        # Valid 2x2 PNG bytes via Pillow for local image inspector
        from io import BytesIO
        from PIL import Image

        buf = BytesIO()
        Image.new("RGB", (24, 24), color=(180, 120, 120)).save(buf, format="PNG")
        img_up = client.post(
            "/api/images/upload",
            headers=headers,
            files={"file": ("skin_sample.png", buf.getvalue(), "image/png")},
            data={"image_context": "Mild redness on forearm"},
        )
        assert img_up.status_code == 201
        img_id = img_up.json()["id"]
        analyzed = client.post(f"/api/images/{img_id}/analyze", headers=headers)
        assert analyzed.status_code == 200
        assert analyzed.json()["ai_model"] == "local-pillow-inspector"

    out = client.post("/api/v1/auth/logout", headers=headers)
    assert out.status_code == 200


def test_token_refresh_and_ephemeral_serverless_rehydration(monkeypatch):
    user = _register_user("persist@example.com", "Persistent Patient")
    token = user["access_token"]
    user_id = user["user"]["id"]
    headers = _auth_header(token)

    refreshed = client.post("/api/auth/refresh", headers=headers)
    assert refreshed.status_code == 200
    assert refreshed.json()["user"]["email"] == "persist@example.com"
    new_token = refreshed.json()["access_token"]

    v1_refreshed = client.post("/api/v1/auth/refresh", headers=_auth_header(new_token))
    assert v1_refreshed.status_code == 200

    # Simulate cold serverless /tmp SQLite instance where user row isn't created yet
    from app.database.session import SessionLocal
    from app.models.entities import User

    with SessionLocal() as db:
        db.query(User).filter(User.id == user_id).delete()
        db.commit()

    monkeypatch.setattr("app.core.security.get_settings", lambda: type("S", (), {
        "jwt_secret_key": get_settings().jwt_secret_key,
        "jwt_algorithm": get_settings().jwt_algorithm,
        "supabase_jwt_secret": "",
        "is_ephemeral_serverless_db": True,
    })())

    me = client.get("/api/auth/me", headers=_auth_header(new_token))
    assert me.status_code == 200
    assert me.json()["email"] == "persist@example.com"


def test_chat_auto_create_missing_session_and_isolation():
    alice = _register_user("autochat_a@example.com", "Alice")
    bob = _register_user("autochat_b@example.com", "Bob")
    alice_h = _auth_header(alice["access_token"])
    bob_h = _auth_header(bob["access_token"])

    with patch("app.services.ai_service.detect_ollama_model", new=AsyncMock(return_value=None)):
        # 1. Direct send with no session_id auto-creates session titled from message
        direct = client.post(
            "/api/chat/send",
            headers=alice_h,
            json={"content": "What does hemoglobin measure?", "language": "en"},
        )
        assert direct.status_code == 200
        created_id = direct.json()["session"]["id"]
        assert "hemoglobin" in direct.json()["session"]["title"].lower()

        # 2. Sending to a stale/non-existent session_id auto-creates it instead of 404
        stale = client.post(
            "/api/chat/sessions/missing-session-123/messages",
            headers=alice_h,
            json={"content": "Follow-up on HbA1c", "language": "en"},
        )
        assert stale.status_code == 200
        assert stale.json()["session"]["id"] == "missing-session-123"

        # 3. Cross-user access to Alice's existing session remains blocked with 404
        cross = client.post(
            f"/api/chat/sessions/{created_id}/messages",
            headers=bob_h,
            json={"content": "Trying Alice session", "language": "en"},
        )
        assert cross.status_code == 404




