#!/usr/bin/env python3
"""Export an idempotent import; does not execute SQL or access credentials."""
import json
from pathlib import Path
import uuid

ROOT = Path(__file__).resolve().parent
data = json.loads((ROOT / "community.json").read_text())


def record_id(value, kind):
    return str(uuid.UUID(value.removeprefix(f"sample-{kind}-")))


profiles = [{
    "id": record_id(p["id"], "writer"), "source_key": p["id"],
    "username": p["username"], "display_name": p["display_name"], "bio": p["bio"],
    "created_at": p["created_at"], "total_stories": p["sample_stats"]["saved_sprints"],
    "total_words": p["sample_stats"]["retained_words"],
} for p in data["profiles"]]
stories = [{
    "id": record_id(s["id"], "story"), "source_key": s["id"],
    "author_id": record_id(s["author_id"], "writer"),
    **{key: s[key] for key in (
        "title", "content", "starter_sentence", "word_count", "time_mode",
        "mode", "is_hardcore", "created_at"
    )},
} for s in data["stories"]]
assert len(profiles) == 150 and len(stories) == 390

sql = ["-- Run supabase-community.sql first. This import touches only sample tables.",
       "-- Re-running updates editorial content without resetting votes or visibility.",
       "BEGIN;", "SET LOCAL lock_timeout = '5s';"]

for table, records, columns in [
    ("sample_profiles", profiles, {
        "id": "uuid", "source_key": "text", "username": "text", "display_name": "text",
        "bio": "text", "created_at": "timestamptz", "total_stories": "integer", "total_words": "integer",
    }),
    ("sample_stories", stories, {
        "id": "uuid", "source_key": "text", "author_id": "uuid", "title": "text",
        "content": "text", "starter_sentence": "text", "word_count": "integer",
        "time_mode": "integer", "mode": "text", "is_hardcore": "boolean", "created_at": "timestamptz",
    }),
]:
    encoded = json.dumps(records, ensure_ascii=False, separators=(",", ":"))
    assert "$collection$" not in encoded
    names = ", ".join(columns)
    shape = ", ".join(f"{name} {kind}" for name, kind in columns.items())
    updates = ", ".join(f"{name} = EXCLUDED.{name}" for name in columns if name not in ("id", "source_key"))
    sql.append(f"INSERT INTO public.{table} ({names})\nSELECT {names} FROM jsonb_to_recordset("
               f"$collection${encoded}$collection$::jsonb) AS imported({shape})\n"
               f"ON CONFLICT (id) DO UPDATE SET {updates};")

sql.extend([
    "UPDATE public.sample_profiles p SET total_stories = (SELECT count(*) FROM public.sample_stories s WHERE s.author_id=p.id AND NOT s.is_hidden), total_words = (SELECT coalesce(sum(word_count),0) FROM public.sample_stories s WHERE s.author_id=p.id AND NOT s.is_hidden);",
    """DO $$ BEGIN
  IF EXISTS (SELECT 1 FROM public.sample_profiles s JOIN public.profiles r
             ON lower(s.username) = lower(r.username)) THEN
    RAISE EXCEPTION 'A sample handle conflicts with an existing account; import rolled back';
  END IF;
  IF (SELECT count(*) FROM public.sample_profiles) < 150 OR
     (SELECT count(*) FROM public.sample_stories) < 390 THEN
    RAISE EXCEPTION 'Unexpected collection counts; import rolled back';
  END IF;
END $$;""",
    "COMMIT;",
    "SELECT (SELECT count(*) FROM public.sample_profiles) AS imported_profiles,"
    " (SELECT count(*) FROM public.sample_stories) AS imported_stories,"
    " (SELECT count(*) FROM public.profiles) AS real_profiles,"
    " (SELECT count(*) FROM public.stories) AS real_stories;",
])
(ROOT / "import.sql").write_text("\n\n".join(sql) + "\n")
print(f"Exported {len(profiles)} profiles and {len(stories)} stories.")
