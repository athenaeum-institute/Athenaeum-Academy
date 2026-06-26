-- 1. Create Notifications Table
CREATE TABLE IF NOT EXISTS public.notifications (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    message TEXT NOT NULL,
    type TEXT DEFAULT 'info',
    is_read BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. Enable RLS
ALTER TABLE public.notifications ENABLE ROW LEVEL SECURITY;

-- 3. Create RLS Policies for Notifications
DROP POLICY IF EXISTS "Users can read own notifications" ON public.notifications;
DROP POLICY IF EXISTS "Users can update own notifications" ON public.notifications;

CREATE POLICY "Users can read own notifications" 
ON public.notifications FOR SELECT 
USING (auth.uid() = user_id);

CREATE POLICY "Users can update own notifications" 
ON public.notifications FOR UPDATE 
USING (auth.uid() = user_id);

-- 4. Create Postgres Trigger Function
CREATE OR REPLACE FUNCTION public.notify_students_on_live_class()
RETURNS TRIGGER AS $$
BEGIN
    -- Insert a notification for every student enrolled in this course
    INSERT INTO public.notifications (user_id, title, message, type)
    SELECT 
        e.student_id, 
        'New Live Class Scheduled!', 
        'A new live class "' || NEW.title || '" has been scheduled for your course by ' || NEW.teacher_name || '.', 
        'live_class'
    FROM public.enrollments e
    WHERE e.course_id = NEW.course_id;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 5. Attach Trigger to live_classes
DROP TRIGGER IF EXISTS trigger_notify_live_class ON public.live_classes;
CREATE TRIGGER trigger_notify_live_class
AFTER INSERT ON public.live_classes
FOR EACH ROW
EXECUTE FUNCTION public.notify_students_on_live_class();
