-- ================================================================
-- FINAL FIX: RLS Policies with Email Direct Check
-- Isse 100% data admin ko dikhega!
-- ================================================================

-- STEP 1: DROP OLD POLICIES
DO $$
DECLARE pol RECORD;
BEGIN
  FOR pol IN 
    SELECT policyname FROM pg_policies 
    WHERE tablename = 'free_trial_requests' AND schemaname = 'public'
  LOOP
    EXECUTE format('DROP POLICY IF EXISTS %I ON public.free_trial_requests', pol.policyname);
  END LOOP;
END $$;

-- ================================================================
-- STEP 2: NAYI POLICIES BANAO
-- ================================================================

-- Student: Apna data dekhe
CREATE POLICY "student_see_own"
ON public.free_trial_requests
FOR SELECT TO authenticated
USING ((select auth.uid()) = user_id);

-- Admin: Saara data dekhe (Email check se bypass)
CREATE POLICY "admin_see_all"
ON public.free_trial_requests
FOR SELECT TO authenticated
USING (
  (auth.jwt() ->> 'email') = 'athenaeum.institute@gmail.com'
  OR
  EXISTS (
    SELECT 1 FROM public.profiles
    WHERE id = (select auth.uid())
    AND TRIM(LOWER(role)) = 'admin'
  )
);

-- Admin: Update kar sake (Email check se bypass)
CREATE POLICY "admin_update"
ON public.free_trial_requests
FOR UPDATE TO authenticated
USING (
  (auth.jwt() ->> 'email') = 'athenaeum.institute@gmail.com'
  OR
  EXISTS (
    SELECT 1 FROM public.profiles
    WHERE id = (select auth.uid())
    AND TRIM(LOWER(role)) = 'admin'
  )
)
WITH CHECK (true);

-- Student: Insert kar sake
CREATE POLICY "student_insert"
ON public.free_trial_requests
FOR INSERT TO authenticated
WITH CHECK (true);

-- ================================================================
-- STEP 3: GRANTS
-- ================================================================
GRANT SELECT, INSERT, UPDATE ON public.free_trial_requests TO authenticated;

-- ================================================================
-- VERIFY: Admin auth check
-- ================================================================
SELECT 'RLS POLICIES UPDATED SUCESSFULLY! Ab admin panel reload karo.' as result;
