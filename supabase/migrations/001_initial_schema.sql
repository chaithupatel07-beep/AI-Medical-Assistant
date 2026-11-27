-- ============================================================================
-- Migration 001: Initial Supabase Schema & Strict Owner RLS Policies
-- Execute in Supabase Dashboard -> SQL Editor
-- ============================================================================

create extension if not exists "pgcrypto";

create table if not exists public.profiles (
  id uuid primary key references auth.users(id) on delete cascade,
  full_name text not null default '',
  email text not null default '',
  preferred_language text not null default 'en' check (preferred_language in ('en', 'hi', 'te')),
  avatar_url text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.chat_sessions (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  title text not null default 'New Health Consultation',
  language text not null default 'en' check (language in ('en', 'hi', 'te')),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
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

create table if not exists public.medical_reports (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  file_name text not null,
  storage_path text not null,
  file_type text not null check (file_type in ('PDF', 'JPG', 'JPEG', 'PNG', 'WEBP')),
  language text not null default 'en' check (language in ('en', 'hi', 'te')),
  extracted_markers jsonb not null default '[]'::jsonb,
  extracted_text text not null default '',
  summary_text text not null default '',
  doctor_questions jsonb not null default '[]'::jsonb,
  created_at timestamptz not null default now()
);

create table if not exists public.image_analyses (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  storage_path text not null,
  language text not null default 'en' check (language in ('en', 'hi', 'te')),
  observations jsonb not null default '[]'::jsonb,
  safety_notes text not null default '',
  created_at timestamptz not null default now()
);

create table if not exists public.symptom_logs (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  language text not null default 'en' check (language in ('en', 'hi', 'te')),
  symptoms jsonb not null default '{}'::jsonb,
  duration text not null,
  severity integer not null check (severity between 1 and 10),
  frequency text,
  educational_guidance text not null default '',
  possible_causes jsonb not null default '[]'::jsonb,
  red_flags jsonb not null default '[]'::jsonb,
  doctor_questions jsonb not null default '[]'::jsonb,
  created_at timestamptz not null default now()
);

create index if not exists idx_chat_sessions_user on public.chat_sessions(user_id, updated_at desc);
create index if not exists idx_chat_messages_session on public.chat_messages(session_id, created_at asc);
create index if not exists idx_medical_reports_user on public.medical_reports(user_id, created_at desc);
create index if not exists idx_image_analyses_user on public.image_analyses(user_id, created_at desc);
create index if not exists idx_symptom_logs_user on public.symptom_logs(user_id, created_at desc);

alter table public.profiles enable row level security;
alter table public.chat_sessions enable row level security;
alter table public.chat_messages enable row level security;
alter table public.medical_reports enable row level security;
alter table public.image_analyses enable row level security;
alter table public.symptom_logs enable row level security;

drop policy if exists "profiles_owner_all" on public.profiles;
create policy "profiles_owner_all" on public.profiles
  for all to authenticated using (auth.uid() = id) with check (auth.uid() = id);

drop policy if exists "Users manage own chat sessions" on public.chat_sessions;
create policy "Users manage own chat sessions" on public.chat_sessions
  for all to authenticated using (auth.uid() = user_id) with check (auth.uid() = user_id);

drop policy if exists "Users manage own chat messages" on public.chat_messages;
create policy "Users manage own chat messages" on public.chat_messages
  for all to authenticated
  using (
    auth.uid() = user_id
    and exists (
      select 1 from public.chat_sessions s
      where s.id = session_id and s.user_id = auth.uid()
    )
  )
  with check (
    auth.uid() = user_id
    and exists (
      select 1 from public.chat_sessions s
      where s.id = session_id and s.user_id = auth.uid()
    )
  );

drop policy if exists "medical_reports_owner_all" on public.medical_reports;
create policy "medical_reports_owner_all" on public.medical_reports
  for all to authenticated using (auth.uid() = user_id) with check (auth.uid() = user_id);

drop policy if exists "image_analyses_owner_all" on public.image_analyses;
create policy "image_analyses_owner_all" on public.image_analyses
  for all to authenticated using (auth.uid() = user_id) with check (auth.uid() = user_id);

drop policy if exists "symptom_logs_owner_all" on public.symptom_logs;
create policy "symptom_logs_owner_all" on public.symptom_logs
  for all to authenticated using (auth.uid() = user_id) with check (auth.uid() = user_id);
