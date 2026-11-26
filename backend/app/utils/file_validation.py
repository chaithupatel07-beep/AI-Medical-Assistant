"""Secure upload validation (extension, MIME, magic bytes, Pillow image check, user-isolated storage)."""

from io import BytesIO
from pathlib import Path
import re
from typing import Set, Tuple
import uuid

from fastapi import HTTPException, UploadFile, status
from PIL import Image, UnidentifiedImageError

from app.core.config import get_settings

REPORT_ALLOWED_EXTENSIONS: Set[str] = {".pdf", ".jpg", ".jpeg", ".png"}
IMAGE_ALLOWED_EXTENSIONS: Set[str] = {".jpg", ".jpeg", ".png"}

MIME_BY_EXTENSION = {
    ".pdf": "application/pdf",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
}


def sanitize_filename(filename: str) -> str:
    base = Path(filename or "upload").name
    cleaned = re.sub(r"[^A-Za-z0-9._-]", "_", base).strip("._")
    return cleaned[:120] or "upload"


def _detect_magic_type(data: bytes) -> str | None:
    if data.startswith(b"%PDF-"):
        return "application/pdf"
    if data.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    return None


async def validate_and_store_upload(
    file: UploadFile,
    user_id: str,
    *,
    kind: str,
) -> Tuple[str, str, str, str, int, bytes]:
    """Validate an uploaded report or medical image and store it inside a user-scoped folder."""
    settings = get_settings()
    allowed_ext = REPORT_ALLOWED_EXTENSIONS if kind == "reports" else IMAGE_ALLOWED_EXTENSIONS

    original_name = sanitize_filename(file.filename or "file")
    ext = Path(original_name).suffix.lower()
    if ext not in allowed_ext:
        allowed_str = ", ".join(sorted(e.lstrip(".").upper() for e in allowed_ext))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file format '{ext or 'unknown'}'. Allowed formats: {allowed_str}.",
        )

    raw_bytes = await file.read()
    size_bytes = len(raw_bytes)
    if size_bytes == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty.",
        )
    if size_bytes > settings.max_upload_size_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds the maximum allowed size of {settings.max_upload_size_mb} MB.",
        )

    detected_mime = _detect_magic_type(raw_bytes)
    expected_mime = MIME_BY_EXTENSION[ext]
    if detected_mime != expected_mime:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File signature does not match its file extension. Please upload a valid file.",
        )

    if detected_mime in {"image/jpeg", "image/png"}:
        try:
            with Image.open(BytesIO(raw_bytes)) as img:
                img.verify()
        except (UnidentifiedImageError, Exception) as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded image appears corrupted or invalid.",
            ) from exc

    user_dir = (settings.upload_path / kind / user_id).resolve()
    user_dir.mkdir(parents=True, exist_ok=True)
    stored_filename = f"{uuid.uuid4()}{ext}"
    dest_path = (user_dir / stored_filename).resolve()

    if user_dir not in dest_path.parents:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid storage path.")

    dest_path.write_bytes(raw_bytes)
    return original_name, stored_filename, str(dest_path), detected_mime, size_bytes, raw_bytes


def delete_stored_file(storage_path: str) -> None:
    try:
        path = Path(storage_path)
        if path.is_file():
            path.unlink()
    except OSError:
        pass
