"""Pydantic schemas for Chat, Symptoms, Medical Reports, Images, and Activity."""

from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, Field


LanguageCode = Literal["en", "te", "hi"]


class ChatSessionCreate(BaseModel):
    title: Optional[str] = Field(None, max_length=200)


class ChatMessageCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=4000)
    language: LanguageCode = "en"


class ChatDirectSendRequest(BaseModel):
    session_id: Optional[str] = Field(None, max_length=64)
    content: str = Field(..., min_length=1, max_length=4000)
    language: LanguageCode = "en"


class ChatMessageResponse(BaseModel):
    id: str
    session_id: str
    role: str
    content: str
    emergency_flagged: bool
    created_at: datetime


class ChatSessionResponse(BaseModel):
    id: str
    title: str
    created_at: datetime
    updated_at: datetime
    message_count: int = 0
    last_message_preview: Optional[str] = None


class ChatSessionDetailResponse(ChatSessionResponse):
    messages: List[ChatMessageResponse]


class ChatTurnResponse(BaseModel):
    session: ChatSessionResponse
    user_message: ChatMessageResponse
    assistant_message: ChatMessageResponse
    emergency_detected: bool
    emergency_reasons: List[str] = []
    emergency_banner: Optional[str] = None
    ai_model: str
    disclaimer: str


class SymptomCheckRequest(BaseModel):
    age: int = Field(..., ge=0, le=120)
    gender: Optional[str] = Field(None, max_length=32)
    main_symptom: str = Field(..., min_length=2, max_length=300)
    duration: str = Field(..., min_length=1, max_length=120)
    severity: Literal["mild", "moderate", "severe"]
    severity_score: Optional[int] = Field(None, ge=1, le=10)
    additional_symptoms: Optional[str] = Field(None, max_length=1500)
    relevant_context: Optional[str] = Field(None, max_length=1500)
    language: LanguageCode = "en"


class PossibleExplanationItem(BaseModel):
    title: str
    description: str


class SymptomCheckResponse(BaseModel):
    activity_id: str
    educational_overview: str
    possible_explanations: List[PossibleExplanationItem]
    recommended_next_steps: List[str]
    warning_signs: List[str]
    when_to_consult_doctor: str
    questions_for_doctor: List[str]
    questions_for_doctor_en: List[str] = []
    severity_score: Optional[int] = None
    emergency_detected: bool
    emergency_reasons: List[str] = []
    emergency_banner: Optional[str] = None
    ai_model: str
    disclaimer: str


class LabMarkerItem(BaseModel):
    name: str
    value: str
    unit: str = ""
    reference_range: str = "Not specified in report"
    status: Literal["high", "low", "normal", "unknown"] = "unknown"
    explanation: str = ""


class MedicalTermItem(BaseModel):
    term: str
    simple_explanation: str


class ReportSummaryResponse(BaseModel):
    id: str
    report_id: str
    plain_summary: str
    lab_markers: List[LabMarkerItem]
    medical_terms: List[MedicalTermItem]
    questions_for_doctor: List[str]
    warnings: List[str]
    ai_model: Optional[str] = None
    disclaimer: str
    created_at: datetime


class MedicalReportResponse(BaseModel):
    id: str
    original_filename: str
    mime_type: str
    file_size_bytes: int
    extraction_method: str
    extracted_text: Optional[str] = None
    status: str
    created_at: datetime
    summary: Optional[ReportSummaryResponse] = None


class MedicalImageResponse(BaseModel):
    id: str
    original_filename: str
    mime_type: str
    file_size_bytes: int
    image_context: Optional[str] = None
    analysis_summary: Optional[str] = None
    observations: List[str] = []
    limitations: Optional[str] = None
    recommended_next_steps: Optional[str] = None
    ai_model: Optional[str] = None
    status: str
    disclaimer: str
    created_at: datetime


class ActivityItemResponse(BaseModel):
    id: str
    activity_type: str
    description: str
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    metadata_json: Optional[str] = None
    created_at: datetime
