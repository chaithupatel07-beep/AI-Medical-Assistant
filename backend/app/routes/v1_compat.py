"""Versioned /api/v1 endpoints delegating cleanly to the core route modules."""

from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.security import decode_access_token, get_current_user
from app.database.session import get_db
from app.models.entities import ChatSession, User
from app.routes import auth, chat, dashboard, images, library, reports, symptoms
from app.schemas.medical import LanguageCode

router = APIRouter(prefix="/api/v1", tags=["API v1"])


class V1ChatRequest(BaseModel):
    session_id: Optional[str] = None
    message: str = Field(..., min_length=1, max_length=4000)
    language: LanguageCode = "en"


class VerifyTokenRequest(BaseModel):
    token: str = Field(..., min_length=10)


@router.get("/health")
async def v1_health():
    from app.main import health_check

    return await health_check()


@router.post("/auth/register", response_model=auth.AuthResponse, status_code=status.HTTP_201_CREATED)
def v1_auth_register(payload: auth.RegisterRequest, db: Session = Depends(get_db)):
    return auth.register(payload=payload, db=db)


@router.post("/auth/login", response_model=auth.AuthResponse)
def v1_auth_login(payload: auth.LoginRequest, db: Session = Depends(get_db)):
    return auth.login(payload=payload, db=db)


@router.post("/auth/logout")
def v1_auth_logout(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return auth.logout(current_user=current_user, db=db)


@router.get("/auth/me")
def v1_auth_me(current_user: User = Depends(get_current_user)):
    return auth.serialize_user(current_user)


@router.post("/auth/verify")
def v1_auth_verify(payload: VerifyTokenRequest, db: Session = Depends(get_db)):
    claims = decode_access_token(payload.token)
    user_id = claims.get("sub")
    user = db.query(User).filter(User.id == user_id).first() if user_id else None
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token user.")
    return {"valid": True, "user": auth.serialize_user(user)}


@router.post("/chat")
async def v1_chat(
    payload: V1ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    session_id = payload.session_id
    if not session_id:
        session = ChatSession(user_id=current_user.id, title="New Health Conversation")
        db.add(session)
        db.commit()
        db.refresh(session)
        session_id = session.id
    return await chat.send_message(
        session_id=session_id,
        payload=chat.ChatMessageCreate(content=payload.message, language=payload.language),
        current_user=current_user,
        db=db,
    )


@router.get("/chat/sessions")
def v1_list_chat_sessions(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return chat.list_sessions(current_user=current_user, db=db)


@router.get("/chat/sessions/{session_id}")
def v1_get_chat_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return chat.get_session_detail(session_id=session_id, current_user=current_user, db=db)


@router.delete("/chat/sessions/{session_id}")
def v1_delete_chat_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return chat.delete_session(session_id=session_id, current_user=current_user, db=db)


@router.post("/symptoms/analyze")
async def v1_analyze_symptoms(
    payload: symptoms.SymptomCheckRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return await symptoms.check_symptoms(payload=payload, current_user=current_user, db=db)


@router.post("/reports/upload", status_code=status.HTTP_201_CREATED)
async def v1_upload_report(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return await reports.upload_medical_report(file=file, current_user=current_user, db=db)


@router.get("/reports")
def v1_list_reports(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return reports.list_reports(current_user=current_user, db=db)


@router.get("/reports/{report_id}")
def v1_get_report(
    report_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return reports.get_report(report_id=report_id, current_user=current_user, db=db)


@router.post("/reports/{report_id}/summarize")
async def v1_summarize_report(
    report_id: str,
    lang: str = Query("en"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return await reports.summarize_medical_report(
        report_id=report_id, lang=lang, current_user=current_user, db=db
    )


@router.delete("/reports/{report_id}")
def v1_delete_report(
    report_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return reports.delete_report(report_id=report_id, current_user=current_user, db=db)


@router.post("/images/analyze")
async def v1_analyze_image(
    file: UploadFile = File(...),
    image_context: Optional[str] = Form(None),
    lang: str = Query("en"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    uploaded = await images.upload_medical_image(
        file=file, image_context=image_context, current_user=current_user, db=db
    )
    return await images.analyze_medical_image(
        image_id=uploaded.id, lang=lang, current_user=current_user, db=db
    )


@router.get("/dashboard")
async def v1_dashboard(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return await dashboard.get_dashboard_overview(current_user=current_user, db=db)


@router.get("/health/articles")
def v1_library_articles(
    category: Optional[str] = Query(None),
    q: Optional[str] = Query(None),
    lang: str = Query("en"),
):
    return library.list_articles(category=category, q=q, lang=lang)


@router.get("/health/articles/{article_id}")
def v1_library_article_detail(article_id: str, lang: str = Query("en")):
    return library.get_article(article_id=article_id, lang=lang)
