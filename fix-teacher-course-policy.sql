-- Allow teachers to view the courses they are assigned to, even if they are unpublished.
CREATE POLICY "Teachers can view own courses" 
ON public.courses 
FOR SELECT 
USING (auth.uid() = instructor_id);
