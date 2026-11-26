"""Medical Report Upload, OCR Extraction, Summarization, and Secure File Access routes."""

import json
from pathlib import Path
from typing import List

from fastapi import APIRouter, Depends, File, HTTPException, Query, Response, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.safety import REPORT_DISCLAIMER, normalize_language
from app.core.security import get_current_user
from app.database.session import get_db
from app.models.entities import MedicalReport, ReportSummary, User
from app.schemas.medical import (
    LabMarkerItem,
    MedicalReportResponse,
    MedicalTermItem,
    ReportSummaryResponse,
)
from app.services.ai_service import generate_report_summary
from app.services.ocr_service import extract_report_text
from app.services.report_parser import format_summary_for_download, parse_lab_markers_from_text
from app.utils.activity import log_activity
from app.utils.file_validation import delete_stored_file, validate_and_store_upload

router = APIRouter(prefix="/api/reports", tags=["Medical Reports"])


def _serialize_summary(summary: ReportSummary) -> ReportSummaryResponse:
    return ReportSummaryResponse(
        id=summary.id,
        report_id=summary.report_id,
        plain_summary=summary.plain_summary,
        lab_markers=[LabMarkerItem(**m) for m in json.loads(summary.lab_markers_json or "[]")],
        medical_terms=[MedicalTermItem(**t) for t in json.loads(summary.medical_terms_json or "[]")],
        questions_for_doctor=json.loads(summary.questions_for_doctor_json or "[]"),
        warnings=json.loads(summary.warnings_json or "[]"),
        ai_model=summary.ai_model,
        disclaimer=summary.disclaimer,
        created_at=summary.created_at,
    )


def _serialize_report(report: MedicalReport) -> MedicalReportResponse:
    return MedicalReportResponse(
        id=report.id,
        original_filename=report.original_filename,
        mime_type=report.mime_type,
        file_size_bytes=report.file_size_bytes,
        extraction_method=report.extraction_method,
        extracted_text=report.extracted_text,
        status=report.status,
        created_at=report.created_at,
        summary=_serialize_summary(report.summary) if report.summary else None,
    )


def _get_owned_report(db: Session, report_id: str, user_id: str) -> MedicalReport:
    report = (
        db.query(MedicalReport)
        .filter(MedicalReport.id == report_id, MedicalReport.user_id == user_id)
        .first()
    )
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Medical report not found.")
    return report


@router.post("/upload", response_model=MedicalReportResponse, status_code=status.HTTP_201_CREATED)
async def upload_medical_report(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    original_name, stored_name, storage_path, mime_type, size_bytes, raw_bytes = (
        await validate_and_store_upload(file, current_user.id, kind="reports")
    )

    extracted_text, extraction_method = await extract_report_text(raw_bytes, mime_type)
    report_status = "extracted" if extracted_text else "uploaded"

    report = MedicalReport(
        user_id=current_user.id,
        original_filename=original_name,
        stored_filename=stored_name,
        storage_path=storage_path,
        mime_type=mime_type,
        file_size_bytes=size_bytes,
        extraction_method=extraction_method,
        extracted_text=extracted_text or None,
        file_data=raw_bytes,
        status=report_status,
    )
    db.add(report)
    db.flush()

    parsed_markers = parse_lab_markers_from_text(extracted_text) if extracted_text else []

    log_activity(
        db,
        user_id=current_user.id,
        activity_type="report_upload",
        description=f"Uploaded medical report '{original_name}' ({extraction_method}).",
        resource_type="medical_report",
        resource_id=report.id,
        metadata={"parsed_marker_count": len(parsed_markers), "extraction_method": extraction_method},
    )
    db.commit()
    db.refresh(report)
    return _serialize_report(report)


@router.post("/{report_id}/summarize", response_model=MedicalReportResponse)
async def summarize_medical_report(
    report_id: str,
    lang: str = Query("en"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    report = _get_owned_report(db, report_id, current_user.id)
    language = normalize_language(lang)

    if not report.extracted_text or not report.extracted_text.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                "No readable text could be extracted from this file. "
                "For scanned PDFs or images, install Tesseract OCR or configure OPENAI_API_KEY in backend/.env."
            ),
        )

    deterministic_markers = parse_lab_markers_from_text(report.extracted_text)
    summary_payload, model_used = await generate_report_summary(
        report.extracted_text, deterministic_markers, language=language
    )

    if report.summary:
        summary = report.summary
        summary.plain_summary = summary_payload.get("plain_summary", "")
        summary.lab_markers_json = json.dumps(summary_payload.get("lab_markers", []))
        summary.medical_terms_json = json.dumps(summary_payload.get("medical_terms", []))
        summary.questions_for_doctor_json = json.dumps(summary_payload.get("questions_for_doctor", []))
        summary.warnings_json = json.dumps(summary_payload.get("warnings", []))
        summary.ai_model = model_used
        summary.disclaimer = summary_payload.get("disclaimer", REPORT_DISCLAIMER)
    else:
        summary = ReportSummary(
            report_id=report.id,
            user_id=current_user.id,
            plain_summary=summary_payload.get("plain_summary", ""),
            lab_markers_json=json.dumps(summary_payload.get("lab_markers", [])),
            medical_terms_json=json.dumps(summary_payload.get("medical_terms", [])),
            questions_for_doctor_json=json.dumps(summary_payload.get("questions_for_doctor", [])),
            warnings_json=json.dumps(summary_payload.get("warnings", [])),
            ai_model=model_used,
            disclaimer=summary_payload.get("disclaimer", REPORT_DISCLAIMER),
        )
        db.add(summary)

    report.status = "summarized"
    log_activity(
        db,
        user_id=current_user.id,
        activity_type="report_summarize",
        description=f"Generated AI summary for '{report.original_filename}'.",
        resource_type="medical_report",
        resource_id=report.id,
        metadata={"ai_model": model_used},
    )
    db.commit()
    db.refresh(report)
    return _serialize_report(report)


@router.get("", response_model=List[MedicalReportResponse])
def list_reports(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    reports = (
        db.query(MedicalReport)
        .filter(MedicalReport.user_id == current_user.id)
        .order_by(MedicalReport.created_at.desc())
        .all()
    )
    return [_serialize_report(r) for r in reports]


@router.get("/{report_id}", response_model=MedicalReportResponse)
def get_report(
    report_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    report = _get_owned_report(db, report_id, current_user.id)
    return _serialize_report(report)


@router.get("/{report_id}/parsed-markers")
def get_deterministic_markers(
    report_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    report = _get_owned_report(db, report_id, current_user.id)
    return {"markers": parse_lab_markers_from_text(report.extracted_text or "")}


@router.get("/{report_id}/file")
def download_original_report(
    report_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    report = _get_owned_report(db, report_id, current_user.id)
    path = Path(report.storage_path)
    if path.is_file():
        return FileResponse(
            path=str(path),
            media_type=report.mime_type,
            filename=report.original_filename,
        )
    if report.file_data:
        return Response(
            content=report.file_data,
            media_type=report.mime_type,
            headers={"Content-Disposition": f'inline; filename="{report.original_filename}"'},
        )
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stored file not found.")


@router.get("/{report_id}/summary/download")
def download_report_summary(
    report_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    report = _get_owned_report(db, report_id, current_user.id)
    if not report.summary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No AI summary has been generated for this report yet.",
        )

    serialized = _serialize_summary(report.summary).model_dump()
    download_name, markdown_text = format_summary_for_download(
        filename=report.original_filename,
        created_at=report.summary.created_at.isoformat(),
        summary_data=serialized,
    )
    return Response(
        content=markdown_text,
        media_type="text/markdown; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{download_name}"'},
    )


@router.delete("/{report_id}")
def delete_report(
    report_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    report = _get_owned_report(db, report_id, current_user.id)
    filename = report.original_filename
    storage_path = report.storage_path
    db.delete(report)
    log_activity(
        db,
        user_id=current_user.id,
        activity_type="record_deleted",
        description=f"Deleted medical report '{filename}'.",
        resource_type="medical_report",
        resource_id=report_id,
    )
    db.commit()
    delete_stored_file(storage_path)
    return {"message": "Medical report deleted successfully."}
