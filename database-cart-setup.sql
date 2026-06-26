-- ============================================================
--  Athenaeum Academy — Cart System Setup
--  Run this in: Supabase Dashboard → SQL Editor
-- ============================================================

-- 1. Create cart_items table
CREATE TABLE IF NOT EXISTS cart_items (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  course_id UUID REFERENCES courses(id) ON DELETE CASCADE,
  added_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(user_id, course_id)
);

-- 2. Enable Row Level Security
ALTER TABLE cart_items ENABLE ROW LEVEL SECURITY;

-- 3. Apply RLS Policy
CREATE POLICY "Users manage own cart" ON cart_items
  FOR ALL USING (auth.uid() = user_id);

-- 4. Grant access to authenticated users
GRANT SELECT, INSERT, DELETE ON public.cart_items TO authenticated;
