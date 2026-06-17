-- ============================================================
-- Supabase Schema & RLS Setup for Mock Exams
-- Run this in your Supabase SQL Editor.
-- ============================================================

-- 1. Create Exam Results Table
CREATE TABLE IF NOT EXISTS public.exam_results (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  student_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE,
  exam_id UUID REFERENCES public.exams(id) ON DELETE CASCADE,
  score INTEGER DEFAULT 0,
  total_marks INTEGER DEFAULT 0,
  percentage NUMERIC DEFAULT 0,
  time_taken_minutes INTEGER DEFAULT 0,
  answers JSONB DEFAULT '{}'::jsonb,
  completed_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()),
  xp_awarded INTEGER DEFAULT 0
);

-- 2. Enable RLS
ALTER TABLE public.exam_results ENABLE ROW LEVEL SECURITY;

-- 3. Policies for Exam Results
-- Students can only view their own results
CREATE POLICY "Students can view own results" ON public.exam_results
  FOR SELECT USING (student_id = auth.uid() OR public.is_admin());

-- Students can insert their own results
CREATE POLICY "Students can insert own results" ON public.exam_results
  FOR INSERT WITH CHECK (student_id = auth.uid());

-- Teachers can view results of exams they created
CREATE POLICY "Teachers can view results for their exams" ON public.exam_results
  FOR SELECT USING (
    EXISTS (
      SELECT 1 FROM public.exams e 
      WHERE e.id = exam_id AND e.teacher_id = auth.uid()
    )
  );

-- 4. Add helper function to add XP securely
CREATE OR REPLACE FUNCTION public.add_student_xp(amount INTEGER)
RETURNS void AS $$
BEGIN
  UPDATE public.profiles
  SET xp = xp + amount
  WHERE id = auth.uid();
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

SELECT 'Exam setup complete! ✅' as status;
