-- SQL query to add welcome_sent tracking to profiles

ALTER TABLE profiles 
ADD COLUMN IF NOT EXISTS welcome_sent BOOLEAN DEFAULT FALSE;

-- Automatically mark existing profiles as sent if they are more than 5 minutes old
UPDATE profiles 
SET welcome_sent = TRUE 
WHERE created_at < NOW() - INTERVAL '5 minutes';
