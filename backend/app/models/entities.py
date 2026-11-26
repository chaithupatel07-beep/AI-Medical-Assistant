"""SQLAlchemy ORM models for the 8 core relational tables."""

from datetime import datetime, timezone
import uuid

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database.session import Base


def _uuid() -> str:
    return str(uuid.uuid4())


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=_uuid)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(150), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    reset_token_hash = Column(String(255), nullable=True)
    reset_token_expires_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=_utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=_utcnow, onupdate=_utcnow, nullable=False)

    profile = relationship(
        "UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    medical_reports = relationship(
        "MedicalReport", back_populates="user", cascade="all, delete-orphan"
    )
    report_summaries = relationship(
        "ReportSummary", back_populates="user", cascade="all, delete-orphan"
    )
    chat_sessions = relationship(
        "ChatSession", back_populates="user", cascade="all, delete-orphan"
    )
    chat_messages = relationship(
        "ChatMessage", back_populates="user", cascade="all, delete-orphan"
    )
    uploaded_images = relationship(
        "UploadedImage", back_populates="user", cascade="all, delete-orphan"
    )
    activities = relationship(
        "UserActivity", back_populates="user", cascade="all, delete-orphan"
    )


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(String(36), primary_key=True, default=_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    date_of_birth = Column(String(20), nullable=True)
    age = Column(Integer, nullable=True)
    gender = Column(String(32), nullable=True)
    blood_type = Column(String(16), nullable=True)
    allergies = Column(Text, nullable=True)
    chronic_conditions = Column(Text, nullable=True)
    emergency_contact = Column(String(150), nullable=True)
    preferred_units = Column(String(16), default="metric", nullable=False)
    updated_at = Column(DateTime(timezone=True), default=_utcnow, onupdate=_utcnow, nullable=False)

    user = relationship("User", back_populates="profile")


class MedicalReport(Base):
    __tablename__ = "medical_reports"

    id = Column(String(36), primary_key=True, default=_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    original_filename = Column(String(255), nullable=False)
    stored_filename = Column(String(255), nullable=False)
    storage_path = Column(String(500), nullable=False)
    mime_type = Column(String(100), nullable=False)
    file_size_bytes = Column(Integer, nullable=False)
    extraction_method = Column(String(50), nullable=False)
    extracted_text = Column(Text, nullable=True)
    status = Column(String(32), default="uploaded", nullable=False)
    created_at = Column(DateTime(timezone=True), default=_utcnow, nullable=False)

    user = relationship("User", back_populates="medical_reports")
    summary = relationship(
        "ReportSummary", back_populates="report", uselist=False, cascade="all, delete-orphan"
    )


class ReportSummary(Base):
    __tablename__ = "report_summaries"

    id = Column(String(36), primary_key=True, default=_uuid)
    report_id = Column(
        String(36), ForeignKey("medical_reports.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    plain_summary = Column(Text, nullable=False)
    lab_markers_json = Column(Text, default="[]", nullable=False)
    medical_terms_json = Column(Text, default="[]", nullable=False)
    questions_for_doctor_json = Column(Text, default="[]", nullable=False)
    warnings_json = Column(Text, default="[]", nullable=False)
    ai_model = Column(String(100), nullable=True)
    disclaimer = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), default=_utcnow, nullable=False)

    report = relationship("MedicalReport", back_populates="summary")
    user = relationship("User", back_populates="report_summaries")


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(String(36), primary_key=True, default=_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    title = Column(String(200), default="New Health Conversation", nullable=False)
    created_at = Column(DateTime(timezone=True), default=_utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=_utcnow, onupdate=_utcnow, nullable=False)

    user = relationship("User", back_populates="chat_sessions")
    messages = relationship(
        "ChatMessage",
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="ChatMessage.created_at",
    )


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(String(36), primary_key=True, default=_uuid)
    session_id = Column(
        String(36), ForeignKey("chat_sessions.id", ondelete="CASCADE"), index=True, nullable=False
    )
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    role = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
    emergency_flagged = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), default=_utcnow, nullable=False)

    session = relationship("ChatSession", back_populates="messages")
    user = relationship("User", back_populates="chat_messages")


class UploadedImage(Base):
    __tablename__ = "uploaded_images"

    id = Column(String(36), primary_key=True, default=_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    original_filename = Column(String(255), nullable=False)
    stored_filename = Column(String(255), nullable=False)
    storage_path = Column(String(500), nullable=False)
    mime_type = Column(String(100), nullable=False)
    file_size_bytes = Column(Integer, nullable=False)
    image_context = Column(Text, nullable=True)
    analysis_summary = Column(Text, nullable=True)
    observations_json = Column(Text, default="[]", nullable=False)
    limitations = Column(Text, nullable=True)
    recommended_next_steps = Column(Text, nullable=True)
    ai_model = Column(String(100), nullable=True)
    status = Column(String(32), default="uploaded", nullable=False)
    created_at = Column(DateTime(timezone=True), default=_utcnow, nullable=False)

    user = relationship("User", back_populates="uploaded_images")


class UserActivity(Base):
    __tablename__ = "user_activity"

    id = Column(String(36), primary_key=True, default=_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    activity_type = Column(String(64), nullable=False)
    description = Column(String(500), nullable=False)
    resource_type = Column(String(64), nullable=True)
    resource_id = Column(String(36), nullable=True)
    metadata_json = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=_utcnow, nullable=False)

    user = relationship("User", back_populates="activities")
