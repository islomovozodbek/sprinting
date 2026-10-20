-- Transactional test: no votes or user state survive this check.
BEGIN;
DO $$
DECLARE
  voter uuid;
  story uuid;
  response json;
  rejected boolean := false;
BEGIN
  IF has_table_privilege('anon', 'public.sample_profiles', 'INSERT')
     OR has_table_privilege('authenticated', 'public.sample_stories', 'UPDATE')
     OR has_function_privilege('anon', 'public.vote_sample_story(uuid,text)', 'EXECUTE') THEN
    RAISE EXCEPTION 'Unexpected public write permission';
  END IF;
  SELECT id INTO voter FROM public.profiles ORDER BY id LIMIT 1;
  SELECT id INTO story FROM public.sample_stories WHERE NOT is_hidden ORDER BY id LIMIT 1;
  IF voter IS NULL OR story IS NULL THEN RAISE EXCEPTION 'Missing test fixture'; END IF;
  PERFORM set_config('request.jwt.claim.sub', voter::text, true);

  response := public.vote_sample_story(story, 'up');
  IF NOT (response->'upvoters')::jsonb @> jsonb_build_array(voter::text) THEN
    RAISE EXCEPTION 'Upvote not recorded';
  END IF;
  response := public.vote_sample_story(story, 'up');
  IF (SELECT count(*) FROM json_array_elements_text(response->'upvoters') x WHERE x = voter::text) <> 1 THEN
    RAISE EXCEPTION 'Duplicate vote';
  END IF;
  response := public.vote_sample_story(story, 'down');
  IF (response->'upvoters')::jsonb @> jsonb_build_array(voter::text)
     OR NOT (response->'downvoters')::jsonb @> jsonb_build_array(voter::text) THEN
    RAISE EXCEPTION 'Vote direction switch failed';
  END IF;
  response := public.vote_sample_story(story, 'none');
  IF (response->'upvoters')::jsonb @> jsonb_build_array(voter::text)
     OR (response->'downvoters')::jsonb @> jsonb_build_array(voter::text) THEN
    RAISE EXCEPTION 'Vote removal failed';
  END IF;
  IF (response->>'net_score')::integer <>
     json_array_length(response->'upvoters') - json_array_length(response->'downvoters') THEN
    RAISE EXCEPTION 'Incorrect score';
  END IF;
  PERFORM set_config('request.jwt.claim.sub', '', true);
  BEGIN
    PERFORM public.vote_sample_story(story, 'up');
  EXCEPTION WHEN raise_exception THEN
    IF SQLERRM = 'Not authenticated' THEN rejected := true; ELSE RAISE; END IF;
  END;
  IF NOT rejected THEN RAISE EXCEPTION 'Unauthenticated vote accepted'; END IF;
END $$;
ROLLBACK;
SELECT 'passed; all test votes rolled back' AS voting_and_permissions;
