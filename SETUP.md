# Setup Guide — AI Medical Assistant

AI Medical Assistant runs out of the box with **zero external API keys** (using SQLite + local Ollama or the built-in offline engine), and upgrades seamlessly when you add **Google Gemini** (`gemini-2.5-flash`) or **Supabase** free-tier credentials.

---

## Option 1: Fastest Zero-Key Local Start (Offline / Local Ollama)

1. **Automated Setup (Windows / macOS / Linux)**:
   ```bash
   python scripts/setup.py
   python scripts/start.py
   ```
   *(On Windows you can also double-click `run.bat`.)*
2. Open **`http://localhost:5173`** (Frontend) and **`http://localhost:8000/docs`** (FastAPI Swagger).
3. *(Optional free local LLM)* Install [Ollama](https://ollama.com/download) and run:
   ```bash
   ollama pull llama3.2
   ```
   The backend automatically detects Ollama on `http://127.0.0.1:11434`.

---

## Option 2: Enable Live Multimodal AI with Google Gemini (Free Tier)

1. Visit **Google AI Studio**: <https://aistudio.google.com/apikey> and create an API key.
2. Add it to `backend/.env` (or your Vercel/Render Environment Variables):
   ```env
   GEMINI_API_KEY=your_google_gemini_api_key_here
   AI_PROVIDER=gemini
   OPENAI_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/
   OPENAI_CHAT_MODEL=gemini-2.5-flash
   OPENAI_VISION_MODEL=gemini-2.5-flash
   ```
3. Restart the backend. All AI chat, symptom guidance, PDF/image medical report reading, and medical image observations will now use **Gemini 2.5 Flash**.

---

## Option 3: Connect Supabase PostgreSQL, Auth & Private Storage (Free Tier)

1. Create a free project at <https://supabase.com/dashboard>.
2. Open **SQL Editor** in Supabase and run:
   - `supabase/schema.sql` (for Supabase Auth + RLS-protected `profiles`, `chat_sessions`, `chat_messages`, `medical_reports`, `image_analyses`, `symptom_logs`, and private `medical-files` bucket), **or**
   - `database/schema.sql` if connecting directly via FastAPI SQLAlchemy (`DATABASE_URL`).
3. Copy your keys from **Project Settings -> API** and **Project Settings -> Database (Session Pooler URI)** into `backend/.env` and Vercel Environment Variables:
   ```env
   DATABASE_URL=postgresql+psycopg://postgres.<project-ref>:<password>@aws-0-<region>.pooler.supabase.com:5432/postgres?sslmode=require
   JWT_SECRET_KEY=<at-least-32-random-characters>
   VITE_SUPABASE_URL=https://<project-ref>.supabase.co
   VITE_SUPABASE_ANON_KEY=<anon-key>
   SUPABASE_URL=https://<project-ref>.supabase.co
   SUPABASE_SERVICE_ROLE_KEY=<service-role-key>
   SUPABASE_STORAGE_BUCKET=medical-files
   ```

---

## Verification Commands

```bash
# Backend tests
cd backend && pytest -q

# Frontend checks & production build
cd frontend && npm run typecheck && npm run test && npm run build
```
