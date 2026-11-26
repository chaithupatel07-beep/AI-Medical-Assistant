# Testing Report — AI Medical Assistant

## Automated Backend Tests (`pytest`)
- Command: `cd backend && .venv\Scripts\pytest.exe -q`
- Coverage:
  - Health & 6-category Health Information Library (`test_health_and_library`)
  - Registration, password complexity, duplicate conflict, forgot/reset password, login (`test_auth_flow_password_validation_and_recovery`)
  - Strict user-specific isolation & profile updates (`test_user_isolation_and_profile_activity`)
  - Unconfigured AI `503` guard & mocked emergency chat turn (`test_chat_unconfigured_503_and_mocked_ai_turn`)
  - PDF/PNG upload validation, magic-byte enforcement, deterministic lab markers without invented ranges, DB `file_data` fallback (`test_report_upload_validation_markers_and_isolation`)
  - Medical image upload, secure stream, and deletion (`test_image_upload_and_delete`)
  - Multilingual Telugu, Hindi, and English library & profile language persistence (`test_multilingual_telugu_hindi_english`)
  - Cloud PostgreSQL / Neon `POSTGRES_URL` normalization (`test_production_database_url_normalization`)
  - `GEMINI_API_KEY` / `OPENAI_API_KEY` auto-detection & sanitization (`test_gemini_api_key_autodetection_and_sanitization`)
  - `/api/v1/*` compatibility endpoints & PyMuPDF extraction (`test_v1_endpoints_and_pymupdf`)
- Note: AI generation calls inside unit/integration tests use `AsyncMock` so tests run deterministically offline; live Gemini 2.5 Flash calls were verified separately via smoke tests.

## Automated Frontend Tests (`Vitest + React Testing Library`)
- Command: `cd frontend && npm run test`
- Coverage (`src/test/app.test.tsx`):
  - Landing page hero, services, safety disclaimer, and FAQ rendering
  - Regional language switching across English, Telugu (`తెలుగు`), and Hindi (`हिन्दी`)
  - Login form validation via React Hook Form + Zod

## Static & Build Verification
- `cd frontend && npm run typecheck && npm run lint && npm run build`
- `cd backend && python -m compileall app`
