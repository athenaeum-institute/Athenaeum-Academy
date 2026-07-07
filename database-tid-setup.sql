-- ============================================================
--  Athenaeum — Local Payments (TID) Setup
--  Run this in Supabase SQL Editor
-- ============================================================

-- 1. Add transaction_id column to enrollments
ALTER TABLE public.enrollments 
ADD COLUMN IF NOT EXISTS transaction_id TEXT;

-- 2. Update the constraint on payment_status to allow 'pending'
-- Attempt to drop the default generated check constraint if it exists
DO $$ 
BEGIN
    -- We catch any exceptions in case the constraint doesn't exist 
    -- or has a different generated name.
    ALTER TABLE public.enrollments DROP CONSTRAINT IF EXISTS enrollments_payment_status_check;
EXCEPTION
    WHEN OTHERS THEN
        NULL;
END $$;

-- Add a new check constraint that allows pending
ALTER TABLE public.enrollments 
ADD CONSTRAINT enrollments_payment_status_check 
CHECK (payment_status IN ('free', 'paid', 'pending', 'active', 'trial'));

-- 3. Confirm completion
SELECT 'Local Payments database setup complete! ✅' as status;
