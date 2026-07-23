-- Fix RLS policies to use the case-insensitive public.is_admin() function

-- 1. Fix live_classes
DROP POLICY IF EXISTS "Admins manage all classes" ON public.live_classes;
CREATE POLICY "Admins manage all classes" 
ON public.live_classes FOR ALL USING (
  public.is_admin()
);

-- 2. Fix course_materials
DROP POLICY IF EXISTS "Admins manage all materials" ON public.course_materials;
CREATE POLICY "Admins manage all materials" 
ON public.course_materials FOR ALL USING (
  public.is_admin()
);

-- 3. As a failsafe, ensure any existing 'Admin' roles are converted to lowercase 'admin'
UPDATE public.profiles 
SET role = 'admin' 
WHERE LOWER(role) = 'admin' AND role != 'admin';
