-- Enable Supabase Realtime for free_trial_requests table
-- This is required for the admin panel's real-time notification system to work.
-- Run this SQL once in the Supabase SQL Editor.

-- Add free_trial_requests to the supabase_realtime publication
-- so that postgres_changes events are fired on INSERT/UPDATE/DELETE
ALTER PUBLICATION supabase_realtime ADD TABLE public.free_trial_requests;
