-- ============================================================
-- Athenaeum Academy: COMMUNITY FEED SETUP
-- Run this in your Supabase SQL Editor.
-- Creates: community_posts, post_likes, post_comments + Storage bucket
-- Does NOT modify any existing tables.
-- ============================================================

-- ───────────────────────────────────────────────────────────
-- 1. COMMUNITY POSTS TABLE
-- ───────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS public.community_posts (
  id             UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id        UUID        REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
  author_name    TEXT        NOT NULL,
  author_role    TEXT        NOT NULL CHECK (author_role IN ('student', 'teacher', 'admin')),
  author_avatar  TEXT,
  content        TEXT        NOT NULL,
  image_url      TEXT,
  category       TEXT        NOT NULL DEFAULT 'general'
                             CHECK (category IN (
                               'general',
                               'class_notes',
                               'announcement',
                               'past_paper',
                               'motivational',
                               'doubt',
                               'result',
                               'exam_schedule',
                               'academy_update'
                             )),
  is_pinned      BOOLEAN     DEFAULT false,
  is_approved    BOOLEAN     DEFAULT true,
  likes_count    INTEGER     DEFAULT 0,
  comments_count INTEGER     DEFAULT 0,
  created_at     TIMESTAMPTZ DEFAULT now(),
  updated_at     TIMESTAMPTZ DEFAULT now()
);

-- ───────────────────────────────────────────────────────────
-- 2. POST LIKES TABLE
-- ───────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS public.post_likes (
  id         UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  post_id    UUID        REFERENCES public.community_posts(id) ON DELETE CASCADE NOT NULL,
  user_id    UUID        REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
  created_at TIMESTAMPTZ DEFAULT now(),
  UNIQUE(post_id, user_id)
);

-- ───────────────────────────────────────────────────────────
-- 3. POST COMMENTS TABLE
-- ───────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS public.post_comments (
  id           UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  post_id      UUID        REFERENCES public.community_posts(id) ON DELETE CASCADE NOT NULL,
  user_id      UUID        REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
  author_name  TEXT        NOT NULL,
  author_role  TEXT        NOT NULL,
  content      TEXT        NOT NULL,
  created_at   TIMESTAMPTZ DEFAULT now()
);

-- ───────────────────────────────────────────────────────────
-- 4. TRIGGER: Auto-update likes_count
-- ───────────────────────────────────────────────────────────
CREATE OR REPLACE FUNCTION public.update_likes_count()
RETURNS TRIGGER AS $$
BEGIN
  IF TG_OP = 'INSERT' THEN
    UPDATE public.community_posts
      SET likes_count = likes_count + 1
      WHERE id = NEW.post_id;
  ELSIF TG_OP = 'DELETE' THEN
    UPDATE public.community_posts
      SET likes_count = GREATEST(likes_count - 1, 0)
      WHERE id = OLD.post_id;
  END IF;
  RETURN NULL;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

DROP TRIGGER IF EXISTS on_like_change ON public.post_likes;
CREATE TRIGGER on_like_change
  AFTER INSERT OR DELETE ON public.post_likes
  FOR EACH ROW EXECUTE FUNCTION public.update_likes_count();

-- ───────────────────────────────────────────────────────────
-- 5. TRIGGER: Auto-update comments_count
-- ───────────────────────────────────────────────────────────
CREATE OR REPLACE FUNCTION public.update_comments_count()
RETURNS TRIGGER AS $$
BEGIN
  IF TG_OP = 'INSERT' THEN
    UPDATE public.community_posts
      SET comments_count = comments_count + 1
      WHERE id = NEW.post_id;
  ELSIF TG_OP = 'DELETE' THEN
    UPDATE public.community_posts
      SET comments_count = GREATEST(comments_count - 1, 0)
      WHERE id = OLD.post_id;
  END IF;
  RETURN NULL;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

DROP TRIGGER IF EXISTS on_comment_change ON public.post_comments;
CREATE TRIGGER on_comment_change
  AFTER INSERT OR DELETE ON public.post_comments
  FOR EACH ROW EXECUTE FUNCTION public.update_comments_count();

-- ───────────────────────────────────────────────────────────
-- 6. TRIGGER: Auto-update updated_at timestamp
-- ───────────────────────────────────────────────────────────
CREATE OR REPLACE FUNCTION public.update_post_timestamp()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS set_post_timestamp ON public.community_posts;
CREATE TRIGGER set_post_timestamp
  BEFORE UPDATE ON public.community_posts
  FOR EACH ROW EXECUTE FUNCTION public.update_post_timestamp();

-- ───────────────────────────────────────────────────────────
-- 7. ENABLE ROW LEVEL SECURITY
-- ───────────────────────────────────────────────────────────
ALTER TABLE public.community_posts  ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.post_likes       ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.post_comments    ENABLE ROW LEVEL SECURITY;

-- Drop old policies (safe re-run)
DROP POLICY IF EXISTS "Anyone can read approved posts"         ON public.community_posts;
DROP POLICY IF EXISTS "Logged in users can create posts"       ON public.community_posts;
DROP POLICY IF EXISTS "Users can update own posts"             ON public.community_posts;
DROP POLICY IF EXISTS "Users can delete own posts"             ON public.community_posts;
DROP POLICY IF EXISTS "Anyone can read likes"                  ON public.post_likes;
DROP POLICY IF EXISTS "Logged in users can like"               ON public.post_likes;
DROP POLICY IF EXISTS "Users can remove own like"              ON public.post_likes;
DROP POLICY IF EXISTS "Anyone can read comments"               ON public.post_comments;
DROP POLICY IF EXISTS "Logged in users can comment"            ON public.post_comments;
DROP POLICY IF EXISTS "Users can delete own comments"          ON public.post_comments;

-- community_posts policies
CREATE POLICY "Anyone can read approved posts"
  ON public.community_posts FOR SELECT
  USING (is_approved = true OR auth.uid() = user_id OR public.is_admin());

CREATE POLICY "Logged in users can create posts"
  ON public.community_posts FOR INSERT
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own posts"
  ON public.community_posts FOR UPDATE
  USING (auth.uid() = user_id OR public.is_admin());

CREATE POLICY "Users can delete own posts"
  ON public.community_posts FOR DELETE
  USING (auth.uid() = user_id OR public.is_admin());

-- post_likes policies
CREATE POLICY "Anyone can read likes"
  ON public.post_likes FOR SELECT
  USING (true);

CREATE POLICY "Logged in users can like"
  ON public.post_likes FOR INSERT
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can remove own like"
  ON public.post_likes FOR DELETE
  USING (auth.uid() = user_id);

-- post_comments policies
CREATE POLICY "Anyone can read comments"
  ON public.post_comments FOR SELECT
  USING (true);

CREATE POLICY "Logged in users can comment"
  ON public.post_comments FOR INSERT
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete own comments"
  ON public.post_comments FOR DELETE
  USING (auth.uid() = user_id OR public.is_admin());

-- ───────────────────────────────────────────────────────────
-- 8. ENABLE REALTIME (Safe — won't break existing publication)
-- ───────────────────────────────────────────────────────────
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_publication_tables
    WHERE pubname = 'supabase_realtime' AND tablename = 'community_posts'
  ) THEN
    ALTER PUBLICATION supabase_realtime ADD TABLE public.community_posts;
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM pg_publication_tables
    WHERE pubname = 'supabase_realtime' AND tablename = 'post_likes'
  ) THEN
    ALTER PUBLICATION supabase_realtime ADD TABLE public.post_likes;
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM pg_publication_tables
    WHERE pubname = 'supabase_realtime' AND tablename = 'post_comments'
  ) THEN
    ALTER PUBLICATION supabase_realtime ADD TABLE public.post_comments;
  END IF;
END $$;

-- ───────────────────────────────────────────────────────────
-- 9. STORAGE BUCKET FOR COMMUNITY IMAGES
-- ───────────────────────────────────────────────────────────
INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
VALUES (
  'community-images',
  'community-images',
  true,
  5242880,
  ARRAY['image/jpeg','image/jpg','image/png','image/webp','image/gif']
)
ON CONFLICT (id) DO NOTHING;

-- Storage policies
DROP POLICY IF EXISTS "Community images are public"            ON storage.objects;
DROP POLICY IF EXISTS "Logged in users can upload community"   ON storage.objects;
DROP POLICY IF EXISTS "Users can delete own community images"  ON storage.objects;

CREATE POLICY "Community images are public"
  ON storage.objects FOR SELECT
  USING (bucket_id = 'community-images');

CREATE POLICY "Logged in users can upload community"
  ON storage.objects FOR INSERT
  WITH CHECK (bucket_id = 'community-images' AND auth.role() = 'authenticated');

CREATE POLICY "Users can delete own community images"
  ON storage.objects FOR DELETE
  USING (bucket_id = 'community-images' AND auth.uid()::text = (storage.foldername(name))[1]);

-- ───────────────────────────────────────────────────────────
SELECT 'Community Feed Setup Complete! ✅' AS status;
