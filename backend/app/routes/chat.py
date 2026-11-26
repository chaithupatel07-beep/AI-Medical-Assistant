"""AI Medical Chatbot routes: sessions, messages, clear conversation, suggested questions."""

from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.safety import EMERGENCY_GUIDANCE, GENERAL_DISCLAIMER, detect_emergency_signals
from app.core.security import get_current_user
from app.database.session import get_db
from app.models.entities import ChatMessage, ChatSession, User
from app.schemas.medical import (
    ChatMessageCreate,
    ChatMessageResponse,
    ChatSessionCreate,
    ChatSessionDetailResponse,
    ChatSessionResponse,
    ChatTurnResponse,
)
from app.services.ai_service import generate_chat_reply
from app.utils.activity import log_activity

router = APIRouter(prefix="/api/chat", tags=["AI Medical Chatbot"])

SUGGESTED_QUESTIONS: List[str] = [
    "What does Hemoglobin A1c (HbA1c) measure in simple terms?",
    "How can I prepare questions before my next doctor visit?",
    "What is the difference between systolic and diastolic blood pressure?",
    "When should a fever or cough be evaluated by a doctor?",
    "What are warning signs of dehydration to watch for?",
    "How do LDL, HDL, and triglycerides differ in a lipid panel?",
]


def _serialize_session(session: ChatSession) -> ChatSessionResponse:
    messages = session.messages or []
    preview = messages[-1].content[:120] if messages else None
    return ChatSessionResponse(
        id=session.id,
        title=session.title,
        created_at=session.created_at,
        updated_at=session.updated_at,
        message_count=len(messages),
        last_message_preview=preview,
    )


def _serialize_message(msg: ChatMessage) -> ChatMessageResponse:
    return ChatMessageResponse(
        id=msg.id,
        session_id=msg.session_id,
        role=msg.role,
        content=msg.content,
        emergency_flagged=msg.emergency_flagged,
        created_at=msg.created_at,
    )


def _get_owned_session(db: Session, session_id: str, user_id: str) -> ChatSession:
    session = (
        db.query(ChatSession)
        .filter(ChatSession.id == session_id, ChatSession.user_id == user_id)
        .first()
    )
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat session not found.")
    return session


@router.get("/suggested-questions")
def get_suggested_questions():
    return {"questions": SUGGESTED_QUESTIONS}


@router.get("/sessions", response_model=List[ChatSessionResponse])
def list_sessions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    sessions = (
        db.query(ChatSession)
        .filter(ChatSession.user_id == current_user.id)
        .order_by(ChatSession.updated_at.desc())
        .all()
    )
    return [_serialize_session(s) for s in sessions]


@router.post("/sessions", response_model=ChatSessionResponse, status_code=status.HTTP_201_CREATED)
def create_session(
    payload: ChatSessionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    title = (payload.title or "New Health Conversation").strip()[:200] or "New Health Conversation"
    session = ChatSession(user_id=current_user.id, title=title)
    db.add(session)
    db.flush()

    log_activity(
        db,
        user_id=current_user.id,
        activity_type="chat_session_created",
        description=f"Started AI conversation '{title}'.",
        resource_type="chat_session",
        resource_id=session.id,
    )
    db.commit()
    db.refresh(session)
    return _serialize_session(session)


@router.get("/sessions/{session_id}", response_model=ChatSessionDetailResponse)
def get_session_detail(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    session = _get_owned_session(db, session_id, current_user.id)
    base = _serialize_session(session)
    return ChatSessionDetailResponse(
        **base.model_dump(),
        messages=[_serialize_message(m) for m in session.messages],
    )


@router.post("/sessions/{session_id}/messages", response_model=ChatTurnResponse)
async def send_message(
    session_id: str,
    payload: ChatMessageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    session = _get_owned_session(db, session_id, current_user.id)
    content = payload.content.strip()
    if not content:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Message cannot be empty.")

    emergency_detected, emergency_reasons = detect_emergency_signals(content)
    history = [{"role": m.role, "content": m.content} for m in session.messages if m.role in ("user", "assistant")]

    reply_text, model_used = await generate_chat_reply(
        history=history,
        user_message=content,
        emergency_detected=emergency_detected,
    )

    if session.title == "New Health Conversation" and len(session.messages) == 0:
        session.title = (content[:60] + ("..." if len(content) > 60 else "")).strip()

    user_msg = ChatMessage(
        session_id=session.id,
        user_id=current_user.id,
        role="user",
        content=content,
        emergency_flagged=emergency_detected,
    )
    assistant_msg = ChatMessage(
        session_id=session.id,
        user_id=current_user.id,
        role="assistant",
        content=reply_text,
        emergency_flagged=emergency_detected,
    )
    session.updated_at = datetime.now(timezone.utc)
    db.add(user_msg)
    db.add(assistant_msg)

    log_activity(
        db,
        user_id=current_user.id,
        activity_type="chat_message",
        description=f"Asked AI Medical Assistant in '{session.title}'.",
        resource_type="chat_session",
        resource_id=session.id,
        metadata={"emergency_detected": emergency_detected, "ai_model": model_used},
    )
    db.commit()
    db.refresh(session)
    db.refresh(user_msg)
    db.refresh(assistant_msg)

    return ChatTurnResponse(
        session=_serialize_session(session),
        user_message=_serialize_message(user_msg),
        assistant_message=_serialize_message(assistant_msg),
        emergency_detected=emergency_detected,
        emergency_reasons=emergency_reasons,
        emergency_banner=EMERGENCY_GUIDANCE if emergency_detected else None,
        ai_model=model_used,
        disclaimer=GENERAL_DISCLAIMER,
    )


@router.post("/sessions/{session_id}/clear", response_model=ChatSessionDetailResponse)
def clear_session_messages(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    session = _get_owned_session(db, session_id, current_user.id)
    db.query(ChatMessage).filter(
        ChatMessage.session_id == session.id,
        ChatMessage.user_id == current_user.id,
    ).delete()
    session.title = "New Health Conversation"
    session.updated_at = datetime.now(timezone.utc)

    log_activity(
        db,
        user_id=current_user.id,
        activity_type="chat_cleared",
        description="Cleared messages in an AI chat conversation.",
        resource_type="chat_session",
        resource_id=session.id,
    )
    db.commit()
    db.refresh(session)
    base = _serialize_session(session)
    return ChatSessionDetailResponse(**base.model_dump(), messages=[])


@router.delete("/sessions/{session_id}")
def delete_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    session = _get_owned_session(db, session_id, current_user.id)
    title = session.title
    db.delete(session)
    log_activity(
        db,
        user_id=current_user.id,
        activity_type="record_deleted",
        description=f"Deleted AI conversation '{title}'.",
        resource_type="chat_session",
        resource_id=session_id,
    )
    db.commit()
    return {"message": "Conversation deleted successfully."}
