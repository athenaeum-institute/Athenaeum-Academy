-- ============================================================
-- Supabase Schema Update for Announcements System
-- Run this in your Supabase SQL Editor.
-- ============================================================

-- 1. Ensure Announcements table has all required columns
ALTER TABLE public.announcements ADD COLUMN IF NOT EXISTS type TEXT DEFAULT 'info' CHECK (type IN ('info', 'success', 'warning', 'urgent'));
ALTER TABLE public.announcements ADD COLUMN IF NOT EXISTS target TEXT DEFAULT 'all' CHECK (target IN ('all', 'paid', 'trial', 'parents', 'teachers'));
ALTER TABLE public.announcements ADD COLUMN IF NOT EXISTS expires_at TIMESTAMP WITH TIME ZONE;
ALTER TABLE public.announcements ADD COLUMN IF NOT EXISTS is_pinned BOOLEAN DEFAULT false;
ALTER TABLE public.announcements ADD COLUMN IF NOT EXISTS course_id UUID REFERENCES public.courses(id) ON DELETE CASCADE;

-- 2. Drop existing target check constraint if it's restrictive and recreate it
ALTER TABLE public.announcements DROP CONSTRAINT IF EXISTS announcements_target_check;
ALTER TABLE public.announcements ADD CONSTRAINT announcements_target_check CHECK (target IN ('all', 'paid', 'trial', 'parents', 'teachers'));

-- 3. Enable Supabase Realtime for the announcements table
-- This allows clients to listen to inserts/updates on this table without polling
BEGIN;
  DROP PUBLICATION IF EXISTS supabase_realtime;
  CREATE PUBLICATION supabase_realtime;
COMMIT;
ALTER PUBLICATION supabase_realtime ADD TABLE public.announcements;

-- 4. RLS Policy for Everyone to read active announcements
DROP POLICY IF EXISTS "Anyone can read active announcements" ON public.announcements;
CREATE POLICY "Anyone can read active announcements" ON public.announcements
  FOR SELECT USING (is_active = true OR public.is_admin());

SELECT 'Announcements Setup Complete! ✅' as status;
