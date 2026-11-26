# AI Medical Assistant — Your Intelligent Healthcare Companion

A complete full-stack, educational AI-powered healthcare support web application built with **React + TypeScript + Vite + Tailwind CSS + Shadcn UI + TanStack Query + React Hook Form + Zod** on the frontend and **Python FastAPI + SQLAlchemy + PyMuPDF + Tesseract OCR + PostgreSQL/Supabase (with SQLite local fallback)** on the backend. Supports **English, Telugu (`తెలుగు`), and Hindi (`हिन्दी`)** across the UI, Health Library, and AI responses.

> **Important Medical Safety Disclaimer:** AI Medical Assistant is strictly an educational healthcare support platform. It does **not** diagnose conditions, prescribe medications, or replace care from a licensed healthcare professional. In an emergency, call your local emergency services immediately.

---

## Problem Statement & Objectives

Medical reports, lab abbreviations, and clinical terminology are often difficult for patients and students to interpret before a doctor visit. This platform aims to:
1. Translate lab reports and medical terms into clear, non-diagnostic plain language in English, Telugu, or Hindi.
2. Provide structured educational symptom preparation without making diagnoses or prescriptions.
3. Preserve strict user privacy, report-supplied reference ranges, and emergency warning detection.

---

## Core Features

1. **Public Landing Page & Medical Safety Center** — Hero overview, feature cards, workflow walkthrough, benefits, and safety disclaimers.
2. **Secure Authentication & User Isolation** — Registration with password complexity rules, JWT Bearer authentication, login, logout, forgot/reset password flow, profile management, and strict user-level ownership on every record and file endpoint.
3. **Personalized Main Dashboard** — Live database statistics (uploaded reports, AI summaries, conversations, symptom checks, medical images), recent reports, recent conversations, health library shortcuts, and AI configuration status.
4. **AI Medical Chatbot** — Real-time Markdown responses, persistent conversation history, new/clear/delete session controls, suggested questions, and automatic emergency warning detection.
5. **Symptom Information Checker** — Structured form (age, optional gender, main symptom, duration, severity, additional symptoms, relevant context) returning educational possibilities, next steps, warning signs, and questions for your doctor.
6. **Medical Report Summarizer (PDF, JPG, JPEG, PNG)** — Drag-and-drop upload with magic-byte validation, progress indicator, authenticated Blob file preview, `pypdf` text extraction, `pytesseract` / Vision OCR fallback, deterministic lab marker parsing without inventing reference ranges, AI plain-language summary, and Markdown summary download.
7. **Medical Image Analysis** — Secure JPG/PNG upload, authenticated preview, Vision AI observations, explicit limitations & uncertainty notice, and recommendation for professional medical review.
8. **Health Information Library** — Searchable across all 6 categories (*General Health*, *Nutrition*, *Fitness and Exercise*, *Preventive Healthcare*, *Common Health Conditions*, *Mental Wellness*) with links to **MedlinePlus**, **WHO**, and **CDC**.
9. **Personal Health Dashboard** — Manage reports, AI summaries, chat history, uploaded images, activity history, personal health profile, and password security with full delete controls.

---

## Project Structure

```text
AI-MEDICAL ASSISTANT/
├── frontend/
│   ├── src/
│   │   ├── assets/             # Custom SVG illustrations
│   │   ├── components/         # Reusable & Shadcn UI components
│   │   ├── hooks/              # Auth context & authenticated Blob preview hook
│   │   ├── layouts/            # PublicLayout & DashboardLayout
│   │   ├── pages/              # Landing, Auth, Dashboard, Chat, Symptoms, Reports, Images, Library, Personal Health
│   │   ├── services/           # Typed REST API client & XHR upload progress helper
│   │   ├── types/              # TypeScript API interfaces
│   │   └── utils/              # Class merging, formatting, password/email validation
│   ├── package.json
│   └── vite.config.ts
├── backend/
│   ├── app/
│   │   ├── core/               # Settings, JWT/bcrypt security, safety guardrails, logging
│   │   ├── database/           # SQLAlchemy engine & session setup
│   │   ├── models/             # 8 relational ORM models
│   │   ├── routes/             # Auth, Users, Chat, Symptoms, Reports, Images, Library, Dashboard
│   │   ├── schemas/            # Pydantic v2 schemas
│   │   ├── services/           # Server-side AI service, OCR service, report parser, library catalog
│   │   └── utils/              # Secure file validation & user activity logging
│   ├── tests/                  # Pytest API integration tests
│   ├── .env.example
│   └── requirements.txt
├── database/
│   └── schema.sql              # PostgreSQL / Supabase DDL schema (8 tables)
├── docs/
│   └── API.md                  # REST API documentation
└── .env.example
```

---

## Setup & Running Locally (Zero API Keys Required!)

AI Medical Assistant works **out of the box with zero external API keys, paid accounts, or Docker**:
- **Database**: Local SQLite (`backend/ai_medical_assistant.db`) created automatically on startup.
- **AI Modes (automatic fallback chain)**:
  1. **Cloud AI (Optional)** — Used if `OPENAI_API_KEY` or `GEMINI_API_KEY` is configured in `backend/.env`.
  2. **Local Ollama AI (Optional)** — Auto-detected at `http://127.0.0.1:11434` if you install [Ollama](https://ollama.com) and run e.g. `ollama pull llama3.2`.
  3. **Built-in Offline Educational Engine (Default)** — Always active with zero setup: medical chatbot knowledge base, rules-based symptom preparation, PyMuPDF + deterministic lab marker parser, and local Pillow medical image inspector.

### Quick 1-Command Setup & Launch

- **Windows**: Double-click **`run.bat`** (or run `python scripts/setup.py` then `python scripts/start.py`)
- **macOS / Linux**:
  ```bash
  python3 scripts/setup.py
  python3 scripts/start.py
  ```

### Manual Setup (Alternative)

1. **Backend (`backend/`)**:
```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```
Interactive Swagger docs: `http://localhost:8000/docs`

2. **Frontend (`frontend/`)**:
```powershell
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173` in your browser. Vite proxies `/api/*` requests directly to `http://127.0.0.1:8000`.

### Run Verification Checks

```powershell
# Backend integration tests
cd backend
.venv\Scripts\pytest.exe -v

# Frontend TypeScript check & production build
cd frontend
npm run build
```

---

## Full-Stack Deployment (Frontend + Backend + PostgreSQL + OCR)

This repository is configured so **every part of the application deploys together** (React SPA + FastAPI API + PostgreSQL + Tesseract OCR + AI integration):

### Option A: Single-Project Full-Stack Deploy on Vercel (`vercel.json` Services)

When importing this repository on **Vercel**:
1. Keep **Root Directory** at `./` (repository root) and **Application Preset** as **Services**.
2. Vercel reads the root `vercel.json` (`services.frontend` + `services.backend` + `rewrites`) and deploys **both** the React Vite frontend (`/`) and the FastAPI backend (`/api/*`) together as a single unified project.
3. Add **Environment Variables** in Vercel:
   - `DATABASE_URL` = your Supabase or Neon PostgreSQL connection string (recommended for persistent storage; otherwise falls back to ephemeral `/tmp` SQLite)
   - `JWT_SECRET_KEY` = a strong random 32+ char secret
   - `AI_PROVIDER` = `gemini` (or `openai`)
   - `OPENAI_API_KEY` = your API key
   - `OPENAI_BASE_URL` = `https://generativelanguage.googleapis.com/v1beta/openai/` (if using Gemini)
   - `OPENAI_CHAT_MODEL` = `gemini-2.5-flash` (or `gpt-4o-mini`)
   - `OPENAI_VISION_MODEL` = `gemini-2.5-flash` (or `gpt-4o-mini`)

### Option B: Single-Platform Full-Stack Deploy (Render Blueprint / Railway / Docker)

- **Render (`render.yaml`)**: Connect this GitHub repo as a **Render Blueprint**. It automatically provisions both:
  1. `ai-medical-assistant-db` (PostgreSQL)
  2. `ai-medical-assistant` (Multi-stage Docker web service building `frontend/dist` and serving it alongside `/api/*` via FastAPI + Uvicorn + Tesseract OCR)
  - Set `OPENAI_API_KEY` (and `OPENAI_BASE_URL` / `OPENAI_CHAT_MODEL` / `OPENAI_VISION_MODEL` if using Gemini) in the Render dashboard environment variables.
- **Railway (`railway.toml` + `Dockerfile`)**: Deploy directly from GitHub + add a Railway PostgreSQL plugin and set `DATABASE_URL` and `OPENAI_API_KEY`.
- **Docker Compose (`docker-compose.yml`)**:
  ```bash
  OPENAI_API_KEY=your_key JWT_SECRET_KEY=your_32_char_secret docker compose up --build -d
  ```
  Runs PostgreSQL 16 (initialized with `database/schema.sql`), persistent `uploads_data`, and the unified FastAPI + React production server at `http://localhost:8000`.

### Option B: Split Deployment (Vercel Frontend + Render/Railway Backend + Supabase PostgreSQL)

1. **Database**: Run `database/schema.sql` in Supabase/PostgreSQL and copy the connection string into `DATABASE_URL`.
2. **Backend**: Deploy `backend/` to Render/Railway with `DATABASE_URL`, `JWT_SECRET_KEY`, `OPENAI_API_KEY`, and `CORS_ORIGINS=https://your-frontend.vercel.app`.
3. **Frontend (`frontend/`)**: Deploy to Vercel (using `frontend/vercel.json` for SPA routing) with `VITE_API_BASE_URL=https://your-backend-url.onrender.com`.

---

## Documentation

- [Architecture](documentation/architecture.md)
- [Setup Guide](documentation/setup-guide.md)
- [API Documentation](documentation/api-documentation.md)
- [Deployment Guide](documentation/deployment-guide.md)
- [Testing Report](documentation/testing-report.md)
- [Deployment Checklist](DEPLOYMENT_CHECKLIST.md)

## Known Limitations & Future Enhancements

- **Limitations**: Educational support only; not a certified medical device or clinical diagnostic tool. Scanned PDFs/images require either local Tesseract OCR or a configured Vision AI key. Ephemeral `/tmp` SQLite on serverless platforms resets unless PostgreSQL (`DATABASE_URL` / `POSTGRES_URL`) is connected.
- **Future Enhancements**: Multi-page scanned PDF OCR batching, clinician-shareable temporary report links, and longitudinal lab marker trend charts.
