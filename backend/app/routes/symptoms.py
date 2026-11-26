"""Symptom Information Checker API routes."""

import json
from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.safety import detect_emergency_signals
from app.core.security import get_current_user
from app.database.session import get_db
from app.models.entities import User, UserActivity
from app.schemas.medical import ActivityItemResponse, SymptomCheckRequest, SymptomCheckResponse
from app.services.ai_service import generate_symptom_guidance
from app.utils.activity import log_activity

router = APIRouter(prefix="/api/symptoms", tags=["Symptom Checker"])


@router.post("/check", response_model=SymptomCheckResponse)
async def check_symptoms(
    payload: SymptomCheckRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    combined_text = " ".join(
        filter(
            None,
            [payload.main_symptom, payload.additional_symptoms or "", payload.relevant_context or ""],
        )
    )
    emergency_detected, emergency_reasons = detect_emergency_signals(combined_text)

    guidance, model_used = await generate_symptom_guidance(
        payload.model_dump(),
        emergency_detected=emergency_detected,
        emergency_reasons=emergency_reasons,
    )

    activity = log_activity(
        db,
        user_id=current_user.id,
        activity_type="symptom_check",
        description=f"Checked symptom info: {payload.main_symptom} ({payload.severity}, {payload.duration}).",
        resource_type="symptom_check",
        metadata={
            "request": payload.model_dump(),
            "response": guidance,
            "ai_model": model_used,
        },
    )
    db.commit()
    db.refresh(activity)

    return SymptomCheckResponse(
        activity_id=activity.id,
        ai_model=model_used,
        **guidance,
    )


@router.get("/history", response_model=List[ActivityItemResponse])
def symptom_check_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    rows = (
        db.query(UserActivity)
        .filter(
            UserActivity.user_id == current_user.id,
            UserActivity.activity_type == "symptom_check",
        )
        .order_by(UserActivity.created_at.desc())
        .limit(30)
        .all()
    )
    return [
        ActivityItemResponse(
            id=row.id,
            activity_type=row.activity_type,
            description=row.description,
            resource_type=row.resource_type,
            resource_id=row.resource_id,
            metadata_json=row.metadata_json,
            created_at=row.created_at,
        )
        for row in rows
    ]
