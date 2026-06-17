-- ============================================================
-- Supabase Schema & RLS Setup for Teacher Dashboard
-- Run this in your Supabase SQL Editor.
-- ============================================================

-- 1. Upgrade Announcements Table
-- Add course_id to allow course-specific announcements
ALTER TABLE public.announcements ADD COLUMN IF NOT EXISTS course_id UUID REFERENCES public.courses(id) ON DELETE CASCADE;

-- Update the target constraint to allow course IDs or general targets
-- First we must drop the old constraint if it exists. Postgres doesn't have an easy "DROP CONSTRAINT IF EXISTS" for all cases
DO $$ BEGIN
    ALTER TABLE public.announcements DROP CONSTRAINT IF EXISTS announcements_target_check;
EXCEPTION
    WHEN undefined_object THEN null;
END $$;

-- Let's just allow target to be any text (it can be 'all', 'paid', 'trial', 'free', or a course ID)
-- Or we keep it simple and just use course_id IS NOT NULL for course announcements.

-- 2. Create Mock Exams Tables
CREATE TABLE IF NOT EXISTS public.exams (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  title TEXT NOT NULL,
  course_id UUID REFERENCES public.courses(id) ON DELETE CASCADE,
  teacher_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  duration_minutes INTEGER DEFAULT 30,
  total_marks INTEGER DEFAULT 0,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()),
  is_published BOOLEAN DEFAULT false
);

CREATE TABLE IF NOT EXISTS public.exam_questions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  exam_id UUID REFERENCES public.exams(id) ON DELETE CASCADE,
  question_text TEXT NOT NULL,
  option_a TEXT NOT NULL,
  option_b TEXT NOT NULL,
  option_c TEXT NOT NULL,
  option_d TEXT NOT NULL,
  correct_option TEXT CHECK (correct_option IN ('A', 'B', 'C', 'D')),
  marks INTEGER DEFAULT 1,
  order_index INTEGER NOT NULL
);

-- 3. Update Existing RLS Policies for Teacher Access

-- Create a helper function to check if a user is a teacher
CREATE OR REPLACE FUNCTION public.is_teacher()
RETURNS BOOLEAN AS $$
BEGIN
  RETURN (
    coalesce(current_setting('request.jwt.claims', true)::jsonb->'user_metadata'->>'role', '') = 'Teacher' OR
    coalesce(current_setting('request.jwt.claims', true)::jsonb->'user_metadata'->>'role', '') = 'teacher' OR
    EXISTS (SELECT 1 FROM public.profiles WHERE id = auth.uid() AND role = 'teacher')
  );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;


-- Courses: Teachers can update and delete their OWN courses.
CREATE POLICY "Teachers can insert own courses" ON public.courses
  FOR INSERT WITH CHECK (public.is_teacher() AND instructor_id = auth.uid());

CREATE POLICY "Teachers can update own courses" ON public.courses
  FOR UPDATE USING (instructor_id = auth.uid());

CREATE POLICY "Teachers can delete own courses" ON public.courses
  FOR DELETE USING (instructor_id = auth.uid());


-- Modules: Teachers can manage modules if they own the parent course.
CREATE POLICY "Teachers manage modules" ON public.modules
  FOR ALL USING (
    EXISTS (
      SELECT 1 FROM public.courses c 
      WHERE c.id = course_id AND c.instructor_id = auth.uid()
    )
  );

-- Lessons: Teachers can manage lessons if they own the parent course.
CREATE POLICY "Teachers manage lessons" ON public.lessons
  FOR ALL USING (
    EXISTS (
      SELECT 1 FROM public.modules m 
      JOIN public.courses c ON m.course_id = c.id
      WHERE m.id = module_id AND c.instructor_id = auth.uid()
    )
  );

-- Announcements: Teachers can post announcements for their own courses
CREATE POLICY "Teachers insert announcements" ON public.announcements
  FOR INSERT WITH CHECK (
    public.is_teacher() AND 
    EXISTS (
      SELECT 1 FROM public.courses c 
      WHERE c.id = course_id AND c.instructor_id = auth.uid()
    )
  );

-- 4. Enable RLS and add Policies for Exams
ALTER TABLE public.exams ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.exam_questions ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Anyone can read published exams" ON public.exams
  FOR SELECT USING (is_published = true OR public.is_admin());

CREATE POLICY "Teachers manage own exams" ON public.exams
  FOR ALL USING (teacher_id = auth.uid());

CREATE POLICY "Anyone can read exam questions" ON public.exam_questions
  FOR SELECT USING (
    EXISTS (
      SELECT 1 FROM public.exams e WHERE e.id = exam_id AND (e.is_published = true OR e.teacher_id = auth.uid() OR public.is_admin())
    )
  );

CREATE POLICY "Teachers manage own exam questions" ON public.exam_questions
  FOR ALL USING (
    EXISTS (
      SELECT 1 FROM public.exams e WHERE e.id = exam_id AND e.teacher_id = auth.uid()
    )
  );

-- 5. Helper RPC for Teacher to check if they own a course (Optional)
-- This is useful if doing complex secure ops.

-- DONE
SELECT 'Teacher database setup complete! ✅' as status;
