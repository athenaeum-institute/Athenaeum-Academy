-- ============================================================
-- Fix Incorrect Course Assignments in Live Classes
-- Run this in your Supabase Dashboard -> SQL Editor
-- ============================================================

-- Explanation:
-- Because of the previous bug, some teachers created classes for
-- 'Biology', 'Physics', etc., but they were accidentally saved 
-- under the 'Mathematics' course_id in the database. 
-- 
-- This script finds all live classes and updates their `course_id`
-- to match the actual course that corresponds to their `subject`.

UPDATE live_classes
SET course_id = (
    SELECT id 
    FROM courses 
    WHERE courses.subject ILIKE '%' || live_classes.subject || '%' 
       OR courses.title ILIKE '%' || live_classes.subject || '%'
    LIMIT 1
)
WHERE EXISTS (
    SELECT 1 
    FROM courses 
    WHERE courses.subject ILIKE '%' || live_classes.subject || '%'
       OR courses.title ILIKE '%' || live_classes.subject || '%'
);

-- Note: After running this, students enrolled in Mathematics will 
-- no longer see the Physics/Biology/English classes, and students 
-- enrolled in Physics will correctly see their Physics classes!
