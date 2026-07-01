-- Run this in your Supabase SQL Editor to fix the checkout permission issue

CREATE POLICY "Students update own enrollments" 
ON public.enrollments 
FOR UPDATE 
USING (auth.uid() = student_id OR public.is_admin());
