# API Documentation — AI Medical Assistant

Interactive Swagger documentation is available at `/docs` and OpenAPI JSON at `/openapi.json`.  
All protected endpoints require `Authorization: Bearer <token>`. User identity is derived strictly from the verified JWT `sub` claim—never from client body parameters.

## System & Health
- `GET /` — Serves SPA HTML when `frontend/dist` is built, otherwise API status JSON.
- `GET /health`, `GET /api/health`, `GET /api/v1/health` — Returns service health, `ai_configured`, `ai_ready`, `ai_mode`, `ai_provider`, `chat_model`, `vision_model`, `gemini_multimodal_ready`, `database_mode`, and disclaimer.

## Authentication
- `POST /api/auth/register`, `POST /api/v1/auth/register` — Register account, enforce password rules, create profile, issue JWT.
- `POST /api/auth/login`, `POST /api/v1/auth/login` — Verify credentials and issue JWT.
- `POST /api/auth/refresh`, `POST /api/v1/auth/refresh` — Issue a refreshed JWT for an active authenticated session.
- `POST /api/auth/logout`, `POST /api/v1/auth/logout` — Record logout activity.
- `POST /api/auth/forgot-password` & `POST /api/auth/reset-password` — Expiring SHA-256 hashed reset token flow.
- `GET /api/auth/me` & `GET /api/v1/auth/me` — Return authenticated user & profile.
- `POST /api/v1/auth/verify` — Verify JWT signature and active user record.

## AI Medical Chatbot
- `GET /api/chat/suggested-questions?lang=en|te|hi` — Localized starter questions.
- `POST /api/chat/send`, `POST /api/v1/chat` — Atomic chat endpoint (auto-creates a session if `session_id` is omitted or missing).
- `GET /api/chat/sessions`, `GET /api/v1/chat/sessions` — List user sessions.
- `POST /api/chat/sessions` — Create new session.
- `GET /api/chat/sessions/{session_id}`, `GET /api/v1/chat/sessions/{session_id}` — Session messages.
- `POST /api/chat/sessions/{session_id}/messages` — Send message (auto-creates missing/stale session + runs emergency check + Gemini/local LLM).
- `POST /api/chat/sessions/{session_id}/clear` — Clear session messages.
- `DELETE /api/chat/sessions/{session_id}`, `DELETE /api/v1/chat/sessions/{session_id}` — Delete session.

## Symptom Information Checker
- `POST /api/symptoms/check`, `POST /api/v1/symptoms/analyze` — Structured educational symptom guidance (`severity_score` 1–10, `language`: `en|te|hi`, bilingual `questions_for_doctor_en`).
- `GET /api/symptoms/history` — Recent symptom checks.

## Medical Reports
- `POST /api/reports/upload`, `POST /api/v1/reports/upload` — Upload PDF/JPG/JPEG/PNG/WEBP, validate magic bytes, extract text via PyMuPDF or Gemini Multimodal Vision.
- `POST /api/reports/{report_id}/summarize`, `POST /api/v1/reports/{report_id}/summarize` — Summarize via native Gemini Multimodal Vision (`inlineData`) or text without fabricating reference ranges.
- `GET /api/reports`, `GET /api/v1/reports` — List user reports.
- `GET /api/reports/{report_id}`, `GET /api/v1/reports/{report_id}` — Report detail.
- `GET /api/reports/{report_id}/file` — Stream original file (owner only; disk or DB fallback).
- `GET /api/reports/{report_id}/summary/download` — Download summary Markdown.
- `DELETE /api/reports/{report_id}`, `DELETE /api/v1/reports/{report_id}` — Delete report & stored file.

## Medical Images
- `POST /api/images/upload` — Upload validated JPG/JPEG/PNG/WEBP image.
- `POST /api/images/{image_id}/analyze` — Vision AI observation + limitations + review advice.
- `POST /api/v1/images/analyze` — Upload and analyze in one request.
- `GET /api/images`, `GET /api/images/{image_id}`, `GET /api/images/{image_id}/file`, `DELETE /api/images/{image_id}`.

## Dashboard & Health Library
- `GET /api/dashboard/overview`, `GET /api/v1/dashboard` — Real DB statistics, recent reports/chats, AI & DB status.
- `GET /api/library/articles`, `GET /api/v1/health/articles?category=...&q=...&lang=en|te|hi` — 6 categories, 12 multilingual articles with MedlinePlus/WHO/CDC sources.
- `GET /api/library/articles/{article_id}`, `GET /api/v1/health/articles/{article_id}`.
