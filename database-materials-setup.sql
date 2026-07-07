-- ============================================================
--  Athenaeum — Course Materials System
--  Run this in Supabase SQL Editor
-- ============================================================

-- 1. Create course_materials table
CREATE TABLE IF NOT EXISTS course_materials (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  course_id UUID REFERENCES courses(id) ON DELETE CASCADE,
  teacher_id UUID REFERENCES auth.users(id),
  teacher_name TEXT NOT NULL,
  title TEXT NOT NULL,
  description TEXT,
  material_type TEXT NOT NULL
    CHECK (material_type IN ('pdf', 'announcement', 'link', 'image')),
  file_url TEXT,
  link_url TEXT,
  is_pinned BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. Enable Row Level Security
ALTER TABLE course_materials ENABLE ROW LEVEL SECURITY;

-- 3. Grant API access to authenticated role
GRANT SELECT, INSERT, UPDATE, DELETE ON course_materials TO authenticated;

-- 4. Students can only see materials for courses they are enrolled in
CREATE POLICY "Students see enrolled course materials"
ON course_materials FOR SELECT
TO authenticated
USING (
  teacher_id = (SELECT auth.uid())
  OR
  EXISTS (
    SELECT 1 FROM enrollments
    WHERE enrollments.course_id = course_materials.course_id
    AND enrollments.user_id = (SELECT auth.uid())
    AND enrollments.status IN ('paid', 'active', 'free_trial')
  )
  OR
  EXISTS (
    SELECT 1 FROM profiles
    WHERE profiles.user_id = (SELECT auth.uid())
    AND profiles.role = 'admin'
  )
);

-- 5. Teachers can insert their own materials
CREATE POLICY "Teachers insert own materials"
ON course_materials FOR INSERT
TO authenticated
WITH CHECK (
  teacher_id = (SELECT auth.uid())
);

-- 6. Teachers can update their own materials
CREATE POLICY "Teachers update own materials"
ON course_materials FOR UPDATE
TO authenticated
USING (teacher_id = (SELECT auth.uid()))
WITH CHECK (teacher_id = (SELECT auth.uid()));

-- 7. Teachers can delete their own materials; Admins can delete any
CREATE POLICY "Teachers and admins delete materials"
ON course_materials FOR DELETE
TO authenticated
USING (
  teacher_id = (SELECT auth.uid())
  OR
  EXISTS (
    SELECT 1 FROM profiles
    WHERE profiles.user_id = (SELECT auth.uid())
    AND profiles.role = 'admin'
  )
);

-- ============================================================
--  Storage Bucket Setup
--  Run these AFTER creating the 'course-materials' bucket
--  in Supabase Storage dashboard (Settings: private, 10MB limit,
--  MIME types: application/pdf, image/jpeg, image/png, image/webp)
-- ============================================================

-- Allow authenticated teachers to upload files
CREATE POLICY "Teachers upload materials"
ON storage.objects FOR INSERT
TO authenticated
WITH CHECK (
  bucket_id = 'course-materials'
  AND auth.uid() IS NOT NULL
);

-- Allow authenticated users (enrolled students) to download files
CREATE POLICY "Authenticated users download materials"
ON storage.objects FOR SELECT
TO authenticated
USING (
  bucket_id = 'course-materials'
  AND auth.uid() IS NOT NULL
);

-- Allow teachers to delete their own uploaded files
CREATE POLICY "Teachers delete own material files"
ON storage.objects FOR DELETE
TO authenticated
USING (
  bucket_id = 'course-materials'
  AND auth.uid() IS NOT NULL
);

-- ============================================================
--  Admin policy: admins can UPDATE (pin/unpin) any material
-- ============================================================
CREATE POLICY "Admins manage all materials"
ON course_materials FOR ALL
TO authenticated
USING (
  EXISTS (
    SELECT 1 FROM profiles
    WHERE profiles.user_id = (SELECT auth.uid())
    AND profiles.role = 'admin'
  )
);
