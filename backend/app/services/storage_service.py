"""Optional private Supabase Storage integration (server-side service-role only)."""

import logging
from typing import Optional

import httpx

from app.core.config import get_settings

logger = logging.getLogger("ai_medical_assistant.storage")


async def upload_to_supabase_storage(
    *,
    object_path: str,
    raw_bytes: bytes,
    mime_type: str,
) -> Optional[str]:
    """Upload a file to the private Supabase Storage bucket when configured."""
    settings = get_settings()
    if not settings.is_supabase_storage_configured:
        return None

    url = (
        f"{settings.supabase_url.rstrip('/')}/storage/v1/object/"
        f"{settings.supabase_storage_bucket}/{object_path.lstrip('/')}"
    )
    headers = {
        "Authorization": f"Bearer {settings.supabase_service_role_key}",
        "apikey": settings.supabase_service_role_key,
        "Content-Type": mime_type,
        "x-upsert": "true",
    }
    try:
        async with httpx.AsyncClient(timeout=20) as client:
            res = await client.post(url, headers=headers, content=raw_bytes)
            if res.status_code in (200, 201):
                return object_path
            logger.warning("Supabase Storage upload returned %s", res.status_code)
    except Exception as exc:
        logger.warning("Supabase Storage upload failed: %s", exc)
    return None


async def create_supabase_signed_url(object_path: str, expires_in: int = 300) -> Optional[str]:
    """Generate a short-lived signed URL for private Supabase Storage objects."""
    settings = get_settings()
    if not settings.is_supabase_storage_configured:
        return None

    url = (
        f"{settings.supabase_url.rstrip('/')}/storage/v1/object/sign/"
        f"{settings.supabase_storage_bucket}/{object_path.lstrip('/')}"
    )
    headers = {
        "Authorization": f"Bearer {settings.supabase_service_role_key}",
        "apikey": settings.supabase_service_role_key,
    }
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            res = await client.post(url, headers=headers, json={"expiresIn": expires_in})
            if res.status_code == 200:
                signed_path = res.json().get("signedURL")
                if signed_path:
                    return f"{settings.supabase_url.rstrip('/')}/storage/v1{signed_path}"
    except Exception as exc:
        logger.warning("Supabase signed URL generation failed: %s", exc)
    return None


async def delete_from_supabase_storage(object_path: str) -> None:
    settings = get_settings()
    if not settings.is_supabase_storage_configured:
        return

    url = f"{settings.supabase_url.rstrip('/')}/storage/v1/object/{settings.supabase_storage_bucket}"
    headers = {
        "Authorization": f"Bearer {settings.supabase_service_role_key}",
        "apikey": settings.supabase_service_role_key,
    }
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            await client.request("DELETE", url, headers=headers, json={"prefixes": [object_path.lstrip("/")]})
    except Exception as exc:
        logger.warning("Supabase Storage delete failed: %s", exc)
