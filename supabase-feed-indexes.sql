-- sprinting.ink — Feed Performance Indexes
-- Run this in the Supabase SQL Editor to dramatically speed up the feed page.
-- Safe to run multiple times (CREATE INDEX IF NOT EXISTS).

-- 1. Speed up "Newest" sort (ORDER BY created_at DESC) + is_hidden filter
--    This is the most-used query path — every page load hits this.
CREATE INDEX IF NOT EXISTS idx_stories_created_at
  ON public.stories (created_at DESC)
  WHERE is_hidden = false;

-- 2. Speed up "Trending" sort (ORDER BY net_score DESC) + is_hidden filter
CREATE INDEX IF NOT EXISTS idx_stories_net_score
  ON public.stories (net_score DESC)
  WHERE is_hidden = false;

-- 3. Speed up author_username search (used in the feed search bar)
CREATE INDEX IF NOT EXISTS idx_stories_author_username
  ON public.stories (author_username text_pattern_ops);

-- 4. Speed up title search (used in the feed search bar)
CREATE INDEX IF NOT EXISTS idx_stories_title
  ON public.stories (title text_pattern_ops);

-- 5. Speed up "stories by this author" queries (used on profile pages)
CREATE INDEX IF NOT EXISTS idx_stories_author_id
  ON public.stories (author_id, created_at DESC);
