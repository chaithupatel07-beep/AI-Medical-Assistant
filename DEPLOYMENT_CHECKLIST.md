# Production Deployment Checklist

- [ ] `JWT_SECRET_KEY` set to a strong 32+ character random secret (never using local dev fallback)
- [ ] `OPENAI_API_KEY` or `GEMINI_API_KEY` set in server/hosting environment variables (never in frontend code)
- [ ] `DATABASE_URL` (or `POSTGRES_URL`) points to persistent PostgreSQL (Supabase / Neon / Render Postgres)
- [ ] `database/schema.sql` and (for Supabase) `database/policies.sql` applied
- [ ] `CORS_ORIGINS` / `FRONTEND_ORIGIN` matches the deployed frontend origin (no trailing slash)
- [ ] `GET /api/health` returns `"status": "ok"`, `"ai_configured": true`, `"database_mode": "persistent"`
- [ ] User registration, login, session persistence across reloads, and logout verified
- [ ] AI Chat, Symptom Checker, PDF/Image Report Summarizer, and Image Analysis verified
- [ ] User isolation tested (User B cannot access or delete User A's records)
- [ ] `.env` files confirmed untracked in git (`git status`)
