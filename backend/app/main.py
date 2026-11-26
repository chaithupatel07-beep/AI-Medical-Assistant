"""FastAPI application entrypoint for AI Medical Assistant."""

from contextlib import asynccontextmanager
import shutil

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import get_settings
from app.core.logging_config import setup_logging
from app.core.safety import GENERAL_DISCLAIMER
from app.database.session import init_db
from app.routes import auth, chat, dashboard, images, library, reports, symptoms, users

logger = setup_logging()
settings = get_settings()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    settings.upload_path.mkdir(parents=True, exist_ok=True)
    (settings.upload_path / "reports").mkdir(parents=True, exist_ok=True)
    (settings.upload_path / "images").mkdir(parents=True, exist_ok=True)
    init_db()
    logger.info("AI Medical Assistant API started (ai_configured=%s)", settings.is_ai_configured)
    yield


app = FastAPI(
    title="AI Medical Assistant API",
    description="Educational AI-powered healthcare support platform API.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def unhandled_exception_handler(_request: Request, exc: Exception):
    logger.exception("Unhandled error: %s", exc)
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected server error occurred. Please try again."},
    )


@app.get("/api/health", tags=["Health"])
def health_check():
    tesseract_ready = bool(settings.tesseract_cmd or shutil.which("tesseract"))
    return {
        "status": "ok",
        "app": settings.app_name,
        "ai_configured": settings.is_ai_configured,
        "ai_provider": settings.ai_provider,
        "chat_model": settings.openai_chat_model,
        "vision_model": settings.openai_vision_model,
        "tesseract_ocr_available": tesseract_ready,
        "disclaimer": GENERAL_DISCLAIMER,
    }


app.include_router(auth.router)
app.include_router(users.router)
app.include_router(chat.router)
app.include_router(symptoms.router)
app.include_router(reports.router)
app.include_router(images.router)
app.include_router(library.router)
app.include_router(dashboard.router)
