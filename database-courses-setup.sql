-- ============================================================
-- Supabase Schema & RLS Setup for Courses & Progress
-- ============================================================

-- 1. Ensure `xp` column exists in profiles
ALTER TABLE public.profiles ADD COLUMN IF NOT EXISTS xp INTEGER DEFAULT 0;

-- 2. Create courses table
CREATE TABLE IF NOT EXISTS public.courses (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  title TEXT NOT NULL,
  description TEXT,
  category TEXT CHECK (category IN ('o_levels', 'a_levels', 'matric', 'inter')),
  subject TEXT,
  thumbnail_url TEXT,
  price NUMERIC DEFAULT 0,
  is_free_preview BOOLEAN DEFAULT false,
  instructor_id UUID REFERENCES public.profiles(id),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()),
  is_published BOOLEAN DEFAULT false
);

-- 3. Create modules table
CREATE TABLE IF NOT EXISTS public.modules (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  course_id UUID REFERENCES public.courses(id) ON DELETE CASCADE,
  title TEXT NOT NULL,
  order_index INTEGER NOT NULL
);

-- 4. Create lessons table
CREATE TABLE IF NOT EXISTS public.lessons (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  module_id UUID REFERENCES public.modules(id) ON DELETE CASCADE,
  title TEXT NOT NULL,
  video_url TEXT,
  duration_minutes INTEGER DEFAULT 0,
  order_index INTEGER NOT NULL,
  is_free_preview BOOLEAN DEFAULT false
);

-- 5. Create enrollments table
CREATE TABLE IF NOT EXISTS public.enrollments (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  student_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  course_id UUID REFERENCES public.courses(id) ON DELETE CASCADE,
  enrolled_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()),
  payment_status TEXT CHECK (payment_status IN ('free', 'paid')) DEFAULT 'free',
  UNIQUE(student_id, course_id)
);

-- 6. Create user_progress table
CREATE TABLE IF NOT EXISTS public.user_progress (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  student_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  lesson_id UUID REFERENCES public.lessons(id) ON DELETE CASCADE,
  completed BOOLEAN DEFAULT false,
  completed_at TIMESTAMP WITH TIME ZONE,
  xp_awarded BOOLEAN DEFAULT false,
  UNIQUE(student_id, lesson_id)
);

-- ============================================================
-- ROW LEVEL SECURITY (RLS)
-- ============================================================

-- Enable RLS on all tables
ALTER TABLE public.courses ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.modules ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.lessons ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.enrollments ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_progress ENABLE ROW LEVEL SECURITY;

-- Utility Function: Check if user is Admin
CREATE OR REPLACE FUNCTION public.is_admin()
RETURNS BOOLEAN AS $$
BEGIN
  RETURN (
    coalesce(current_setting('request.jwt.claims', true)::jsonb->'user_metadata'->>'role', '') = 'Admin'
  );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;


-- Courses RLS
CREATE POLICY "Anyone can read published courses" ON public.courses
  FOR SELECT USING (is_published = true OR public.is_admin());

CREATE POLICY "Admin full access courses" ON public.courses
  FOR ALL USING (public.is_admin());

-- Modules RLS
CREATE POLICY "Anyone can read modules of published courses" ON public.modules
  FOR SELECT USING (
    EXISTS (SELECT 1 FROM public.courses WHERE id = public.modules.course_id AND (is_published = true OR public.is_admin()))
  );

CREATE POLICY "Admin full access modules" ON public.modules
  FOR ALL USING (public.is_admin());

-- Lessons RLS
CREATE POLICY "Anyone can read lessons of published courses" ON public.lessons
  FOR SELECT USING (
    EXISTS (
      SELECT 1 FROM public.modules m 
      JOIN public.courses c ON m.course_id = c.id 
      WHERE m.id = public.lessons.module_id AND (c.is_published = true OR public.is_admin())
    )
  );

CREATE POLICY "Admin full access lessons" ON public.lessons
  FOR ALL USING (public.is_admin());

-- Enrollments RLS
CREATE POLICY "Students can view their own enrollments" ON public.enrollments
  FOR SELECT USING (auth.uid() = student_id);

CREATE POLICY "Students can insert their own enrollments" ON public.enrollments
  FOR INSERT WITH CHECK (auth.uid() = student_id);

CREATE POLICY "Admin full access enrollments" ON public.enrollments
  FOR ALL USING (public.is_admin());

-- User Progress RLS
CREATE POLICY "Students can view their own progress" ON public.user_progress
  FOR SELECT USING (auth.uid() = student_id);

CREATE POLICY "Students can update their own progress" ON public.user_progress
  FOR UPDATE USING (auth.uid() = student_id);
  
CREATE POLICY "Students can insert their own progress" ON public.user_progress
  FOR INSERT WITH CHECK (auth.uid() = student_id);

CREATE POLICY "Admin full access user_progress" ON public.user_progress
  FOR ALL USING (public.is_admin());
