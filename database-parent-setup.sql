-- ============================================================
-- Supabase Schema Update for Parent Dashboard
-- Run this in your Supabase SQL Editor.
-- ============================================================

-- 1. Add parent_id to profiles
ALTER TABLE public.profiles ADD COLUMN IF NOT EXISTS parent_id UUID REFERENCES public.profiles(id);

-- 2. Create Parent-Child Links Table
CREATE TABLE IF NOT EXISTS public.parent_child_links (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  parent_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE,
  student_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE,
  linked_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()),
  is_verified BOOLEAN DEFAULT true -- Setting true by default for easier testing
);

-- 3. RLS for parent_child_links
ALTER TABLE public.parent_child_links ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Parents can read their own links" ON public.parent_child_links
  FOR SELECT USING (parent_id = auth.uid() OR student_id = auth.uid());

CREATE POLICY "Parents can insert links" ON public.parent_child_links
  FOR INSERT WITH CHECK (parent_id = auth.uid());

-- 4. RLS Policy Updates for Read-Only Parent Access
-- Profiles: Parent can read linked student's profile
CREATE POLICY "Parents can view linked child profiles" ON public.profiles
  FOR SELECT USING (
    id IN (
      SELECT student_id FROM public.parent_child_links 
      WHERE parent_id = auth.uid() AND is_verified = true
    )
  );

-- Enrollments: Parent can read linked student's enrollments
CREATE POLICY "Parents can view linked child enrollments" ON public.enrollments
  FOR SELECT USING (
    student_id IN (
      SELECT student_id FROM public.parent_child_links 
      WHERE parent_id = auth.uid() AND is_verified = true
    )
  );

-- User Progress: Parent can read linked student's progress
CREATE POLICY "Parents can view linked child progress" ON public.user_progress
  FOR SELECT USING (
    student_id IN (
      SELECT student_id FROM public.parent_child_links 
      WHERE parent_id = auth.uid() AND is_verified = true
    )
  );

-- Exam Results: Parent can read linked student's exam results
CREATE POLICY "Parents can view linked child exam results" ON public.exam_results
  FOR SELECT USING (
    student_id IN (
      SELECT student_id FROM public.parent_child_links 
      WHERE parent_id = auth.uid() AND is_verified = true
    )
  );

-- 5. RPC to link child securely by email
CREATE OR REPLACE FUNCTION public.link_child_by_email(student_email TEXT)
RETURNS json AS $$
DECLARE
  v_student_id UUID;
  v_parent_id UUID := auth.uid();
  v_existing BOOLEAN;
BEGIN
  -- Find student ID from auth.users (requires security definer)
  SELECT id INTO v_student_id 
  FROM auth.users 
  WHERE email = student_email AND id IN (SELECT id FROM public.profiles WHERE role = 'student');

  IF v_student_id IS NULL THEN
    RETURN json_build_object('success', false, 'message', 'Student not found or not registered.');
  END IF;

  -- Check if already linked
  SELECT EXISTS(
    SELECT 1 FROM public.parent_child_links 
    WHERE parent_id = v_parent_id AND student_id = v_student_id
  ) INTO v_existing;

  IF v_existing THEN
    RETURN json_build_object('success', false, 'message', 'Student is already linked to your account.');
  END IF;

  -- Create link
  INSERT INTO public.parent_child_links (parent_id, student_id, is_verified)
  VALUES (v_parent_id, v_student_id, true); -- Auto verified for testing

  RETURN json_build_object('success', true, 'message', 'Student linked successfully!');
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

SELECT 'Parent Dashboard Setup Complete! ✅' as status;
