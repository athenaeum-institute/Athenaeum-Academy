-- ============================================================
-- Security Patch: Prevent Unauthorized Teacher Logins
-- ============================================================

-- 1. Ensure `pending_teacher` is a valid role (along with different casing formats)
ALTER TABLE public.profiles DROP CONSTRAINT IF EXISTS profiles_role_check;
ALTER TABLE public.profiles ADD CONSTRAINT profiles_role_check 
  CHECK (role IN ('student', 'teacher', 'admin', 'pending_teacher', 'Student', 'Teacher', 'Admin', 'Parent', 'pending_parent'));

-- 2. Update the signup trigger to forcefully set unauthorized teachers to 'pending_teacher'
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS trigger
LANGUAGE plpgsql
SECURITY INVOKER
SET search_path = ''
AS $$
DECLARE
  requested_role text;
  final_role text;
BEGIN
  requested_role := coalesce(new.raw_user_meta_data->>'role', 'Student');
  
  -- Force all Teacher/Admin signups into pending or Student (admins can only be created by admins)
  IF lower(requested_role) = 'teacher' THEN
    final_role := 'pending_teacher';
  ELSIF lower(requested_role) = 'admin' THEN
    final_role := 'Student';
  ELSE
    final_role := requested_role;
  END IF;

  insert into public.profiles (id, full_name, role, plan_type)
  values (
    new.id,
    coalesce(new.raw_user_meta_data->>'full_name', split_part(new.email, '@', 1)),
    final_role,
    'trial'   -- Everyone starts with a trial
  );
  return new;
END;
$$;

-- 3. Prevent users from updating their own role via the Supabase client
CREATE OR REPLACE FUNCTION public.protect_profile_role()
RETURNS TRIGGER AS $$
BEGIN
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

-- Drop trigger if it already exists, then attach it to the profiles table
DROP TRIGGER IF EXISTS protect_profile_role_trigger ON public.profiles;
CREATE TRIGGER protect_profile_role_trigger
BEFORE UPDATE ON public.profiles
FOR EACH ROW
EXECUTE FUNCTION public.protect_profile_role();

SELECT 'Security patch applied! Unauthorized users can no longer become teachers.' as status;
