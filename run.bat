@echo off
setlocal
cd /d "%~dp0"

if not exist "backend\.venv\Scripts\python.exe" (
    echo [AI Medical Assistant] Running initial automated setup...
    python scripts\setup.py
    if errorlevel 1 exit /b 1
)

if not exist "frontend\node_modules" (
    echo [AI Medical Assistant] Installing missing frontend packages...
    python scripts\setup.py
    if errorlevel 1 exit /b 1
)

python scripts\start.py
