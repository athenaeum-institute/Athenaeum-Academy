-- Ultimate Fix for Live Classes Deletion
-- We will replace the policy with a direct, failsafe ILIKE check.

DROP POLICY IF EXISTS "Admins manage all classes" ON public.live_classes;

CREATE POLICY "Admins manage all classes" 
ON public.live_classes FOR ALL 
TO authenticated
USING (
  EXISTS (
    SELECT 1 FROM public.profiles 
    WHERE profiles.id = auth.uid() 
    AND profiles.role ILIKE '%admin%'
  )
);

-- Ensure authenticated users can delete
GRANT DELETE ON public.live_classes TO authenticated;
