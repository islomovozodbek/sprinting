-- Reversible moderation of the one post identified in the user's screenshot.
-- Run in this project's Supabase SQL Editor with an administrator account.
-- Does not delete the story, its author, or any other posts.
BEGIN;
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM public.stories
    WHERE id = 'e238f6ab-00d1-4359-a9a8-dcc2441b368b'::uuid
      AND author_username = 'tester444'
      AND starter_sentence = 'The vending machine gave me something that wasn''t food…'
  ) THEN
    RAISE EXCEPTION 'Expected story not found; no change applied';
  END IF;
END $$;

UPDATE public.stories
SET is_hidden = true
WHERE id = 'e238f6ab-00d1-4359-a9a8-dcc2441b368b'::uuid
  AND author_username = 'tester444'
RETURNING id, author_username, is_hidden;
COMMIT;

-- Verify (expected true):
SELECT id, is_hidden FROM public.stories
WHERE id = 'e238f6ab-00d1-4359-a9a8-dcc2441b368b'::uuid;

-- Undo if needed:
-- UPDATE public.stories SET is_hidden = false
-- WHERE id = 'e238f6ab-00d1-4359-a9a8-dcc2441b368b'::uuid;
