# Ongoing editorial publication

Run `python3 scratch/fictional-community/schedule.py` from this repository.
An empty array means no posting is due. Do nothing and stay quiet.

The 18 regular/frequent fictional writers have two or three slots each week,
rotated deterministically by writer and week in their existing local timezone.
Preferred hours and a varied minute are preserved. A six-hour heartbeat means
publication happens at the next check, not exactly at the planned minute.
Only slots in the preceding 12 hours are eligible; do not backfill older slots.
The configured start time excludes all historical slots.

Before drafting, query `sample_stories` for the returned `source_key` values
and read each author's most recent stories in the live database. Use the
existing public Supabase client credentials locally without printing them.
Skip slots already present. Publish at most five per run; let excess slots
expire rather than flooding the feed.

For each remaining slot, write a genuinely new fictional story matching its
style and interests. Use the returned examples for voice, never as a plot
template. Vary topic, narrator, pacing, length, and ending. Mostly use a single
block for a three-minute draft, with occasional natural paragraph breaks.
Use a few plausible typos or unfinished thoughts where that voice calls for
them; do not apply a standard typo pattern. Aim for 45–150 words usually,
with occasional 25–240-word pieces. Do not claim that the text records a real
person's writing session. Do not generate votes, followers, auth accounts,
real-user analytics, or leaderboard streaks.

Save an array of objects to a uniquely named JSON file in `/private/tmp`:
`source_key`, `title`, `starter_sentence`, `content`, and `time_mode` (1,2,3,5).
Export with:

    python3 scratch/fictional-community/schedule.py --batch /private/tmp/BATCH.json --output /private/tmp/POSTS.sql

Review the generated SQL. It must only insert into `sample_stories` and update
`sample_profiles` totals. The stable slot keys and UUIDs make retries safe;
the actual publication timestamp comes from database `now()`.

Apply through the already-authorized Supabase project's SQL Editor:
`https://supabase.com/dashboard/project/qugqybqvfhcoyotkuokb`.
Use an available scoped database connector if one is connected; otherwise use
the documented browser-control tool with the existing signed-in session.
Never obtain or expose admin credentials. For Monaco, use select-all and
clipboard paste, then select-all/copy and compare the full editor contents
with the intended SQL before Run selected. A textarea fill can leave old SQL.
Do not run any existing editor content without verifying it.

Verify the result rows and public `community_stories` view for every inserted
ID. On unknown result, query those IDs before retrying. If the session has
expired or the database cannot be reached, do not claim success or substitute
local-only files; report the concrete blocker once. Do not push a Git commit
for ordinary data-only posts. Collection rankings derive live from the same
tables and need no manual refresh or deployment.

Stop publishing when `schedule-config.json` has `enabled: false`.
Keep successful runs and no-op checks quiet. Notify only on actionable failure.
