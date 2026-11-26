-- ============================================================
-- AI Medical Assistant - Supabase Row Level Security (RLS)
-- ============================================================
-- Run after database/schema.sql on Supabase PostgreSQL.
-- Enforces strict per-user isolation: auth.uid()::text = user_id

ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE medical_reports ENABLE ROW LEVEL SECURITY;
ALTER TABLE report_summaries ENABLE ROW LEVEL SECURITY;
ALTER TABLE chat_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE chat_messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE uploaded_images ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_activity ENABLE ROW LEVEL SECURITY;

-- Users table
DROP POLICY IF EXISTS users_select_own ON users;
CREATE POLICY users_select_own ON users
    FOR SELECT USING (auth.uid()::text = id);

DROP POLICY IF EXISTS users_update_own ON users;
CREATE POLICY users_update_own ON users
    FOR UPDATE USING (auth.uid()::text = id) WITH CHECK (auth.uid()::text = id);

-- UserProfiles table
DROP POLICY IF EXISTS profiles_all_own ON user_profiles;
CREATE POLICY profiles_all_own ON user_profiles
    FOR ALL USING (auth.uid()::text = user_id) WITH CHECK (auth.uid()::text = user_id);

-- MedicalReports table
DROP POLICY IF EXISTS reports_all_own ON medical_reports;
CREATE POLICY reports_all_own ON medical_reports
    FOR ALL USING (auth.uid()::text = user_id) WITH CHECK (auth.uid()::text = user_id);

-- ReportSummaries table
DROP POLICY IF EXISTS summaries_all_own ON report_summaries;
CREATE POLICY summaries_all_own ON report_summaries
    FOR ALL USING (auth.uid()::text = user_id) WITH CHECK (auth.uid()::text = user_id);

-- ChatSessions table
DROP POLICY IF EXISTS chat_sessions_all_own ON chat_sessions;
CREATE POLICY chat_sessions_all_own ON chat_sessions
    FOR ALL USING (auth.uid()::text = user_id) WITH CHECK (auth.uid()::text = user_id);

-- ChatMessages table
DROP POLICY IF EXISTS chat_messages_all_own ON chat_messages;
CREATE POLICY chat_messages_all_own ON chat_messages
    FOR ALL USING (auth.uid()::text = user_id) WITH CHECK (auth.uid()::text = user_id);

-- UploadedImages table
DROP POLICY IF EXISTS uploaded_images_all_own ON uploaded_images;
CREATE POLICY uploaded_images_all_own ON uploaded_images
    FOR ALL USING (auth.uid()::text = user_id) WITH CHECK (auth.uid()::text = user_id);

-- UserActivity table
DROP POLICY IF EXISTS user_activity_all_own ON user_activity;
CREATE POLICY user_activity_all_own ON user_activity
    FOR ALL USING (auth.uid()::text = user_id) WITH CHECK (auth.uid()::text = user_id);

-- ============================================================
-- Private Supabase Storage Bucket ("medical-files")
-- ============================================================
INSERT INTO storage.buckets (id, name, public)
VALUES ('medical-files', 'medical-files', FALSE)
ON CONFLICT (id) DO NOTHING;

DROP POLICY IF EXISTS storage_medical_files_own ON storage.objects;
CREATE POLICY storage_medical_files_own ON storage.objects
    FOR ALL
    USING (
        bucket_id = 'medical-files'
        AND auth.uid()::text = (storage.foldername(name))[1]
    )
    WITH CHECK (
        bucket_id = 'medical-files'
        AND auth.uid()::text = (storage.foldername(name))[1]
    );
