"""Application configuration loaded from backend/.env or environment variables."""

from functools import lru_cache
from pathlib import Path
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    """Server configuration settings. AI API keys remain strictly server-side."""

    app_name: str = "AI Medical Assistant"
    app_env: str = "development"
    port: int = 8000
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    jwt_secret_key: str = "dev-local-secret-change-in-production-9f8e7d6c5b4a3210"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440

    database_url: str = f"sqlite:///{(BASE_DIR / 'ai_medical_assistant.db').as_posix()}"

    ai_provider: str = "openai"
    openai_api_key: str = ""
    openai_base_url: str = "https://api.openai.com/v1"
    openai_chat_model: str = "gpt-4o-mini"
    openai_vision_model: str = "gpt-4o-mini"

    tesseract_cmd: str = ""
    max_upload_size_mb: int = 10
    upload_dir: str = str(BASE_DIR / "uploads")
    frontend_dist_dir: str = ""

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def normalized_database_url(self) -> str:
        url = (self.database_url or "").strip()
        if url.startswith("postgres://"):
            return "postgresql+psycopg://" + url[len("postgres://"):]
        if url.startswith("postgresql://") and "+psycopg" not in url:
            return "postgresql+psycopg://" + url[len("postgresql://"):]
        return url

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

    @property
    def is_ai_configured(self) -> bool:
        key = (self.openai_api_key or "").strip()
        return bool(key) and not key.startswith("your_")

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
