"""Symptom Information Checker API routes."""

import json
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.safety import detect_emergency_signals, normalize_language
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
            [
                payload.main_symptom,
                payload.additional_symptoms or "",
                payload.aggravating_factors or "",
                payload.relevant_context or "",
            ],
        )
    )
    lang = normalize_language(payload.language)
    emergency_detected, emergency_reasons = detect_emergency_signals(combined_text, lang)

    guidance, model_used = await generate_symptom_guidance(
        payload.model_dump(),
        emergency_detected=emergency_detected,
        emergency_reasons=emergency_reasons,
        language=lang,
    )

    severity_label = (
        f"{payload.severity} ({payload.severity_score}/10)"
        if payload.severity_score is not None
        else payload.severity
    )
    activity = log_activity(
        db,
        user_id=current_user.id,
        activity_type="symptom_check",
        description=f"Checked symptom info: {payload.main_symptom} ({severity_label}, {payload.duration}).",
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


@router.delete("/{activity_id}")
def delete_symptom_entry(
    activity_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    row = (
        db.query(UserActivity)
        .filter(
            UserActivity.id == activity_id,
            UserActivity.user_id == current_user.id,
            UserActivity.activity_type == "symptom_check",
        )
        .first()
    )
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Symptom record not found.")
    db.delete(row)
    db.commit()
    return {"message": "Symptom record deleted."}
