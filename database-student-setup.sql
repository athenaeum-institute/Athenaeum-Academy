-- ============================================================
-- Supabase Schema Update for Student Dashboard
-- Run this in your Supabase SQL Editor.
-- ============================================================

-- 1. Add Streak Columns to Profiles
ALTER TABLE public.profiles ADD COLUMN IF NOT EXISTS last_login_date DATE;
ALTER TABLE public.profiles ADD COLUMN IF NOT EXISTS streak_days INTEGER DEFAULT 0;

-- 2. Create RPC for Streak Update
CREATE OR REPLACE FUNCTION public.update_student_streak()
RETURNS json AS $$
DECLARE
  v_last_login DATE;
  v_streak INTEGER;
  v_today DATE := current_date;
  v_xp_bonus INTEGER := 0;
  v_is_milestone BOOLEAN := false;
BEGIN
  -- Get current streak
  SELECT last_login_date, streak_days 
  INTO v_last_login, v_streak 
  FROM public.profiles 
  WHERE id = auth.uid();

  IF v_last_login IS NULL OR v_last_login < v_today - interval '1 day' THEN
    -- Missed a day or first login, reset streak to 1
    v_streak := 1;
  ELSIF v_last_login = v_today - interval '1 day' THEN
    -- Logged in yesterday, increment streak
    v_streak := v_streak + 1;
  ELSE
    -- Already logged in today, no change
    RETURN json_build_object('streak', v_streak, 'bonus', 0, 'updated', false);
  END IF;

  -- Milestone logic (only if streak actually incremented today)
  IF v_streak = 7 THEN
    v_xp_bonus := 100;
    v_is_milestone := true;
  ELSIF v_streak = 30 THEN
    v_xp_bonus := 500;
    v_is_milestone := true;
  END IF;

  -- Update profile
  UPDATE public.profiles 
  SET 
    last_login_date = v_today,
    streak_days = v_streak,
    xp = xp + v_xp_bonus
  WHERE id = auth.uid();

  RETURN json_build_object(
    'streak', v_streak, 
    'bonus', v_xp_bonus, 
    'is_milestone', v_is_milestone,
    'updated', true
  );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

SELECT 'Student Dashboard Setup Complete! ✅' as status;
