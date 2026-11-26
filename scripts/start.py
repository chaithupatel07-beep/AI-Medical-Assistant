"""Cross-platform launcher starting FastAPI backend (:8000) and Vite frontend (:5173)."""

from __future__ import annotations

from pathlib import Path
import shutil
import signal
import subprocess
import sys
import time

ROOT_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = ROOT_DIR / "backend"
FRONTEND_DIR = ROOT_DIR / "frontend"


def _venv_uvicorn() -> Path:
    if sys.platform == "win32":
        return BACKEND_DIR / ".venv" / "Scripts" / "uvicorn.exe"
    return BACKEND_DIR / ".venv" / "bin" / "uvicorn"


def main() -> int:
    npm_cmd = shutil.which("npm.cmd" if sys.platform == "win32" else "npm")
    if not npm_cmd:
        print("[error] npm not found on PATH.")
        return 1

    # Ensure database & directories exist before startup
    subprocess.run([sys.executable, str(ROOT_DIR / "scripts" / "setup.py"), "--check"], check=True)

    uvicorn_bin = _venv_uvicorn()
    backend_cmd = (
        [str(uvicorn_bin), "app.main:app", "--host", "127.0.0.1", "--port", "8000", "--reload"]
        if uvicorn_bin.exists()
        else [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000", "--reload"]
    )
    frontend_cmd = [npm_cmd, "run", "dev", "--", "--host", "127.0.0.1", "--port", "5173"]

    print("[start] Starting FastAPI backend on http://localhost:8000 ...")
    backend_proc = subprocess.Popen(backend_cmd, cwd=str(BACKEND_DIR))
    print("[start] Starting Vite frontend on http://localhost:5173 ...")
    frontend_proc = subprocess.Popen(frontend_cmd, cwd=str(FRONTEND_DIR))

    print("\nAI Medical Assistant is running:")
    print("  Frontend UI : http://localhost:5173")
    print("  Backend API : http://localhost:8000")
    print("  Swagger Docs: http://localhost:8000/docs")
    print("Press Ctrl+C to stop both services.\n")

    def shutdown(*_args):
        for proc in (frontend_proc, backend_proc):
            if proc.poll() is None:
                proc.terminate()
        raise SystemExit(0)

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    try:
        while True:
            if backend_proc.poll() is not None or frontend_proc.poll() is not None:
                break
            time.sleep(0.5)
    except KeyboardInterrupt:
        pass
    finally:
        for proc in (frontend_proc, backend_proc):
            if proc.poll() is None:
                proc.terminate()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
