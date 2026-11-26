"""FastAPI application entrypoint for AI Medical Assistant."""

from contextlib import asynccontextmanager
from pathlib import Path
import shutil

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.core.config import get_settings
from app.core.logging_config import setup_logging
from app.core.rate_limit import RateLimitMiddleware
from app.core.safety import GENERAL_DISCLAIMER
from app.database.session import init_db
from app.routes import auth, chat, dashboard, images, library, reports, symptoms, users, v1_compat

logger = setup_logging()
settings = get_settings()


def _bootstrap_runtime() -> None:
    settings.upload_path.mkdir(parents=True, exist_ok=True)
    (settings.upload_path / "reports").mkdir(parents=True, exist_ok=True)
    (settings.upload_path / "images").mkdir(parents=True, exist_ok=True)
    init_db()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    _bootstrap_runtime()
    logger.info("AI Medical Assistant API started (ai_configured=%s)", settings.is_ai_configured)
    yield


_bootstrap_runtime()


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
app.add_middleware(RateLimitMiddleware, requests_per_minute=settings.rate_limit_per_minute)


@app.exception_handler(Exception)
async def unhandled_exception_handler(_request: Request, exc: Exception):
    logger.exception("Unhandled error: %s", exc)
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected server error occurred. Please try again."},
    )


@app.get("/health", tags=["Health"])
@app.get("/api/health", tags=["Health"])
async def health_check():
    from app.ai.local_engine import detect_ollama_model

    tesseract_ready = bool(settings.tesseract_cmd or shutil.which("tesseract"))
    dist_path = settings.frontend_dist_path
    ollama_model = None
    if not settings.is_ai_configured:
        ollama_model = await detect_ollama_model(settings.ollama_model or None)

    if settings.is_ai_configured:
        ai_mode = "cloud_ai"
        ai_provider = settings.effective_provider
        chat_model = settings.effective_chat_model
        vision_model = settings.effective_vision_model
    elif ollama_model:
        ai_mode = "ollama_local"
        ai_provider = "ollama"
        chat_model = ollama_model
        vision_model = ollama_model
    else:
        ai_mode = "built_in_offline"
        ai_provider = "local-engine"
        chat_model = "built-in-educational-engine"
        vision_model = "local-pillow-inspector"

    return {
        "status": "ok",
        "app": settings.app_name,
        "ai_configured": settings.is_ai_configured,
        "ai_ready": True,
        "ai_mode": ai_mode,
        "ollama_model": ollama_model,
        "ai_provider": ai_provider,
        "chat_model": chat_model,
        "vision_model": vision_model,
        "tesseract_ocr_available": tesseract_ready,
        "frontend_served": dist_path is not None,
        "database_mode": "ephemeral_sqlite" if settings.is_ephemeral_serverless_db else "persistent",
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
app.include_router(v1_compat.router)


@app.get("/", include_in_schema=False)
def root_status():
    dist = settings.frontend_dist_path
    if dist is not None:
        return FileResponse(str(dist / "index.html"))
    return {
        "app": settings.app_name,
        "status": "ok",
        "docs": "/docs",
        "health": "/api/health",
    }


_frontend_dist = settings.frontend_dist_path
if _frontend_dist is not None:
    _assets_dir = _frontend_dist / "assets"
    if _assets_dir.is_dir():
        app.mount("/assets", StaticFiles(directory=str(_assets_dir)), name="frontend-assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    def serve_spa(full_path: str):
        if full_path == "api" or full_path.startswith("api/"):
            raise HTTPException(status_code=404, detail="API endpoint not found.")
        candidate = (_frontend_dist / full_path).resolve()
        if (
            full_path
            and _frontend_dist.resolve() in candidate.parents
            and candidate.is_file()
        ):
            return FileResponse(str(candidate))
        return FileResponse(str(_frontend_dist / "index.html"))
