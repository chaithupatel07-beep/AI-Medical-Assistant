-- ============================================================================
-- AI Medical Assistant — Supabase Schema, RLS Policies & Private Storage
-- Safe to execute in Supabase SQL Editor.
-- Enforces strict per-user isolation via auth.uid() = user_id / id.
-- ============================================================================

create extension if not exists "pgcrypto";

-- 1. User Profiles linked to Supabase Auth
create table if not exists public.profiles (
  id uuid primary key references auth.users(id) on delete cascade,
  full_name text not null default '',
  preferred_language text not null default 'en' check (preferred_language in ('en', 'hi', 'te')),
  created_at timestamptz not null default now()
);

-- 2. Chat Sessions & Messages
create table if not exists public.chat_sessions (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  title text not null default 'New Health Consultation',
  language text not null default 'en' check (language in ('en', 'hi', 'te')),
  created_at timestamptz not null default now()
);

create table if not exists public.chat_messages (
  id uuid primary key default gen_random_uuid(),
  session_id uuid not null references public.chat_sessions(id) on delete cascade,
  user_id uuid not null references auth.users(id) on delete cascade,
  language text not null default 'en' check (language in ('en', 'hi', 'te')),
  role text not null check (role in ('user', 'assistant', 'system')),
  content text not null,
  is_emergency_flagged boolean not null default false,
  created_at timestamptz not null default now()
);

-- 3. Medical Reports (PDF / JPG / PNG)
create table if not exists public.medical_reports (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  file_name text not null,
  storage_path text not null,
  file_type text not null check (file_type in ('PDF', 'JPG', 'PNG')),
  language text not null default 'en' check (language in ('en', 'hi', 'te')),
  extracted_markers jsonb not null default '[]'::jsonb,
  summary_text text not null default '',
  doctor_questions jsonb not null default '[]'::jsonb,
  created_at timestamptz not null default now()
);

-- 4. Medical Image Analyses
create table if not exists public.image_analyses (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  storage_path text not null,
  language text not null default 'en' check (language in ('en', 'hi', 'te')),
  observations jsonb not null default '[]'::jsonb,
  safety_notes text not null default '',
  created_at timestamptz not null default now()
);

-- 5. Structured Symptom Logs
create table if not exists public.symptom_logs (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  language text not null default 'en' check (language in ('en', 'hi', 'te')),
  symptoms jsonb not null default '{}'::jsonb,
  duration text not null,
  severity integer not null check (severity between 1 and 10),
  educational_guidance text not null default '',
  doctor_questions jsonb not null default '[]'::jsonb,
  created_at timestamptz not null default now()
);

-- Enable Row-Level Security (RLS)
alter table public.profiles enable row level security;
alter table public.chat_sessions enable row level security;
alter table public.chat_messages enable row level security;
alter table public.medical_reports enable row level security;
alter table public.image_analyses enable row level security;
alter table public.symptom_logs enable row level security;

-- Owner-only Policies
drop policy if exists "profiles_owner_all" on public.profiles;
create policy "profiles_owner_all" on public.profiles
  for all using (auth.uid() = id) with check (auth.uid() = id);

drop policy if exists "chat_sessions_owner_all" on public.chat_sessions;
drop policy if exists "Users manage own chat sessions" on public.chat_sessions;
create policy "Users manage own chat sessions"
  on public.chat_sessions
  for all
  to authenticated
  using (auth.uid() = user_id)
  with check (auth.uid() = user_id);

drop policy if exists "chat_messages_owner_all" on public.chat_messages;
drop policy if exists "Users manage own chat messages" on public.chat_messages;
create policy "Users manage own chat messages"
  on public.chat_messages
  for all
  to authenticated
  using (auth.uid() = user_id)
  with check (auth.uid() = user_id);

drop policy if exists "medical_reports_owner_all" on public.medical_reports;
create policy "medical_reports_owner_all" on public.medical_reports
  for all using (auth.uid() = user_id) with check (auth.uid() = user_id);

drop policy if exists "image_analyses_owner_all" on public.image_analyses;
create policy "image_analyses_owner_all" on public.image_analyses
  for all using (auth.uid() = user_id) with check (auth.uid() = user_id);

drop policy if exists "symptom_logs_owner_all" on public.symptom_logs;
create policy "symptom_logs_owner_all" on public.symptom_logs
  for all using (auth.uid() = user_id) with check (auth.uid() = user_id);

-- Private Storage Bucket (`medical-files`) with {user_id}/* folder isolation
insert into storage.buckets (id, name, public)
values ('medical-files', 'medical-files', false)
on conflict (id) do nothing;

drop policy if exists "medical_files_owner_select" on storage.objects;
create policy "medical_files_owner_select" on storage.objects
  for select using (
    bucket_id = 'medical-files'
    and auth.uid()::text = (storage.foldername(name))[1]
  );

drop policy if exists "medical_files_owner_insert" on storage.objects;
create policy "medical_files_owner_insert" on storage.objects
  for insert with check (
    bucket_id = 'medical-files'
    and auth.uid()::text = (storage.foldername(name))[1]
  );

drop policy if exists "medical_files_owner_delete" on storage.objects;
create policy "medical_files_owner_delete" on storage.objects
  for delete using (
    bucket_id = 'medical-files'
    and auth.uid()::text = (storage.foldername(name))[1]
  );
