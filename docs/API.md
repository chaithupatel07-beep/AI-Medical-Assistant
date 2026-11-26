# AI Medical Assistant — REST API Documentation

Base URL (local): `http://localhost:8000` (or proxied via Vite at `/api/*`).  
Interactive OpenAPI / Swagger UI: `http://localhost:8000/docs`.

All protected endpoints require an `Authorization: Bearer <jwt_token>` header. Every query and file endpoint filters strictly by `user_id == current_user.id`.

## Health
- `GET /api/health` — Returns backend status, AI provider configuration status (`ai_configured`), model names, Tesseract availability, and general disclaimer.

## Authentication (`/api/auth`)
- `POST /api/auth/register` — Register user, enforce password complexity, create `user_profiles` row, return JWT + user.
- `POST /api/auth/login` — Authenticate email/password, return JWT + user.
- `POST /api/auth/logout` — Log sign-out activity for authenticated user.
- `POST /api/auth/forgot-password` — Generate expiring SHA-256 hashed reset token.
- `POST /api/auth/reset-password` — Validate token and update password hash.
- `GET /api/auth/me` — Return authenticated user & profile.

## User Management (`/api/users`)
- `GET /api/users/profile` — Fetch profile details.
- `PUT /api/users/profile` — Update name, age, gender, blood type, allergies, chronic conditions, emergency contact, preferred units.
- `POST /api/users/change-password` — Verify current password and update password.
- `GET /api/users/activity?limit=50` — List user's activity history.
- `DELETE /api/users/activity/{activity_id}` — Delete one activity entry.
- `DELETE /api/users/activity` — Clear user's activity history.

## AI Medical Chatbot (`/api/chat`)
- `GET /api/chat/suggested-questions` — Curated educational prompt chips.
- `GET /api/chat/sessions` — List user's chat sessions.
- `POST /api/chat/sessions` — Create a new chat session.
- `GET /api/chat/sessions/{session_id}` — Retrieve session metadata and ordered messages.
- `POST /api/chat/sessions/{session_id}/messages` — Run emergency detection, call server-side LLM, persist turn.
- `POST /api/chat/sessions/{session_id}/clear` — Clear messages in a session.
- `DELETE /api/chat/sessions/{session_id}` — Delete session and all messages.

## Symptom Information Checker (`/api/symptoms`)
- `POST /api/symptoms/check` — Validate structured symptom inputs, run emergency detection, call server-side LLM for non-diagnostic educational guidance, persist to activity history.
- `GET /api/symptoms/history` — List recent symptom check entries.

## Medical Report Summarizer (`/api/reports`)
- `POST /api/reports/upload` — Validate PDF/JPG/JPEG/PNG (extension + magic bytes + size + Pillow check), store in per-user folder, extract text (`pypdf` / OCR).
- `POST /api/reports/{report_id}/summarize` — Parse deterministic lab markers and generate AI plain-language summary without inventing missing reference ranges.
- `GET /api/reports` — List user's uploaded reports & summaries.
- `GET /api/reports/{report_id}` — Fetch single report detail.
- `GET /api/reports/{report_id}/parsed-markers` — Deterministic lab marker extraction output.
- `GET /api/reports/{report_id}/file` — Stream original uploaded file (authenticated owner only).
- `GET /api/reports/{report_id}/summary/download` — Download generated summary as Markdown (`.md`).
- `DELETE /api/reports/{report_id}` — Delete database record and stored file.

## Medical Image Analysis (`/api/images`)
- `POST /api/images/upload` — Validate JPG/JPEG/PNG image, store in per-user folder.
- `POST /api/images/{image_id}/analyze` — Send image server-side to Vision AI model, store non-diagnostic observations, limitations, and clinician review guidance.
- `GET /api/images` — List user's uploaded images.
- `GET /api/images/{image_id}` — Fetch image record.
- `GET /api/images/{image_id}/file` — Stream image bytes (authenticated owner only).
- `DELETE /api/images/{image_id}` — Delete image record and stored file.

## Health Information Library (`/api/library`)
- `GET /api/library/categories` — List the 6 health categories.
- `GET /api/library/articles?category=...&q=...` — Search and filter educational articles.
- `GET /api/library/articles/{article_id}` — Retrieve single article.

## Dashboard (`/api/dashboard`)
- `GET /api/dashboard/overview` — Live database counts, recent reports, recent chats, recent activity, AI config status, and profile summary.
