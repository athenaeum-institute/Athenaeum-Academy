-- ============================================================
-- Supabase Schema & RLS Setup for Admin Dashboard
-- ============================================================

-- 1. Update Profiles Table
-- Ensure profiles table has necessary columns for admin management
ALTER TABLE public.profiles ADD COLUMN IF NOT EXISTS role TEXT DEFAULT 'student';
ALTER TABLE public.profiles ADD COLUMN IF NOT EXISTS plan_type TEXT DEFAULT 'trial';
ALTER TABLE public.profiles ADD COLUMN IF NOT EXISTS status TEXT DEFAULT 'active';

-- Add constraints if they don't exist
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'profiles_role_check') THEN
        ALTER TABLE public.profiles ADD CONSTRAINT profiles_role_check CHECK (role IN ('student', 'teacher', 'admin'));
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'profiles_plan_type_check') THEN
        ALTER TABLE public.profiles ADD CONSTRAINT profiles_plan_type_check CHECK (plan_type IN ('free', 'trial', 'paid'));
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'profiles_status_check') THEN
        ALTER TABLE public.profiles ADD CONSTRAINT profiles_status_check CHECK (status IN ('active', 'blocked', 'deleted'));
    END IF;
END $$;


-- 2. Create Announcements Table
CREATE TABLE IF NOT EXISTS public.announcements (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  title TEXT NOT NULL,
  message TEXT NOT NULL,
  target TEXT CHECK (target IN ('all', 'paid', 'trial')) DEFAULT 'all',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()),
  is_active BOOLEAN DEFAULT true
);

-- Enable RLS for Announcements
ALTER TABLE public.announcements ENABLE ROW LEVEL SECURITY;

-- Everyone can read active announcements
CREATE POLICY "Anyone can read active announcements" ON public.announcements
  FOR SELECT USING (is_active = true);

-- Admin full access to announcements
CREATE POLICY "Admin full access announcements" ON public.announcements
  FOR ALL USING (public.is_admin());


-- 3. Secure RPCs for Admin Actions
-- Standard Supabase Anon keys cannot arbitrarily UPDATE other users' profiles via REST 
-- unless RLS allows it. Instead of complex RLS on profiles (which might cause infinite recursion),
-- we use SECURITY DEFINER functions that execute with elevated privileges.

-- Function to upgrade/change a student's plan
CREATE OR REPLACE FUNCTION public.admin_update_plan(target_user_id UUID, new_plan TEXT)
RETURNS void AS $$
BEGIN
  IF NOT public.is_admin() THEN
    RAISE EXCEPTION 'Access denied. Admin only.';
  END IF;
  
  -- 1. Update the user's plan in profiles
  UPDATE public.profiles SET plan_type = new_plan WHERE id = target_user_id;
  
  -- 2. Ensure their individual course enrollments match the new plan
  IF new_plan != 'paid' THEN
    UPDATE public.enrollments SET payment_status = 'free' WHERE student_id = target_user_id;
  ELSE
    UPDATE public.enrollments SET payment_status = 'paid' WHERE student_id = target_user_id;
  END IF;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to block/unblock/soft-delete a user
CREATE OR REPLACE FUNCTION public.admin_update_status(target_user_id UUID, new_status TEXT)
RETURNS void AS $$
BEGIN
  IF NOT public.is_admin() THEN
    RAISE EXCEPTION 'Access denied. Admin only.';
  END IF;
  
  UPDATE public.profiles SET status = new_status WHERE id = target_user_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to assign teacher role
CREATE OR REPLACE FUNCTION public.admin_assign_teacher(target_user_id UUID, is_teacher BOOLEAN)
RETURNS void AS $$
BEGIN
  IF NOT public.is_admin() THEN
    RAISE EXCEPTION 'Access denied. Admin only.';
  END IF;
  
  IF is_teacher THEN
    UPDATE public.profiles SET role = 'teacher' WHERE id = target_user_id;
  ELSE
    UPDATE public.profiles SET role = 'student' WHERE id = target_user_id;
  END IF;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
