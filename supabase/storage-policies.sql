-- Private Supabase Storage bucket (`medical-files`) and per-user RLS folder policies

insert into storage.buckets (id, name, public)
values ('medical-files', 'medical-files', false)
on conflict (id) do nothing;

drop policy if exists "medical_files_owner_select" on storage.objects;
create policy "medical_files_owner_select" on storage.objects
  for select
  to authenticated
  using (
    bucket_id = 'medical-files'
    and auth.uid()::text = (storage.foldername(name))[1]
  );

drop policy if exists "medical_files_owner_insert" on storage.objects;
create policy "medical_files_owner_insert" on storage.objects
  for insert
  to authenticated
  with check (
    bucket_id = 'medical-files'
    and auth.uid()::text = (storage.foldername(name))[1]
  );

drop policy if exists "medical_files_owner_delete" on storage.objects;
create policy "medical_files_owner_delete" on storage.objects
  for delete
  to authenticated
  using (
    bucket_id = 'medical-files'
    and auth.uid()::text = (storage.foldername(name))[1]
  );
