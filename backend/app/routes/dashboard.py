"""Personalized Dashboard Overview route using live database queries."""

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import get_current_user
from app.database.session import get_db
from app.models.entities import (
    ChatMessage,
    ChatSession,
    MedicalReport,
    ReportSummary,
    UploadedImage,
    User,
    UserActivity,
)
from app.routes.auth import serialize_user

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("/overview")
async def get_dashboard_overview(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    from app.ai.local_engine import detect_ollama_model
    settings = get_settings()

    total_reports = (
        db.query(func.count(MedicalReport.id))
        .filter(MedicalReport.user_id == current_user.id)
        .scalar()
        or 0
    )
    summarized_reports = (
        db.query(func.count(ReportSummary.id))
        .filter(ReportSummary.user_id == current_user.id)
        .scalar()
        or 0
    )
    total_chat_sessions = (
        db.query(func.count(ChatSession.id))
        .filter(ChatSession.user_id == current_user.id)
        .scalar()
        or 0
    )
    total_chat_messages = (
        db.query(func.count(ChatMessage.id))
        .filter(ChatMessage.user_id == current_user.id)
        .scalar()
        or 0
    )
    total_images = (
        db.query(func.count(UploadedImage.id))
        .filter(UploadedImage.user_id == current_user.id)
        .scalar()
        or 0
    )
    total_symptom_checks = (
        db.query(func.count(UserActivity.id))
        .filter(
            UserActivity.user_id == current_user.id,
            UserActivity.activity_type == "symptom_check",
        )
        .scalar()
        or 0
    )

    recent_reports = (
        db.query(MedicalReport)
        .filter(MedicalReport.user_id == current_user.id)
        .order_by(MedicalReport.created_at.desc())
        .limit(5)
        .all()
    )
    recent_chats = (
        db.query(ChatSession)
        .filter(ChatSession.user_id == current_user.id)
        .order_by(ChatSession.updated_at.desc())
        .limit(5)
        .all()
    )
    recent_activity = (
        db.query(UserActivity)
        .filter(UserActivity.user_id == current_user.id)
        .order_by(UserActivity.created_at.desc())
        .limit(8)
        .all()
    )

    return {
        "user": serialize_user(current_user),
        "stats": {
            "total_reports": total_reports,
            "summarized_reports": summarized_reports,
            "total_chat_sessions": total_chat_sessions,
            "total_chat_messages": total_chat_messages,
            "total_images": total_images,
            "total_symptom_checks": total_symptom_checks,
        },
        "recent_reports": [
            {
                "id": r.id,
                "original_filename": r.original_filename,
                "status": r.status,
                "extraction_method": r.extraction_method,
                "has_summary": r.summary is not None,
                "created_at": r.created_at,
            }
            for r in recent_reports
        ],
        "recent_chats": [
            {
                "id": c.id,
                "title": c.title,
                "message_count": len(c.messages),
                "updated_at": c.updated_at,
            }
            for c in recent_chats
        ],
        "recent_activity": [
            {
                "id": a.id,
                "activity_type": a.activity_type,
                "description": a.description,
                "created_at": a.created_at,
            }
            for a in recent_activity
        ],
        "ai_status": await (lambda: _build_ai_status(settings, detect_ollama_model))(),
        "database_mode": "ephemeral_sqlite" if settings.is_ephemeral_serverless_db else "persistent",
    }


async def _build_ai_status(settings, detect_ollama_model):
    ollama_model = None
    if not settings.is_ai_configured:
        ollama_model = await detect_ollama_model(settings.ollama_model or None)
    if settings.is_ai_configured:
        return {
            "configured": True,
            "ready": True,
            "mode": "cloud_ai",
            "ollama_model": None,
            "provider": settings.effective_provider,
            "chat_model": settings.effective_chat_model,
            "vision_model": settings.effective_vision_model,
        }
    if ollama_model:
        return {
            "configured": True,
            "ready": True,
            "mode": "ollama_local",
            "ollama_model": ollama_model,
            "provider": "ollama",
            "chat_model": ollama_model,
            "vision_model": ollama_model,
        }
    return {
        "configured": False,
        "ready": True,
        "mode": "built_in_offline",
        "ollama_model": None,
        "provider": "local-engine",
        "chat_model": "built-in-educational-engine",
        "vision_model": "local-pillow-inspector",
    }
