"""Application configuration loaded from backend/.env or environment variables."""

from functools import lru_cache
import os
from pathlib import Path
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[2]
IS_VERCEL = bool(os.environ.get("VERCEL"))
DEFAULT_WRITABLE_DIR = Path("/tmp/ai_medical_assistant") if IS_VERCEL else BASE_DIR


class Settings(BaseSettings):
    """Server configuration settings. AI API keys remain strictly server-side."""

    app_name: str = "AI Medical Assistant"
    app_env: str = "production" if IS_VERCEL else "development"
    port: int = 8000
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    jwt_secret_key: str = "dev-local-secret-change-in-production-9f8e7d6c5b4a3210"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440

    database_url: str = f"sqlite:///{(DEFAULT_WRITABLE_DIR / 'ai_medical_assistant.db').as_posix()}"
    postgres_url: str = ""
    postgres_prisma_url: str = ""
    neon_database_url: str = ""

    ai_provider: str = "openai"
    openai_api_key: str = ""
    gemini_api_key: str = ""
    openai_base_url: str = "https://api.openai.com/v1"
    openai_chat_model: str = "gpt-4o-mini"
    openai_vision_model: str = "gpt-4o-mini"

    tesseract_cmd: str = ""
    max_upload_size_mb: int = 10
    upload_dir: str = str(DEFAULT_WRITABLE_DIR / "uploads")
    frontend_dist_dir: str = ""

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def normalized_database_url(self) -> str:
        raw_db = (self.database_url or "").strip()
        fallback_pg = (
            (self.postgres_url or "").strip()
            or (self.neon_database_url or "").strip()
            or (self.postgres_prisma_url or "").strip()
        )
        url = fallback_pg if (fallback_pg and (not raw_db or raw_db.startswith("sqlite"))) else raw_db
        if url.startswith("postgres://"):
            return "postgresql+psycopg://" + url[len("postgres://"):]
        if url.startswith("postgresql://") and "+psycopg" not in url:
            return "postgresql+psycopg://" + url[len("postgresql://"):]
        return url

    @property
    def is_ephemeral_serverless_db(self) -> bool:
        return IS_VERCEL and self.normalized_database_url.startswith("sqlite")

    @property
    def cors_origin_list(self) -> List[str]:
        return [
            origin.strip().rstrip("/")
            for origin in self.cors_origins.split(",")
            if origin.strip()
        ]

    @property
    def max_upload_size_bytes(self) -> int:
        return self.max_upload_size_mb * 1024 * 1024

    @staticmethod
    def _clean_key(raw: str) -> str:
        cleaned = (raw or "").strip().strip('"').strip("'").strip()
        if not cleaned or cleaned.startswith("your_"):
            return ""
        return cleaned

    @property
    def effective_api_key(self) -> str:
        return self._clean_key(self.openai_api_key) or self._clean_key(self.gemini_api_key)

    @property
    def _uses_gemini_key(self) -> bool:
        key = self.effective_api_key
        if not key:
            return self.ai_provider.lower() == "gemini"
        if self._clean_key(self.gemini_api_key) and not self._clean_key(self.openai_api_key):
            return True
        if key.startswith(("AIza", "AQ.")):
            return True
        return (
            self.ai_provider.lower() == "gemini"
            or "generativelanguage.googleapis.com" in self.openai_base_url
        )

    @property
    def effective_provider(self) -> str:
        if self._uses_gemini_key:
            return "gemini"
        return self.ai_provider

    @property
    def effective_base_url(self) -> str:
        base = (self.openai_base_url or "").strip()
        if self._uses_gemini_key and (not base or base == "https://api.openai.com/v1"):
            return "https://generativelanguage.googleapis.com/v1beta/openai/"
        return base or "https://api.openai.com/v1"

    @property
    def effective_chat_model(self) -> str:
        model = (self.openai_chat_model or "").strip()
        if self._uses_gemini_key and (not model or model == "gpt-4o-mini"):
            return "gemini-2.5-flash"
        return model or "gpt-4o-mini"

    @property
    def effective_vision_model(self) -> str:
        model = (self.openai_vision_model or "").strip()
        if self._uses_gemini_key and (not model or model == "gpt-4o-mini"):
            return "gemini-2.5-flash"
        return model or "gpt-4o-mini"

    @property
    def is_ai_configured(self) -> bool:
        return bool(self.effective_api_key)

    @property
    def upload_path(self) -> Path:
        path = Path(self.upload_dir)
        if not path.is_absolute():
            path = (BASE_DIR / path).resolve()
        return path

    @property
    def frontend_dist_path(self) -> Path | None:
        candidates = []
        if self.frontend_dist_dir.strip():
            candidates.append(Path(self.frontend_dist_dir.strip()))
        candidates.extend([BASE_DIR / "static_frontend", BASE_DIR.parent / "frontend" / "dist"])
        for candidate in candidates:
            resolved = candidate if candidate.is_absolute() else (BASE_DIR / candidate).resolve()
            if (resolved / "index.html").is_file():
                return resolved
        return None


@lru_cache
def get_settings() -> Settings:
    return Settings()
