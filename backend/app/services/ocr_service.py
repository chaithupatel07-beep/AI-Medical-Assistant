"""PDF text extraction (PyMuPDF primary + pypdf fallback) and image/scanned-PDF OCR."""

import base64
from io import BytesIO
import logging
import shutil
from typing import Tuple

import pymupdf as fitz
from openai import AsyncOpenAI
from PIL import Image
from pypdf import PdfReader
import pytesseract

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


def _render_first_pdf_page_png(raw_bytes: bytes) -> bytes | None:
    try:
        with fitz.open(stream=raw_bytes, filetype="pdf") as doc:
            if len(doc) == 0:
                return None
            pix = doc[0].get_pixmap(dpi=160)
            return pix.tobytes("png")
    except Exception as exc:
        logger.warning("PyMuPDF page render failed: %s", exc)
        return None


def _extract_image_text_tesseract(raw_bytes: bytes) -> str:
    settings = get_settings()
    tesseract_exe = settings.tesseract_cmd or shutil.which("tesseract")
    if not tesseract_exe:
        return ""
    pytesseract.pytesseract.tesseract_cmd = tesseract_exe
    with Image.open(BytesIO(raw_bytes)) as img:
        return (pytesseract.image_to_string(img) or "").strip()


async def _extract_image_text_vision_ai(raw_bytes: bytes, mime_type: str) -> str:
    settings = get_settings()
    if not settings.is_ai_configured:
        return ""
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
        logger.warning("Vision OCR fallback failed: %s", exc)
        return ""


async def _ocr_image_bytes(raw_bytes: bytes, mime_type: str) -> Tuple[str, str]:
    try:
        tesseract_text = _extract_image_text_tesseract(raw_bytes)
        if tesseract_text:
            return tesseract_text, "tesseract_ocr"
    except Exception as exc:
        logger.warning("Tesseract OCR failed: %s", exc)

    vision_text = await _extract_image_text_vision_ai(raw_bytes, mime_type)
    if vision_text:
        return vision_text, "vision_ai_ocr"

    return "", "ocr_unavailable"


async def extract_report_text(raw_bytes: bytes, mime_type: str) -> Tuple[str, str]:
    """Extract text from PDF (PyMuPDF + OCR fallback) or image reports."""
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

        # Scanned PDF fallback: render page 1 via PyMuPDF and run OCR
        rendered_png = _render_first_pdf_page_png(raw_bytes)
        if rendered_png:
            ocr_text, ocr_method = await _ocr_image_bytes(rendered_png, "image/png")
            if ocr_text:
                return ocr_text, f"pymupdf_{ocr_method}"

        return "", "pdf_no_embedded_text"

    if mime_type in {"image/jpeg", "image/png"}:
        return await _ocr_image_bytes(raw_bytes, mime_type)

    return "", "unsupported"
