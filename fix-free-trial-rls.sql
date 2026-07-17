-- ================================================================
-- COMPLETE FIX: Free Trial - Naye Account Ka Data Dikhne Ka Fix
-- Supabase SQL Editor mein POORA paste karke RUN karo
-- ================================================================

-- STEP 1: TABLE EXIST KARTA HAI? CHECK KARO
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT FROM information_schema.tables 
    WHERE table_schema = 'public' 
    AND table_name = 'free_trial_requests'
  ) THEN
    -- Table nahi hai to banao
    CREATE TABLE public.free_trial_requests (
      id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
      user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
      full_name TEXT NOT NULL,
      email TEXT NOT NULL,
      phone TEXT NOT NULL,
      course_name TEXT NOT NULL,
      preferred_time TEXT NOT NULL,
      status TEXT DEFAULT 'pending',
      created_at TIMESTAMPTZ DEFAULT NOW()
    );
    RAISE NOTICE 'Table banaya gaya';
  ELSE
    RAISE NOTICE 'Table pehle se exist karta hai';
  END IF;
END $$;

-- STEP 2: RLS ON KARO
ALTER TABLE public.free_trial_requests ENABLE ROW LEVEL SECURITY;

-- STEP 3: SAARI PURANI POLICIES HATAO
DO $$
DECLARE
  pol RECORD;
BEGIN
  FOR pol IN 
    SELECT policyname FROM pg_policies 
    WHERE tablename = 'free_trial_requests' AND schemaname = 'public'
  LOOP
    EXECUTE format('DROP POLICY IF EXISTS %I ON public.free_trial_requests', pol.policyname);
    RAISE NOTICE 'Policy hatayi: %', pol.policyname;
  END LOOP;
END $$;

-- STEP 4: NAYI CORRECT POLICIES BANAO

-- Policy 1: Koi bhi authenticated user INSERT kar sake
CREATE POLICY "allow_student_insert"
ON public.free_trial_requests
FOR INSERT
TO authenticated
WITH CHECK (true);

-- Policy 2: Students apne requests dekh sakein
CREATE POLICY "allow_student_select_own"
ON public.free_trial_requests
FOR SELECT
TO authenticated
USING ((select auth.uid()) = user_id);

-- Policy 3: Admins SAARE requests dekh sakein
CREATE POLICY "allow_admin_select_all"
ON public.free_trial_requests
FOR SELECT
TO authenticated
USING (
  EXISTS (
    SELECT 1 FROM public.profiles
    WHERE profiles.id = (select auth.uid())
    AND lower(profiles.role) = 'admin'
  )
);

-- Policy 4: Admins status update kar sakein
CREATE POLICY "allow_admin_update"
ON public.free_trial_requests
FOR UPDATE
TO authenticated
USING (
  EXISTS (
    SELECT 1 FROM public.profiles
    WHERE profiles.id = (select auth.uid())
    AND lower(profiles.role) = 'admin'
  )
)
WITH CHECK (true);

-- STEP 5: GRANT PERMISSIONS (Data API ke liye zaruri)
GRANT SELECT, INSERT, UPDATE ON public.free_trial_requests TO authenticated;
GRANT USAGE ON SCHEMA public TO authenticated;

-- STEP 6: REALTIME ON KARO (already on hai to skip)
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_publication_tables
    WHERE pubname = 'supabase_realtime'
    AND tablename = 'free_trial_requests'
  ) THEN
    ALTER PUBLICATION supabase_realtime ADD TABLE public.free_trial_requests;
    RAISE NOTICE 'Realtime ON kiya';
  ELSE
    RAISE NOTICE 'Realtime pehle se ON hai - skip';
  END IF;
END $$;

-- ================================================================
-- RESULT: Abhi table mein kya kya data hai dekho
-- ================================================================
SELECT 
  id,
  full_name,
  email,
  phone,
  course_name,
  preferred_time,
  status,
  created_at
FROM public.free_trial_requests
ORDER BY created_at DESC;
