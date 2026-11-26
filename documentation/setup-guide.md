# Setup Guide — Local Development

## Prerequisites

- **Node.js** 20+ and **npm**
- **Python** 3.11–3.13
- **Optional**: PostgreSQL 15+ (or Supabase/Neon) and Tesseract OCR binary (`tesseract`)

## 1. Backend Setup

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```

Edit `backend/.env`:
- Set `JWT_SECRET_KEY` to a random 32+ character string.
- Set `OPENAI_API_KEY` (or `GEMINI_API_KEY`).
- Leave `DATABASE_URL=sqlite:///./ai_medical_assistant.db` for local SQLite, or set your PostgreSQL / Supabase connection string.

Start the backend:
```powershell
uvicorn app.main:app --reload --port 8000
```

## 2. Frontend Setup

```powershell
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173` in your browser. Vite automatically proxies `/api/*` requests to `http://127.0.0.1:8000`.

## 3. Running Tests & Checks

```powershell
# Backend
cd backend
python -m compileall app
pytest -q

# Frontend
cd frontend
npm run typecheck
npm run lint
npm run test
npm run build
```
