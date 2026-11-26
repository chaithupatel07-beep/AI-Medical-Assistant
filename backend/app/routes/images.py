"""Medical Image Upload, Vision AI Observation, and Secure File Access routes."""

import json
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.safety import IMAGE_DISCLAIMER
from app.core.security import get_current_user
from app.database.session import get_db
from app.models.entities import UploadedImage, User
from app.schemas.medical import MedicalImageResponse
from app.services.ai_service import analyze_medical_image_with_vision
from app.utils.activity import log_activity
from app.utils.file_validation import delete_stored_file, validate_and_store_upload

router = APIRouter(prefix="/api/images", tags=["Medical Image Analysis"])


def _serialize_image(img: UploadedImage) -> MedicalImageResponse:
    return MedicalImageResponse(
        id=img.id,
        original_filename=img.original_filename,
        mime_type=img.mime_type,
        file_size_bytes=img.file_size_bytes,
        image_context=img.image_context,
        analysis_summary=img.analysis_summary,
        observations=json.loads(img.observations_json or "[]"),
        limitations=img.limitations,
        recommended_next_steps=img.recommended_next_steps,
        ai_model=img.ai_model,
        status=img.status,
        disclaimer=IMAGE_DISCLAIMER,
        created_at=img.created_at,
    )


def _get_owned_image(db: Session, image_id: str, user_id: str) -> UploadedImage:
    record = (
        db.query(UploadedImage)
        .filter(UploadedImage.id == image_id, UploadedImage.user_id == user_id)
        .first()
    )
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Medical image not found.")
    return record


@router.post("/upload", response_model=MedicalImageResponse, status_code=status.HTTP_201_CREATED)
async def upload_medical_image(
    file: UploadFile = File(...),
    image_context: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    original_name, stored_name, storage_path, mime_type, size_bytes, _raw = (
        await validate_and_store_upload(file, current_user.id, kind="images")
    )

    record = UploadedImage(
        user_id=current_user.id,
        original_filename=original_name,
        stored_filename=stored_name,
        storage_path=storage_path,
        mime_type=mime_type,
        file_size_bytes=size_bytes,
        image_context=(image_context or "").strip()[:1000] or None,
        status="uploaded",
    )
    db.add(record)
    db.flush()

    log_activity(
        db,
        user_id=current_user.id,
        activity_type="image_upload",
        description=f"Uploaded medical image '{original_name}'.",
        resource_type="uploaded_image",
        resource_id=record.id,
    )
    db.commit()
    db.refresh(record)
    return _serialize_image(record)


@router.post("/{image_id}/analyze", response_model=MedicalImageResponse)
async def analyze_medical_image(
    image_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    record = _get_owned_image(db, image_id, current_user.id)
    path = Path(record.storage_path)
    if not path.is_file():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stored image file missing.")

    raw_bytes = path.read_bytes()
    analysis, model_used = await analyze_medical_image_with_vision(
        raw_bytes=raw_bytes,
        mime_type=record.mime_type,
        image_context=record.image_context,
    )

    record.analysis_summary = analysis.get("analysis_summary", "")
    record.observations_json = json.dumps(analysis.get("observations", []))
    record.limitations = analysis.get("limitations", "")
    record.recommended_next_steps = analysis.get("recommended_next_steps", "")
    record.ai_model = model_used
    record.status = "analyzed"

    log_activity(
        db,
        user_id=current_user.id,
        activity_type="image_analysis",
        description=f"Generated Vision AI observations for '{record.original_filename}'.",
        resource_type="uploaded_image",
        resource_id=record.id,
        metadata={"ai_model": model_used},
    )
    db.commit()
    db.refresh(record)
    return _serialize_image(record)


@router.get("", response_model=List[MedicalImageResponse])
def list_images(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    items = (
        db.query(UploadedImage)
        .filter(UploadedImage.user_id == current_user.id)
        .order_by(UploadedImage.created_at.desc())
        .all()
    )
    return [_serialize_image(item) for item in items]


@router.get("/{image_id}", response_model=MedicalImageResponse)
def get_image(
    image_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    record = _get_owned_image(db, image_id, current_user.id)
    return _serialize_image(record)


@router.get("/{image_id}/file")
def view_medical_image(
    image_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    record = _get_owned_image(db, image_id, current_user.id)
    path = Path(record.storage_path)
    if not path.is_file():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stored image not found.")
    return FileResponse(
        path=str(path),
        media_type=record.mime_type,
        filename=record.original_filename,
    )


@router.delete("/{image_id}")
def delete_image(
    image_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    record = _get_owned_image(db, image_id, current_user.id)
    filename = record.original_filename
    storage_path = record.storage_path
    db.delete(record)
    log_activity(
        db,
        user_id=current_user.id,
        activity_type="record_deleted",
        description=f"Deleted medical image '{filename}'.",
        resource_type="uploaded_image",
        resource_id=image_id,
    )
    db.commit()
    delete_stored_file(storage_path)
    return {"message": "Medical image deleted successfully."}
