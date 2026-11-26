"""Automated zero-credential setup script for AI Medical Assistant."""

from __future__ import annotations

import argparse
from pathlib import Path
import secrets
import shutil
import socket
import subprocess
import sys

ROOT_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = ROOT_DIR / "backend"
FRONTEND_DIR = ROOT_DIR / "frontend"


def _venv_python() -> Path:
    if sys.platform == "win32":
        return BACKEND_DIR / ".venv" / "Scripts" / "python.exe"
    return BACKEND_DIR / ".venv" / "bin" / "python"


def _is_port_free(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.5)
        return sock.connect_ex(("127.0.0.1", port)) != 0


def _ensure_directories() -> None:
    for rel in ("uploads", "uploads/reports", "uploads/images", "logs"):
        (BACKEND_DIR / rel).mkdir(parents=True, exist_ok=True)


def _ensure_env_files() -> None:
    backend_env = BACKEND_DIR / ".env"
    if not backend_env.exists():
        secret = secrets.token_hex(32)
        backend_env.write_text(
            "\n".join(
                [
                    "APP_NAME=AI Medical Assistant",
                    "APP_ENV=development",
                    "ENVIRONMENT=development",
                    "PORT=8000",
                    "CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173",
                    f"JWT_SECRET_KEY={secret}",
                    "JWT_ALGORITHM=HS256",
                    "ACCESS_TOKEN_EXPIRE_MINUTES=1440",
                    "DATABASE_URL=sqlite:///./ai_medical_assistant.db",
                    "AI_PROVIDER=openai",
                    "OPENAI_API_KEY=",
                    "GEMINI_API_KEY=",
                    "OLLAMA_BASE_URL=http://127.0.0.1:11434",
                    "UPLOAD_DIR=./uploads",
                    "MAX_UPLOAD_SIZE_MB=10",
                    "RATE_LIMIT_PER_MINUTE=120",
                    "",
                ]
            ),
            encoding="utf-8",
        )
        print("[setup] Created local backend/.env with auto-generated JWT secret and SQLite default.")

    frontend_env = FRONTEND_DIR / ".env"
    if not frontend_env.exists():
        frontend_env.write_text("VITE_API_BASE_URL=\n", encoding="utf-8")
        print("[setup] Created local frontend/.env (uses Vite /api proxy cleanly).")


def _run(cmd: list[str], cwd: Path) -> None:
    print(f"[setup] Running: {' '.join(cmd)} (in {cwd.name})")
    subprocess.run(cmd, cwd=str(cwd), check=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Setup AI Medical Assistant locally.")
    parser.add_argument(
        "--check",
        action="store_true",
        help="Verify environment, initialize directories/SQLite DB, and skip package installation.",
    )
    args = parser.parse_args()

    if sys.version_info < (3, 10):
        print("[error] Python 3.10+ is required.")
        return 1

    npm_cmd = shutil.which("npm.cmd" if sys.platform == "win32" else "npm")
    if not npm_cmd:
        print("[error] Node.js / npm was not found on PATH. Install Node 18+ first.")
        return 1

    _ensure_directories()
    _ensure_env_files()

    venv_py = _venv_python()
    if not args.check:
        if not venv_py.exists():
            _run([sys.executable, "-m", "venv", str(BACKEND_DIR / ".venv")], cwd=BACKEND_DIR)
        _run([str(venv_py), "-m", "pip", "install", "--upgrade", "pip"], cwd=BACKEND_DIR)
        _run([str(venv_py), "-m", "pip", "install", "-r", "requirements.txt"], cwd=BACKEND_DIR)
        _run([npm_cmd, "install"], cwd=FRONTEND_DIR)

    py_for_db = str(venv_py if venv_py.exists() else Path(sys.executable))
    _run([py_for_db, "-c", "from app.database.session import init_db; init_db(); print('Database initialized.')"], cwd=BACKEND_DIR)

    ollama_ready = shutil.which("ollama") is not None
    tesseract_ready = shutil.which("tesseract") is not None
    print("\n--- Environment Check ---")
    print(f"Python:     {sys.version.split()[0]}")
    print(f"npm:        {npm_cmd}")
    print(f"Ollama CLI: {'Detected (optional local LLM supported)' if ollama_ready else 'Not detected (built-in offline engine active)'}")
    print(f"Tesseract:  {'Detected (local OCR enabled)' if tesseract_ready else 'Not detected (text PDFs work; scanned image OCR optional)'}")
    print(f"Port 8000:  {'Free' if _is_port_free(8000) else 'In use'}")
    print(f"Port 5173:  {'Free' if _is_port_free(5173) else 'In use'}")
    print("\nSetup complete! Start the app anytime with:\n  python scripts/start.py\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
