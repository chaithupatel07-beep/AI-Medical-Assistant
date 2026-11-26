# System Architecture — AI Medical Assistant

## Overview

AI Medical Assistant uses a modular three-tier architecture designed for strict user isolation, non-diagnostic medical safety, multilingual accessibility (English, Telugu, Hindi), and multi-platform deployment (Vercel Services, Render Blueprint, Docker Compose).

## Layers

1. **Presentation Layer (`frontend/`)**
   - **Framework**: React 18 + TypeScript + Vite + Tailwind CSS + Shadcn/Radix UI + Lucide icons.
   - **State & Forms**: TanStack Query (`@tanstack/react-query`) for server state, React Hook Form + Zod for schema validation, and React Contexts (`AuthProvider`, `LanguageProvider`).
   - **Multilingual i18n**: Instant switching between English (`en`), Telugu (`te`), and Hindi (`hi`) across all UI views, forms, disclaimers, Health Library articles, and AI prompts.

2. **Application & AI Layer (`backend/`)**
   - **API Framework**: FastAPI + Pydantic v2 + Uvicorn, exposing `/api/*` and versioned `/api/v1/*` endpoints.
   - **Security & Guardrails**:
     - `bcrypt` password hashing + `PyJWT` HS256 verification (compatible with internal JWTs and optional `SUPABASE_JWT_SECRET`).
     - Sliding-window `RateLimitMiddleware` (`429 Too Many Requests`).
     - Server-side `file_validation.py` checking extension, MIME type, binary magic bytes (`%PDF-`, JPEG, PNG), file size, and Pillow integrity.
     - `safety.py` multilingual emergency detection and strict non-diagnostic disclaimers.
   - **Document & AI Processing**:
     - `ocr_service.py`: **PyMuPDF (`fitz`)** primary PDF text extraction + `pypdf` fallback + PyMuPDF page rendering to PNG + Tesseract OCR / Vision AI OCR fallback.
     - `report_parser.py`: Deterministic marker extraction using ONLY reference ranges present in the report.
     - `ai_service.py`: Server-side OpenAI / Gemini OpenAI-compatible client (keys never leave the server).

3. **Persistence Layer (`database/` & Storage)**
   - **Relational Database**: 8 core tables (`users`, `user_profiles`, `medical_reports`, `report_summaries`, `chat_sessions`, `chat_messages`, `uploaded_images`, `user_activity`) defined in `database/schema.sql`, with Supabase Row Level Security (`database/policies.sql`).
   - **File Storage**: Per-user isolated local directories (`uploads/`), database `file_data` (`BYTEA`/`BLOB`) fallback for stateless serverless platforms, and optional private Supabase Storage bucket (`medical-files`) via `storage_service.py`.
