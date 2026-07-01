-- Create free_trial_requests table
CREATE TABLE IF NOT EXISTS free_trial_requests (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id),
    full_name TEXT NOT NULL,
    email TEXT NOT NULL,
    phone TEXT NOT NULL,
    course_name TEXT NOT NULL,
    preferred_time TEXT NOT NULL,
    status TEXT DEFAULT 'pending',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Enable RLS
ALTER TABLE free_trial_requests ENABLE ROW LEVEL SECURITY;

-- Policy: Users can manage their own trial requests
CREATE POLICY "Users manage own trial requests" 
ON free_trial_requests 
FOR ALL 
USING (auth.uid() = user_id);

-- Policy: Admins can view all trial requests
CREATE POLICY "Admins see all trial requests" 
ON free_trial_requests 
FOR SELECT 
USING (
    EXISTS (
        SELECT 1 
        FROM profiles 
        WHERE profiles.id = auth.uid() 
        AND (profiles.role = 'Admin' OR profiles.role = 'admin')
    )
);

-- Policy: Admins can update all trial requests (e.g. status)
CREATE POLICY "Admins update all trial requests" 
ON free_trial_requests 
FOR UPDATE 
USING (
    EXISTS (
        SELECT 1 
        FROM profiles 
        WHERE profiles.id = auth.uid() 
        AND (profiles.role = 'Admin' OR profiles.role = 'admin')
    )
);
