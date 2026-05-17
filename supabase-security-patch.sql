-- 1. Remove dangerous UPDATE policy on daily_submissions
DROP POLICY IF EXISTS "Users can update votes on daily submissions" ON public.daily_submissions;

-- 2. Create secure RPC for daily submissions voting
CREATE OR REPLACE FUNCTION public.vote_daily_submission(
  p_submission_id UUID,
  p_user_id       UUID,
  p_direction     TEXT   -- 'up' | 'down' | 'none'
)
RETURNS JSON
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
  v_sub            daily_submissions%ROWTYPE;
  v_new_upvoters   UUID[];
  v_new_downvoters UUID[];
  v_new_net_score  INTEGER;
  v_score_delta    INTEGER := 0;
BEGIN
  IF auth.uid() IS NULL THEN RAISE EXCEPTION 'Not authenticated'; END IF;
  
  SELECT * INTO v_sub FROM daily_submissions WHERE id = p_submission_id;
  IF NOT FOUND THEN RAISE EXCEPTION 'Submission not found'; END IF;

  v_new_upvoters   := COALESCE(v_sub.upvoters, ARRAY[]::UUID[]);
  v_new_downvoters := COALESCE(v_sub.downvoters, ARRAY[]::UUID[]);

  IF p_user_id = ANY(v_new_upvoters) THEN v_score_delta := v_score_delta - 1; END IF;
  IF p_user_id = ANY(v_new_downvoters) THEN v_score_delta := v_score_delta + 1; END IF;

  v_new_upvoters   := array_remove(v_new_upvoters,   p_user_id);
  v_new_downvoters := array_remove(v_new_downvoters, p_user_id);

  IF p_direction = 'up' THEN
    v_new_upvoters  := array_append(v_new_upvoters, p_user_id);
    v_score_delta   := v_score_delta + 1;
  ELSIF p_direction = 'down' THEN
    v_new_downvoters := array_append(v_new_downvoters, p_user_id);
    v_score_delta    := v_score_delta - 1;
  END IF;

  v_new_net_score := COALESCE(array_length(v_new_upvoters, 1), 0) - COALESCE(array_length(v_new_downvoters, 1), 0);

  UPDATE daily_submissions
  SET upvoters = v_new_upvoters, downvoters = v_new_downvoters, net_score = v_new_net_score
  WHERE id = p_submission_id;

  IF v_score_delta <> 0 AND v_sub.author_id IS NOT NULL THEN
    UPDATE profiles
    SET total_upvotes_received = GREATEST(0, total_upvotes_received + v_score_delta),
        net_score = GREATEST(0, net_score + v_score_delta)
    WHERE id = v_sub.author_id;
    
    IF p_direction = 'up' AND p_user_id <> v_sub.author_id THEN
      INSERT INTO public.notifications (user_id, actor_id, type, reference_id)
      VALUES (v_sub.author_id, p_user_id, 'upvote', p_submission_id);
    END IF;
  END IF;

  RETURN json_build_object('upvoters', v_new_upvoters, 'downvoters', v_new_downvoters, 'net_score', v_new_net_score);
END;
$$;

REVOKE ALL ON FUNCTION public.vote_daily_submission(UUID, UUID, TEXT) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION public.vote_daily_submission(UUID, UUID, TEXT) TO authenticated;

-- 3. Fix notifications insert policy
DROP POLICY IF EXISTS "System can insert notifications" ON public.notifications;
-- (We don't need a public INSERT policy because RPC functions run with SECURITY DEFINER and bypass RLS)

-- 4. Fix daily prompts insert policy (Only service role or specific admins should insert prompts)
DROP POLICY IF EXISTS "Users can create daily prompt records" ON public.daily_prompts;
-- Let users read it, but upsert happens via RPC or service_role in Next.js API routes, 
-- or we can use an RPC for it.
