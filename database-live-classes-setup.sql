-- ============================================================
-- Supabase Schema & RLS Setup for Live Classes
-- ============================================================

CREATE TABLE IF NOT EXISTS public.live_classes (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  course_id UUID REFERENCES public.courses(id) ON DELETE CASCADE,
  title TEXT NOT NULL,
  subject TEXT NOT NULL,
  teacher_name TEXT NOT NULL,
  description TEXT,
  start_time TIMESTAMPTZ NOT NULL,
  end_time TIMESTAMPTZ NOT NULL,
  jitsi_room_name TEXT NOT NULL UNIQUE,
  status TEXT DEFAULT 'scheduled' CHECK (status IN ('scheduled', 'live', 'ended')),
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- RLS Policies
ALTER TABLE public.live_classes ENABLE ROW LEVEL SECURITY;

-- Students can only see live classes for courses they are enrolled in
CREATE POLICY "Students see their enrolled course classes" ON public.live_classes
  FOR SELECT USING (
    EXISTS (
      SELECT 1 FROM public.enrollments 
      WHERE enrollments.course_id = live_classes.course_id 
      AND enrollments.student_id = auth.uid()
      AND enrollments.payment_status IN ('paid', 'free')
    )
  );

-- Teachers can see and manage their own classes
CREATE POLICY "Teachers manage their classes" ON public.live_classes
  FOR ALL USING (auth.uid() IN (
    SELECT id FROM public.profiles WHERE role = 'teacher'
  ));

-- Admins can see and manage all classes
CREATE POLICY "Admins manage all classes" ON public.live_classes
  FOR ALL USING (auth.uid() IN (
    SELECT id FROM public.profiles WHERE role = 'admin'
  ));

-- ============================================================
-- SAMPLE DATA (For Testing)
-- We need a valid course_id to insert sample data. 
-- Assuming you have at least one course, we will select its ID.
-- Replace the start_time/end_time manually if you want specific times.
-- ============================================================

DO $$
DECLARE
    sample_course_id UUID;
BEGIN
    -- Get the first available course to use for dummy data
    SELECT id INTO sample_course_id FROM public.courses LIMIT 1;
    
    IF sample_course_id IS NOT NULL THEN
        -- 1. LIVE NOW Class (Starts 5 mins ago, ends in 55 mins)
        INSERT INTO public.live_classes (course_id, title, subject, teacher_name, description, start_time, end_time, jitsi_room_name, status)
        VALUES (
            sample_course_id,
            'Cell Biology: Mitosis Deep Dive',
            'Biology',
            'Prof. Maria Khan',
            'An in-depth look at cell division phases.',
            NOW() - INTERVAL '5 minutes',
            NOW() + INTERVAL '55 minutes',
            'athenaeum-bio-' || gen_random_uuid(),
            'live'
        );

        -- 2. UPCOMING Class (Starts in 2 hours)
        INSERT INTO public.live_classes (course_id, title, subject, teacher_name, description, start_time, end_time, jitsi_room_name, status)
        VALUES (
            sample_course_id,
            'Algebra II: Polynomials',
            'Mathematics',
            'Mr. Ahmed Raza',
            'Solving advanced polynomial equations.',
            NOW() + INTERVAL '2 hours',
            NOW() + INTERVAL '3 hours',
            'athenaeum-math-' || gen_random_uuid(),
            'scheduled'
        );

        -- 3. UPCOMING Class (Starts in 2 days)
        INSERT INTO public.live_classes (course_id, title, subject, teacher_name, description, start_time, end_time, jitsi_room_name, status)
        VALUES (
            sample_course_id,
            'O-Level Physics: Kinematics',
            'Physics',
            'Dr. Salman',
            'Review of distance, velocity, and acceleration graphs.',
            NOW() + INTERVAL '2 days',
            NOW() + INTERVAL '2 days 1 hour',
            'athenaeum-phy-' || gen_random_uuid(),
            'scheduled'
        );
        
        -- 4. PAST Class (Ended yesterday)
        INSERT INTO public.live_classes (course_id, title, subject, teacher_name, description, start_time, end_time, jitsi_room_name, status)
        VALUES (
            sample_course_id,
            'English Essay Writing Basics',
            'English',
            'Ms. Sarah',
            'Structuring your arguments effectively.',
            NOW() - INTERVAL '1 day 2 hours',
            NOW() - INTERVAL '1 day 1 hour',
            'athenaeum-eng-' || gen_random_uuid(),
            'ended'
        );
    END IF;
END $$;
