"""Authentication, password hashing, complexity validation, and JWT utilities."""

from datetime import datetime, timedelta, timezone
import hashlib
import re
import secrets
from typing import Any, Dict, Tuple

import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import jwt
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.database.session import get_db
from app.models.entities import User, UserProfile

bearer_scheme = HTTPBearer(auto_error=False)


def validate_password_strength(password: str) -> None:
    """Enforce strong password rules consistently across registration, change, and reset."""
    errors = []
    if len(password) < 8:
        errors.append("at least 8 characters")
    if not re.search(r"[A-Z]", password):
        errors.append("one uppercase letter")
    if not re.search(r"[a-z]", password):
        errors.append("one lowercase letter")
    if not re.search(r"\d", password):
        errors.append("one number")
    if not re.search(r"[^A-Za-z0-9]", password):
        errors.append("one special character")
    if errors:
        raise ValueError(f"Password must contain {', '.join(errors)}.")


def hash_password(password: str) -> str:
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password(plain_password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), password_hash.encode("utf-8"))
    except Exception:
        return False


def create_access_token(subject: str, extra_claims: Dict[str, Any] | None = None) -> str:
    settings = get_settings()
    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(minutes=settings.access_token_expire_minutes)
    payload: Dict[str, Any] = {
        "sub": subject,
        "iat": int(now.timestamp()),
        "exp": int(expires_at.timestamp()),
    }
    if extra_claims:
        payload.update(extra_claims)
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> Dict[str, Any]:
    settings = get_settings()
    secrets_to_try = [settings.jwt_secret_key]
    if settings.supabase_jwt_secret.strip():
        secrets_to_try.append(settings.supabase_jwt_secret.strip())

    last_exc: Exception | None = None
    for secret in secrets_to_try:
        try:
            return jwt.decode(
                token,
                secret,
                algorithms=[settings.jwt_algorithm],
                options={"verify_aud": False},
            )
        except jwt.ExpiredSignatureError as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Your session has expired. Please sign in again.",
            ) from exc
        except jwt.PyJWTError as exc:
            last_exc = exc

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials.",
    ) from last_exc


def generate_reset_token() -> Tuple[str, str]:
    raw_token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(raw_token.encode("utf-8")).hexdigest()
    return raw_token, token_hash


def hash_reset_token(raw_token: str) -> str:
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    if not credentials or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required.",
        )
    payload = decode_access_token(credentials.credentials)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token.",
        )
    user = db.query(User).filter(User.id == user_id).first()
    if not user and get_settings().is_ephemeral_serverless_db:
        token_email = str(payload.get("email") or "").strip().lower()
        token_name = str(payload.get("full_name") or "").strip() or (
            token_email.split("@")[0] if token_email else "Patient"
        )
        if token_email:
            user = db.query(User).filter(User.email == token_email).first()
        if not user and token_email:
            # Cold-started serverless /tmp SQLite instance: restore verified JWT user record
            user = User(
                id=str(user_id),
                email=token_email,
                password_hash=hash_password(secrets.token_urlsafe(24)),
                full_name=token_name,
            )
            db.add(user)
            db.flush()
            db.add(UserProfile(user_id=user.id))
            db.commit()
            db.refresh(user)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account not found or inactive.",
        )
    return user
