-- ============================================================
--  Athenaeum Academy — Live Classes Setup
--  Run this in: Supabase Dashboard → SQL Editor
-- ============================================================

CREATE TABLE IF NOT EXISTS live_classes (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  course_id UUID REFERENCES courses(id) ON DELETE CASCADE,
  teacher_id UUID REFERENCES auth.users(id),
  title TEXT NOT NULL,
  subject TEXT NOT NULL,
  teacher_name TEXT NOT NULL,
  description TEXT,
  start_time TIMESTAMPTZ NOT NULL,
  end_time TIMESTAMPTZ NOT NULL,
  jitsi_room_name TEXT UNIQUE NOT NULL,
  status TEXT DEFAULT 'scheduled' 
    CHECK (status IN ('scheduled','live','ended','cancelled')),
  created_at TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE live_classes ENABLE ROW LEVEL SECURITY;

-- Students see classes for their enrolled courses only
CREATE POLICY "Students see enrolled course classes" 
ON live_classes FOR SELECT USING (
  EXISTS (
    SELECT 1 FROM enrollments 
    WHERE enrollments.course_id = live_classes.course_id 
    AND enrollments.student_id = auth.uid()
  )
);

-- Teachers manage their own classes
CREATE POLICY "Teachers manage own classes" 
ON live_classes FOR ALL USING (
  teacher_id = auth.uid()
);

-- Admins manage all classes
CREATE POLICY "Admins manage all classes" 
ON live_classes FOR ALL USING (
  EXISTS (
    SELECT 1 FROM profiles 
    WHERE profiles.id = auth.uid() 
    AND profiles.role = 'admin'
  )
);

-- Grant appropriate permissions to authenticated users
GRANT SELECT, INSERT, UPDATE, DELETE ON public.live_classes TO authenticated;
