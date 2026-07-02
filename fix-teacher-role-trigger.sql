-- ============================================================
-- Fix: Allow Teacher Code to Bypass Role Protection Trigger
-- ============================================================

-- 1. Update the role protection trigger to allow bypass via session variable
CREATE OR REPLACE FUNCTION public.protect_profile_role()
RETURNS TRIGGER AS $$
BEGIN
  -- Allow bypass via session variable (used by verify_teacher_code)
  IF current_setting('app.bypass_role_protect', true) = 'true' THEN
    RETURN NEW;
  END IF;

  -- If the role is being changed
  IF NEW.role IS DISTINCT FROM OLD.role THEN
    -- Allow Admins to change anyone's role
    IF public.is_admin() THEN
      RETURN NEW;
    END IF;
    
    -- Otherwise, silently block the role change by keeping the old role
    NEW.role = OLD.role;
  END IF;
  
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 2. Update verify_teacher_code to use the bypass and make the code reusable (lifetime)
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

  -- Find the code (no longer checking is_used=false, code is lifetime)
  SELECT * INTO code_record 
  FROM public.teacher_access_codes 
  WHERE code = entered_code;

  IF NOT FOUND THEN
    RAISE EXCEPTION 'Invalid security code.';
  END IF;

  -- Temporarily bypass the role protection trigger for this transaction
  PERFORM set_config('app.bypass_role_protect', 'true', true);

  -- 1. Update user's profile role to 'Teacher'
  UPDATE public.profiles SET role = 'Teacher' WHERE id = user_id;

  -- 2. Assign the teacher to the course
  UPDATE public.courses SET instructor_id = user_id WHERE id = code_record.course_id;

  RETURN true;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

SELECT 'Teacher Code system updated to lifetime reusable codes and role trigger fixed!' as status;
