# Production Deployment Guide

## Option 1: Unified Single-Project Deploy on Vercel (`vercel.json` Services)

1. Push the repository to GitHub (`.env` files are excluded by `.gitignore`).
2. Import the repository root (`./`) in Vercel with **Application Preset: `Services`**.
3. Attach **Neon Serverless Postgres** in Vercel **Storage** (sets `DATABASE_URL` / `POSTGRES_URL` automatically) or provide a Supabase PostgreSQL `DATABASE_URL`.
4. Add Environment Variables in Vercel **Settings → Environment Variables**:
   - `JWT_SECRET_KEY`: 32+ random characters
   - `GEMINI_API_KEY` (or `OPENAI_API_KEY`): server-side AI API key
   - `DATABASE_URL`: PostgreSQL connection string (auto-populated when Neon is connected)
5. Redeploy if variables were added after the initial build, then verify `GET /api/health` returns `"ai_configured": true` and `"database_mode": "persistent"`.

## Option 2: Render Full-Stack Blueprint (`render.yaml`) + Docker

1. Connect the repository in Render → **New + → Blueprint**.
2. `render.yaml` provisions `ai-medical-assistant-db` (PostgreSQL) and `ai-medical-assistant` (multi-stage Docker container running React `frontend/dist` + FastAPI + Tesseract OCR).
3. Enter `OPENAI_API_KEY` (or `GEMINI_API_KEY`) when prompted and deploy.

## Option 3: Supabase Database + RLS Setup

1. Run `database/schema.sql` in the Supabase SQL Editor.
2. Run `database/policies.sql` to enable Row Level Security on all tables and create the private `medical-files` storage bucket.
3. Configure `DATABASE_URL`, `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_ROLE_KEY`, and `SUPABASE_JWT_SECRET` on the backend only.
