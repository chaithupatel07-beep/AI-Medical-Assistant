"""Authentication routes: register, login, logout, forgot-password, reset-password, me."""

from datetime import datetime, timedelta, timezone
import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import (
    create_access_token,
    generate_reset_token,
    get_current_user,
    hash_password,
    hash_reset_token,
    verify_password,
)
from app.database.session import get_db
from app.models.entities import User, UserProfile
from app.schemas.auth import (
    AuthResponse,
    ForgotPasswordRequest,
    LoginRequest,
    RegisterRequest,
    ResetPasswordRequest,
    UserProfileResponse,
    UserResponse,
)
from app.utils.activity import log_activity

router = APIRouter(prefix="/api/auth", tags=["Authentication"])
logger = logging.getLogger("ai_medical_assistant.auth")


def serialize_user(user: User) -> UserResponse:
    profile_data = None
    if user.profile:
        profile_data = UserProfileResponse(
            date_of_birth=user.profile.date_of_birth,
            age=user.profile.age,
            gender=user.profile.gender,
            blood_type=user.profile.blood_type,
            allergies=user.profile.allergies,
            chronic_conditions=user.profile.chronic_conditions,
            emergency_contact=user.profile.emergency_contact,
            preferred_units=user.profile.preferred_units,
            preferred_language=getattr(user.profile, "preferred_language", "en") or "en",
            updated_at=user.profile.updated_at,
        )
    return UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        created_at=user.created_at,
        profile=profile_data,
    )


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    normalized_email = payload.email.strip().lower()
    existing = db.query(User).filter(User.email == normalized_email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists.",
        )

    user = User(
        email=normalized_email,
        password_hash=hash_password(payload.password),
        full_name=payload.full_name,
    )
    db.add(user)
    db.flush()

    profile = UserProfile(user_id=user.id)
    db.add(profile)
    log_activity(
        db,
        user_id=user.id,
        activity_type="register",
        description="Created AI Medical Assistant account.",
        resource_type="user",
        resource_id=user.id,
    )
    db.commit()
    db.refresh(user)

    token = create_access_token(subject=user.id, extra_claims={"email": user.email})
    return AuthResponse(access_token=token, user=serialize_user(user))


@router.post("/login", response_model=AuthResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    normalized_email = payload.email.strip().lower()
    user = db.query(User).filter(User.email == normalized_email).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This account has been deactivated.",
        )

    log_activity(
        db,
        user_id=user.id,
        activity_type="login",
        description="Signed in to AI Medical Assistant.",
        resource_type="user",
        resource_id=user.id,
    )
    db.commit()
    db.refresh(user)

    token = create_access_token(subject=user.id, extra_claims={"email": user.email})
    return AuthResponse(access_token=token, user=serialize_user(user))


@router.post("/logout")
def logout(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    log_activity(
        db,
        user_id=current_user.id,
        activity_type="logout",
        description="Signed out of session.",
        resource_type="user",
        resource_id=current_user.id,
    )
    db.commit()
    return {"message": "Logged out successfully."}


@router.post("/forgot-password")
def forgot_password(payload: ForgotPasswordRequest, db: Session = Depends(get_db)):
    settings = get_settings()
    normalized_email = payload.email.strip().lower()
    user = db.query(User).filter(User.email == normalized_email).first()

    response_payload = {
        "message": "If an account exists for this email address, password reset instructions have been prepared.",
        "delivery_mode": "development_preview" if settings.app_env == "development" else "email",
    }

    if user:
        raw_token, token_hash = generate_reset_token()
        user.reset_token_hash = token_hash
        user.reset_token_expires_at = datetime.now(timezone.utc) + timedelta(minutes=30)
        log_activity(
            db,
            user_id=user.id,
            activity_type="password_reset_requested",
            description="Requested a password reset token.",
            resource_type="user",
            resource_id=user.id,
        )
        db.commit()
        logger.info("Password reset token generated for user_id=%s", user.id)
        if settings.app_env == "development":
            response_payload["reset_token"] = raw_token

    return response_payload


@router.post("/reset-password")
def reset_password(payload: ResetPasswordRequest, db: Session = Depends(get_db)):
    token_hash = hash_reset_token(payload.token.strip())
    user = db.query(User).filter(User.reset_token_hash == token_hash).first()

    if not user or not user.reset_token_expires_at:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired password reset token.",
        )

    expires_at = user.reset_token_expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)

    if expires_at < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password reset token has expired. Please request a new one.",
        )

    user.password_hash = hash_password(payload.new_password)
    user.reset_token_hash = None
    user.reset_token_expires_at = None
    log_activity(
        db,
        user_id=user.id,
        activity_type="password_reset_completed",
        description="Reset account password.",
        resource_type="user",
        resource_id=user.id,
    )
    db.commit()
    return {"message": "Password has been reset successfully. You can now sign in."}


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return serialize_user(current_user)
