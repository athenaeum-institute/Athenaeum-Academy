-- ============================================================
-- Teacher Access Codes Setup
-- Run this script in your Supabase SQL Editor
-- ============================================================

-- 1. Create the teacher_access_codes table
CREATE TABLE IF NOT EXISTS public.teacher_access_codes (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  code TEXT UNIQUE NOT NULL,
  course_id UUID REFERENCES public.courses(id) ON DELETE CASCADE,
  is_used BOOLEAN DEFAULT false,
  used_by UUID REFERENCES auth.users(id),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()),
  used_at TIMESTAMP WITH TIME ZONE
);

-- Enable RLS
ALTER TABLE public.teacher_access_codes ENABLE ROW LEVEL SECURITY;

-- Admins can do everything
CREATE POLICY "Admin full access on teacher_access_codes" ON public.teacher_access_codes
  FOR ALL USING (public.is_admin());

-- Authenticated users can only read unused codes (for verification purposes)
CREATE POLICY "Users can read unused codes" ON public.teacher_access_codes
  FOR SELECT USING (is_used = false);


-- 2. RPC to Generate a unique Code (Admin Only)
CREATE OR REPLACE FUNCTION public.generate_teacher_code(target_course_id UUID)
RETURNS TEXT AS $$
DECLARE
  new_code TEXT;
  course_record RECORD;
BEGIN
  -- Only allow admins to generate codes
  IF NOT public.is_admin() THEN
    RAISE EXCEPTION 'Access denied. Only admins can generate teacher codes.';
  END IF;

  -- Ensure course exists
  SELECT * INTO course_record FROM public.courses WHERE id = target_course_id;
  IF NOT FOUND THEN
    RAISE EXCEPTION 'Course not found.';
  END IF;

  -- Generate a random code (e.g. ATH-MATH-XXXX)
  -- Simplified for now: ATH-<random 8 chars>
  new_code := 'ATH-' || upper(substr(md5(random()::text), 1, 8));

  -- Insert into the table
  INSERT INTO public.teacher_access_codes (code, course_id)
  VALUES (new_code, target_course_id);

  RETURN new_code;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;


-- 3. RPC for a Teacher to Verify Code (Any Auth User)
CREATE OR REPLACE FUNCTION public.verify_teacher_code(entered_code TEXT)
RETURNS BOOLEAN AS $$
DECLARE
  code_record RECORD;
  user_id UUID;
BEGIN
  user_id := auth.uid();
  IF user_id IS NULL THEN
    RAISE EXCEPTION 'You must be logged in to verify a code.';
  END IF;

  -- Find the code
  SELECT * INTO code_record 
  FROM public.teacher_access_codes 
  WHERE code = entered_code AND is_used = false;

  IF NOT FOUND THEN
    RAISE EXCEPTION 'Invalid or already used security code.';
  END IF;

  -- 1. Mark code as used
  UPDATE public.teacher_access_codes 
  SET is_used = true, used_by = user_id, used_at = now() 
  WHERE id = code_record.id;

  -- 2. Update user's profile role to 'Teacher' (bypassing triggers if needed, since this is SECURITY DEFINER)
  -- Note: If we have a trigger blocking this, the trigger must allow changes by admin. 
  -- Since SECURITY DEFINER functions run with the privileges of the creator (Admin), the profile trigger will allow it.
  UPDATE public.profiles SET role = 'Teacher' WHERE id = user_id;

  -- 3. Assign the teacher to the course
  UPDATE public.courses SET instructor_id = user_id WHERE id = code_record.course_id;

  RETURN true;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

SELECT 'Teacher Codes System Setup Complete!' as status;
