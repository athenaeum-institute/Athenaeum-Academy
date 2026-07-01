-- ============================================================
-- Athenaeum Academy: MASTER DATABASE SETUP SCRIPT
-- Run this ONCE in your Supabase SQL Editor.
-- It safely creates all necessary tables in the correct order.
-- ============================================================

-- ───────────────────────────────────────────────────────────
-- 1. PROFILES TABLE & AUTH TRIGGER
-- ───────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS public.profiles (
  id            UUID        REFERENCES auth.users(id) ON DELETE CASCADE PRIMARY KEY,
  full_name     TEXT,
  role          TEXT        DEFAULT 'student' CHECK (role IN ('student','teacher','admin')),
  plan_type     TEXT        DEFAULT 'trial'   CHECK (plan_type IN ('trial','paid','free')),
  status        TEXT        DEFAULT 'active'  CHECK (status IN ('active','blocked','deleted')),
  xp            INTEGER     DEFAULT 0,
  trial_start   TIMESTAMPTZ DEFAULT now(),
  trial_end     TIMESTAMPTZ DEFAULT (now() + interval '3 days'),
  phone         TEXT,
  avatar_url    TEXT,
  created_at    TIMESTAMPTZ DEFAULT now(),
  updated_at    TIMESTAMPTZ DEFAULT now()
);

-- Auto-create profile trigger
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS trigger LANGUAGE plpgsql SECURITY DEFINER SET search_path = 'public' AS $$
BEGIN
  INSERT INTO public.profiles (id, full_name, role, plan_type)
  VALUES (
    NEW.id,
    COALESCE(NEW.raw_user_meta_data->>'full_name', split_part(COALESCE(NEW.email, ''), '@', 1)),
    COALESCE(NEW.raw_user_meta_data->>'role', 'student'),
    'trial'
  );
  RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE PROCEDURE public.handle_new_user();

-- ───────────────────────────────────────────────────────────
-- 2. AI USAGE TABLE
-- ───────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS public.ai_usage (
  id            BIGINT      GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  user_id       UUID        REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
  usage_date    DATE        DEFAULT current_date NOT NULL,
  questions_used INT        DEFAULT 0,
  quizzes_used  INT         DEFAULT 0,
  updated_at    TIMESTAMPTZ DEFAULT now(),
  UNIQUE(user_id, usage_date)
);

-- ───────────────────────────────────────────────────────────
-- 3. COURSES & LESSONS TABLES
-- ───────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS public.courses (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  title TEXT NOT NULL,
  description TEXT,
  category TEXT CHECK (category IN ('o_levels', 'a_levels', 'matric', 'inter', 'A-Level', 'O-Level', 'Matric', 'Inter')),
  subject TEXT,
  thumbnail_url TEXT,
  price NUMERIC DEFAULT 0,
  is_free_preview BOOLEAN DEFAULT false,
  instructor_id UUID REFERENCES public.profiles(id),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()),
  is_published BOOLEAN DEFAULT false
);

CREATE TABLE IF NOT EXISTS public.modules (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  course_id UUID REFERENCES public.courses(id) ON DELETE CASCADE,
  title TEXT NOT NULL,
  order_index INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS public.lessons (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  module_id UUID REFERENCES public.modules(id) ON DELETE CASCADE,
  title TEXT NOT NULL,
  video_url TEXT,
  duration_minutes INTEGER DEFAULT 0,
  order_index INTEGER NOT NULL,
  is_free_preview BOOLEAN DEFAULT false
);

-- If old enrollments table exists with course_name (text), drop it to avoid conflict
DO $$ BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='enrollments' AND column_name='course_name') THEN
        DROP TABLE public.enrollments CASCADE;
    END IF;
END $$;

CREATE TABLE IF NOT EXISTS public.enrollments (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  student_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  course_id UUID REFERENCES public.courses(id) ON DELETE CASCADE,
  enrolled_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()),
  payment_status TEXT CHECK (payment_status IN ('free', 'paid')) DEFAULT 'free',
  UNIQUE(student_id, course_id)
);

CREATE TABLE IF NOT EXISTS public.user_progress (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  student_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  lesson_id UUID REFERENCES public.lessons(id) ON DELETE CASCADE,
  completed BOOLEAN DEFAULT false,
  completed_at TIMESTAMP WITH TIME ZONE,
  xp_awarded BOOLEAN DEFAULT false,
  UNIQUE(student_id, lesson_id)
);

-- ───────────────────────────────────────────────────────────
-- 4. ANNOUNCEMENTS TABLE
-- ───────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS public.announcements (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  title TEXT NOT NULL,
  message TEXT NOT NULL,
  target TEXT CHECK (target IN ('all', 'paid', 'trial', 'free')) DEFAULT 'all',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()),
  is_active BOOLEAN DEFAULT true
);

-- ───────────────────────────────────────────────────────────
-- 5. ADMIN UTILITY FUNCTIONS (RPC)
-- ───────────────────────────────────────────────────────────
CREATE OR REPLACE FUNCTION public.is_admin()
RETURNS BOOLEAN AS $$
BEGIN
  RETURN (
    coalesce(current_setting('request.jwt.claims', true)::jsonb->'user_metadata'->>'role', '') = 'Admin' OR
    EXISTS (SELECT 1 FROM public.profiles WHERE id = auth.uid() AND role = 'admin')
  );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE OR REPLACE FUNCTION public.admin_update_plan(target_user_id UUID, new_plan TEXT)
RETURNS void AS $$
BEGIN
  IF NOT public.is_admin() THEN RAISE EXCEPTION 'Access denied.'; END IF;
  
  -- 1. Update the user's plan in profiles
  UPDATE public.profiles SET plan_type = new_plan WHERE id = target_user_id;
  
  -- 2. Ensure their individual course enrollments match the new plan
  IF new_plan != 'paid' THEN
    UPDATE public.enrollments SET payment_status = 'free', status = 'free' WHERE student_id = target_user_id;
  ELSE
    UPDATE public.enrollments SET payment_status = 'paid', status = 'paid' WHERE student_id = target_user_id;
  END IF;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE OR REPLACE FUNCTION public.admin_update_status(target_user_id UUID, new_status TEXT)
RETURNS void AS $$
BEGIN
  IF NOT public.is_admin() THEN RAISE EXCEPTION 'Access denied.'; END IF;
  UPDATE public.profiles SET status = new_status WHERE id = target_user_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE OR REPLACE FUNCTION public.admin_assign_teacher(target_user_id UUID, is_teacher BOOLEAN)
RETURNS void AS $$
BEGIN
  IF NOT public.is_admin() THEN RAISE EXCEPTION 'Access denied.'; END IF;
  UPDATE public.profiles SET role = CASE WHEN is_teacher THEN 'teacher' ELSE 'student' END WHERE id = target_user_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ───────────────────────────────────────────────────────────
-- 6. ENABLE RLS & POLICIES
-- ───────────────────────────────────────────────────────────
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.ai_usage ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.courses ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.modules ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.lessons ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.enrollments ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_progress ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.announcements ENABLE ROW LEVEL SECURITY;

-- Disable existing policies if needed to avoid duplicate errors (or use DO block)
-- For simplicity, assuming this is a fresh run or policies don't exist yet, 
-- but if they do, Supabase will just ignore them if we use standard DDL.
-- However, DROP POLICY IF EXISTS is safer.

DO $$ 
DECLARE
  table_names text[] := ARRAY['profiles', 'ai_usage', 'courses', 'modules', 'lessons', 'enrollments', 'user_progress', 'announcements'];
  t text;
  pol record;
BEGIN
  FOREACH t IN ARRAY table_names
  LOOP
    FOR pol IN SELECT policyname FROM pg_policies WHERE schemaname = 'public' AND tablename = t
    LOOP
      EXECUTE format('DROP POLICY IF EXISTS %I ON public.%I', pol.policyname, t);
    END LOOP;
  END LOOP;
END $$;

-- Profiles
CREATE POLICY "Users can view own profile" ON public.profiles FOR SELECT USING (auth.uid() = id OR public.is_admin());
CREATE POLICY "Users can update own profile" ON public.profiles FOR UPDATE USING (auth.uid() = id OR public.is_admin());

-- AI Usage
CREATE POLICY "Users can view own AI usage" ON public.ai_usage FOR SELECT USING (auth.uid() = user_id OR public.is_admin());
CREATE POLICY "Users can upsert own AI usage" ON public.ai_usage FOR INSERT WITH CHECK (auth.uid() = user_id OR public.is_admin());
CREATE POLICY "Users can update own AI usage" ON public.ai_usage FOR UPDATE USING (auth.uid() = user_id OR public.is_admin());

-- Courses
CREATE POLICY "Anyone can read published courses" ON public.courses FOR SELECT USING (is_published = true OR public.is_admin());
CREATE POLICY "Admin full access courses" ON public.courses FOR ALL USING (public.is_admin());

-- Modules & Lessons
CREATE POLICY "Anyone can read modules" ON public.modules FOR SELECT USING (true);
CREATE POLICY "Admin full access modules" ON public.modules FOR ALL USING (public.is_admin());
CREATE POLICY "Anyone can read lessons" ON public.lessons FOR SELECT USING (true);
CREATE POLICY "Admin full access lessons" ON public.lessons FOR ALL USING (public.is_admin());

-- Enrollments & Progress
CREATE POLICY "Students view own enrollments" ON public.enrollments FOR SELECT USING (auth.uid() = student_id OR public.is_admin());
CREATE POLICY "Students insert own enrollments" ON public.enrollments FOR INSERT WITH CHECK (auth.uid() = student_id OR public.is_admin());
CREATE POLICY "Students view own progress" ON public.user_progress FOR SELECT USING (auth.uid() = student_id OR public.is_admin());
CREATE POLICY "Students update own progress" ON public.user_progress FOR UPDATE USING (auth.uid() = student_id OR public.is_admin());
CREATE POLICY "Students insert own progress" ON public.user_progress FOR INSERT WITH CHECK (auth.uid() = student_id OR public.is_admin());

-- Announcements
CREATE POLICY "Anyone can read active announcements" ON public.announcements FOR SELECT USING (is_active = true OR public.is_admin());
CREATE POLICY "Admin full access announcements" ON public.announcements FOR ALL USING (public.is_admin());

-- ───────────────────────────────────────────────────────────
-- 7. GRANT PERMISSIONS
-- ───────────────────────────────────────────────────────────
GRANT USAGE ON SCHEMA public TO anon, authenticated;
GRANT ALL ON ALL TABLES IN SCHEMA public TO anon, authenticated;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO anon, authenticated;

SELECT 'Master Setup Complete! ✅' AS status;
