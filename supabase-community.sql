-- Additive, reversible publication of the editorial collection.
-- Login accounts, real-user statistics, and leaderboards remain in existing tables.
BEGIN;

CREATE TABLE IF NOT EXISTS public.sample_profiles (
  id uuid PRIMARY KEY,
  source_key text UNIQUE NOT NULL,
  username text UNIQUE NOT NULL,
  display_name text NOT NULL,
  bio text NOT NULL DEFAULT '',
  created_at timestamptz NOT NULL,
  total_stories integer NOT NULL DEFAULT 0,
  total_words integer NOT NULL DEFAULT 0,
  published boolean NOT NULL DEFAULT true,
  is_synthetic boolean NOT NULL DEFAULT true CHECK (is_synthetic),
  include_in_real_metrics boolean NOT NULL DEFAULT false CHECK (NOT include_in_real_metrics),
  provenance text NOT NULL DEFAULT 'Fictional editorial profile; no login account.'
);

CREATE TABLE IF NOT EXISTS public.sample_stories (
  id uuid PRIMARY KEY,
  source_key text UNIQUE NOT NULL,
  author_id uuid NOT NULL REFERENCES public.sample_profiles(id),
  title text NOT NULL,
  content text NOT NULL,
  starter_sentence text NOT NULL,
  word_count integer NOT NULL CHECK (word_count > 0),
  time_mode integer NOT NULL CHECK (time_mode IN (1, 2, 3, 5, 30)),
  mode text NOT NULL,
  is_hardcore boolean NOT NULL DEFAULT false,
  created_at timestamptz NOT NULL,
  net_score integer NOT NULL DEFAULT 0,
  upvoters uuid[] NOT NULL DEFAULT '{}',
  downvoters uuid[] NOT NULL DEFAULT '{}',
  is_hidden boolean NOT NULL DEFAULT false,
  is_synthetic boolean NOT NULL DEFAULT true CHECK (is_synthetic),
  include_in_real_metrics boolean NOT NULL DEFAULT false CHECK (NOT include_in_real_metrics),
  provenance text NOT NULL DEFAULT 'AI-written fiction; timestamp represents a simulated writing session.'
);

CREATE INDEX IF NOT EXISTS sample_stories_created_idx ON public.sample_stories(created_at DESC, id);
CREATE INDEX IF NOT EXISTS sample_stories_author_idx ON public.sample_stories(author_id);

ALTER TABLE public.sample_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.sample_stories ENABLE ROW LEVEL SECURITY;
REVOKE ALL ON public.sample_profiles, public.sample_stories FROM anon, authenticated;
GRANT SELECT ON public.sample_profiles, public.sample_stories TO anon, authenticated;

DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE schemaname = 'public' AND tablename = 'sample_profiles' AND policyname = 'Read published editorial profiles') THEN
    CREATE POLICY "Read published editorial profiles" ON public.sample_profiles
      FOR SELECT TO anon, authenticated USING (published);
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE schemaname = 'public' AND tablename = 'sample_stories' AND policyname = 'Read visible editorial stories') THEN
    CREATE POLICY "Read visible editorial stories" ON public.sample_stories
      FOR SELECT TO anon, authenticated USING (NOT is_hidden AND EXISTS (
        SELECT 1 FROM public.sample_profiles p WHERE p.id = author_id AND p.published
      ));
  END IF;
END $$;

-- Invoker views retain each underlying table's row-level security.
-- If a real account later takes a matching handle, it takes precedence.
CREATE OR REPLACE VIEW public.community_profiles WITH (security_invoker = true) AS
SELECT id, username, display_name, bio, photo_url, created_at,
       total_stories, total_words, followers_count, following_count,
       current_streak, level, aura, is_og, profile_color, total_upvotes_received,
       false AS is_synthetic
FROM public.profiles
UNION ALL
SELECT p.id, p.username, p.display_name, p.bio, NULL::text, p.created_at,
       p.total_stories, p.total_words, 0, 0, 0, 1, 0, false, 'derby'::text, 0, true
FROM public.sample_profiles p
WHERE p.published AND NOT EXISTS (
  SELECT 1 FROM public.profiles real WHERE lower(real.username) = lower(p.username)
);

CREATE OR REPLACE VIEW public.community_stories WITH (security_invoker = true) AS
SELECT id, author_id, author_username, title, content, starter_sentence,
       word_count, time_mode, created_at, net_score, upvoters, downvoters,
       is_hidden, false AS is_synthetic
FROM public.stories WHERE NOT is_hidden
UNION ALL
SELECT s.id, s.author_id, p.username, s.title, s.content, s.starter_sentence,
       s.word_count, s.time_mode, s.created_at, s.net_score, s.upvoters, s.downvoters,
       s.is_hidden, true
FROM public.sample_stories s JOIN public.sample_profiles p ON p.id = s.author_id
WHERE NOT s.is_hidden AND p.published AND NOT EXISTS (
  SELECT 1 FROM public.profiles real WHERE lower(real.username) = lower(p.username)
);

REVOKE ALL ON public.community_profiles, public.community_stories FROM anon, authenticated;
GRANT SELECT ON public.community_profiles, public.community_stories TO anon, authenticated;

-- Only signed-in readers can call this voting RPC. No author rewards.
-- Owner-requested fictional reactions are separately recorded in seeded-reactions.json.
CREATE OR REPLACE FUNCTION public.vote_sample_story(p_story_id uuid, p_direction text)
RETURNS json
LANGUAGE plpgsql SECURITY DEFINER SET search_path = public
AS $$
DECLARE
  voter uuid := auth.uid();
  item public.sample_stories%ROWTYPE;
BEGIN
  IF voter IS NULL THEN RAISE EXCEPTION 'Not authenticated'; END IF;
  IF p_direction IS NULL OR p_direction NOT IN ('up', 'down', 'none') THEN
    RAISE EXCEPTION 'Invalid vote direction';
  END IF;
  SELECT s.* INTO item FROM public.sample_stories s
  JOIN public.sample_profiles p ON p.id = s.author_id
  WHERE s.id = p_story_id AND NOT s.is_hidden AND p.published
    AND NOT EXISTS (SELECT 1 FROM public.profiles r WHERE lower(r.username) = lower(p.username))
  FOR UPDATE OF s;
  IF NOT FOUND THEN RAISE EXCEPTION 'Story not found'; END IF;
  item.upvoters := array_remove(item.upvoters, voter);
  item.downvoters := array_remove(item.downvoters, voter);
  IF p_direction = 'up' THEN item.upvoters := array_append(item.upvoters, voter); END IF;
  IF p_direction = 'down' THEN item.downvoters := array_append(item.downvoters, voter); END IF;
  item.net_score := cardinality(item.upvoters) - cardinality(item.downvoters);
  UPDATE public.sample_stories SET upvoters = item.upvoters,
    downvoters = item.downvoters, net_score = item.net_score WHERE id = item.id;
  RETURN json_build_object('upvoters', item.upvoters, 'downvoters', item.downvoters, 'net_score', item.net_score);
END $$;
REVOKE ALL ON FUNCTION public.vote_sample_story(uuid, text) FROM PUBLIC, anon;
GRANT EXECUTE ON FUNCTION public.vote_sample_story(uuid, text) TO authenticated;

NOTIFY pgrst, 'reload schema';
COMMIT;
