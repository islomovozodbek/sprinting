-- Live totals from visible editorial stories; no simulated votes or streaks.
BEGIN;
CREATE OR REPLACE VIEW public.collection_rankings WITH (security_invoker = true) AS
SELECT p.id, p.username, 'derby'::text AS profile_color,
       count(s.id)::integer AS total_stories,
       coalesce(sum(cardinality(s.upvoters)), 0)::integer AS total_upvotes_received
FROM public.sample_profiles p
JOIN public.sample_stories s ON s.author_id = p.id AND NOT s.is_hidden
WHERE p.published AND NOT EXISTS (
  SELECT 1 FROM public.profiles r WHERE lower(r.username) = lower(p.username)
)
GROUP BY p.id, p.username;
GRANT SELECT ON public.collection_rankings TO anon, authenticated;
NOTIFY pgrst, 'reload schema';
COMMIT;
SELECT username, total_stories, total_upvotes_received
FROM public.collection_rankings ORDER BY total_stories DESC, username LIMIT 5;
