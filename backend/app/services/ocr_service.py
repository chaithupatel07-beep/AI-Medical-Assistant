"""PDF text extraction (PyMuPDF + pypdf) and native Google Gemini multimodal Vision extraction."""

import base64
from io import BytesIO
import logging
from typing import Tuple

import httpx
import pymupdf as fitz
from openai import AsyncOpenAI
from pypdf import PdfReader

from app.core.config import get_settings

logger = logging.getLogger("ai_medical_assistant.ocr")


def _extract_pdf_text_pymupdf(raw_bytes: bytes) -> str:
    chunks = []
    with fitz.open(stream=raw_bytes, filetype="pdf") as doc:
        for page in doc:
            text = (page.get_text("text") or "").strip()
            if text:
                chunks.append(text)
    return "\n\n".join(chunks).strip()


def _extract_pdf_text_pypdf(raw_bytes: bytes) -> str:
    reader = PdfReader(BytesIO(raw_bytes))
    chunks = []
    for page in reader.pages:
        text = page.extract_text() or ""
        if text.strip():
            chunks.append(text.strip())
    return "\n\n".join(chunks).strip()


def _render_pdf_pages_png(raw_bytes: bytes, max_pages: int = 3) -> list[bytes]:
    pages_png: list[bytes] = []
    try:
        with fitz.open(stream=raw_bytes, filetype="pdf") as doc:
            for page in doc[:max_pages]:
                pix = page.get_pixmap(dpi=160)
                pages_png.append(pix.tobytes("png"))
        return pages_png
    except Exception as exc:
        logger.warning("PyMuPDF page render failed: %s", exc)
        return pages_png


async def _extract_via_gemini_inline_data(raw_bytes: bytes, mime_type: str) -> str:
    settings = get_settings()
    if not settings.is_ai_configured or not settings._uses_gemini_key:
        return ""

    b64 = base64.b64encode(raw_bytes).decode("utf-8")
    prompt = (
        "Transcribe ALL visible text, lab test names, measured values, units, and printed "
        "reference ranges from this medical report line by line verbatim. "
        "Do not invent or infer missing numbers."
    )
    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [
                    {"text": prompt},
                    {"inlineData": {"mimeType": mime_type, "data": b64}},
                ],
            }
        ],
        "generationConfig": {"temperature": 0.0, "maxOutputTokens": 3000},
    }

    models_to_try = [settings.effective_vision_model]
    if "gemini-2.5-flash" not in models_to_try:
        models_to_try.append("gemini-2.5-flash")

    async with httpx.AsyncClient(timeout=40.0) as client:
        for model_name in models_to_try:
            url = (
                f"https://generativelanguage.googleapis.com/v1beta/models/"
                f"{model_name}:generateContent?key={settings.effective_api_key}"
            )
            try:
                res = await client.post(url, json=payload)
                if res.status_code == 404:
                    continue
                if res.status_code == 200:
                    data = res.json()
                    parts = data.get("candidates", [{}])[0].get("content", {}).get("parts", [])
                    text = "\n".join(p.get("text", "") for p in parts if isinstance(p, dict)).strip()
                    if text:
                        return text
                logger.warning("Gemini Vision transcription status %s: %s", res.status_code, res.text[:200])
                break
            except Exception as exc:
                logger.warning("Gemini Vision transcription failed: %s", exc)
                break
    return ""


async def _extract_image_text_vision_ai(raw_bytes: bytes, mime_type: str) -> str:
    settings = get_settings()
    if not settings.is_ai_configured:
        return ""
    if settings._uses_gemini_key:
        gemini_text = await _extract_via_gemini_inline_data(raw_bytes, mime_type)
        if gemini_text:
            return gemini_text

    client = AsyncOpenAI(
        api_key=settings.effective_api_key,
        base_url=settings.effective_base_url,
    )
    b64 = base64.b64encode(raw_bytes).decode("utf-8")
    data_url = f"data:{mime_type};base64,{b64}"
    try:
        extra_kwargs = (
            {"reasoning_effort": "low"}
            if settings.effective_provider.lower() == "gemini"
            or "generativelanguage.googleapis.com" in settings.effective_base_url
            else {}
        )
        response = await client.chat.completions.create(
            model=settings.effective_vision_model,
            temperature=0.0,
            max_tokens=2500,
            **extra_kwargs,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Transcribe all visible text, lab test names, measured values, units, "
                        "and printed reference ranges from this medical report image verbatim. "
                        "Do not invent or infer missing numbers or ranges."
                    ),
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Transcribe the report text accurately line by line."},
                        {"type": "image_url", "image_url": {"url": data_url}},
                    ],
                },
            ],
        )
        return (response.choices[0].message.content or "").strip()
    except Exception as exc:
        logger.warning("Vision transcription fallback failed: %s", exc)
        return ""


async def extract_report_text(raw_bytes: bytes, mime_type: str) -> Tuple[str, str]:
    """Extract text from PDF (PyMuPDF + Gemini multimodal fallback) or image reports."""
    if mime_type == "application/pdf":
        try:
            text = _extract_pdf_text_pymupdf(raw_bytes)
            if text:
                return text, "pymupdf"
        except Exception as exc:
            logger.warning("PyMuPDF extraction failed, trying pypdf: %s", exc)

        try:
            fallback_text = _extract_pdf_text_pypdf(raw_bytes)
            if fallback_text:
                return fallback_text, "pypdf"
        except Exception as exc:
            logger.warning("pypdf extraction failed: %s", exc)

        # Scanned PDF: try native Gemini inlineData directly first, then rendered pages
        gemini_pdf_text = await _extract_via_gemini_inline_data(raw_bytes, "application/pdf")
        if gemini_pdf_text:
            return gemini_pdf_text, "gemini_multimodal"

        rendered_pages = _render_pdf_pages_png(raw_bytes, max_pages=3)
        if rendered_pages:
            chunks = []
            for png_bytes in rendered_pages:
                vision_text = await _extract_image_text_vision_ai(png_bytes, "image/png")
                if vision_text:
                    chunks.append(vision_text)
            if chunks:
                return "\n\n".join(chunks), "gemini_vision"

        return "", "gemini_vision_pending"

    if mime_type in {"image/jpeg", "image/png", "image/webp"}:
        vision_text = await _extract_image_text_vision_ai(raw_bytes, mime_type)
        if vision_text:
            return vision_text, "gemini_vision"
        return "", "gemini_vision_pending"

    return "", "unsupported"
