#!/usr/bin/env python3
"""Plan editorial posts and export validated, retry-safe publication SQL."""
import argparse
from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import uuid
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent
UTC = timezone.utc


def number(value):
    return int(hashlib.sha256(value.encode()).hexdigest()[:12], 16)


def slots(bundle, now, starts_at):
    """Return recent slots only; missed days never cause a catch-up flood."""
    result = []
    for profile in bundle["profiles"]:
        habits = profile["habits"]
        if habits["cohort"] not in ("regular", "frequent"):
            continue
        zone = ZoneInfo(habits["timezone_for_simulation"])
        local = now.astimezone(zone)
        for offset in range(2):
            day = local.date() - timedelta(days=offset)
            week = day - timedelta(days=day.weekday())
            seed = f"{profile['id']}:{week}"
            count = 3 if habits["cohort"] == "frequent" else 2 + number(seed) % 2
            weekdays = sorted(range(7), key=lambda d: number(f"{seed}:{d}"))[:count]
            if day.weekday() not in weekdays:
                continue
            hours = habits["preferred_local_hours"]
            hour = hours[number(f"{seed}:{day}:hour") % len(hours)]
            minute = number(f"{seed}:{day}:minute") % 60
            planned = datetime(day.year, day.month, day.day, hour, minute, tzinfo=zone).astimezone(UTC)
            if not max(starts_at, now - timedelta(hours=12)) <= planned <= now:
                continue
            source_key = f"scheduled:{profile['username']}:{day}"
            examples = [s for s in bundle["stories"] if s["author_id"] == profile["id"]][-3:]
            result.append({
                "id": str(uuid.uuid5(uuid.NAMESPACE_URL, source_key)),
                "source_key": source_key,
                "author_id": profile["id"].removeprefix("sample-writer-"),
                "username": profile["username"],
                "scheduled_at": planned.isoformat(),
                "style": profile["writing_style"],
                "examples": [{"title": s["title"], "content": s["content"], "time_mode": s["time_mode"]} for s in examples],
            })
    return sorted(result, key=lambda item: item["scheduled_at"])


def export(batch, due, bundle):
    eligible = {item["source_key"]: item for item in due}
    existing_texts = {s["content"].strip().casefold() for s in bundle["stories"]}
    seen = set()
    assert len(batch) <= 5, "Maximum five posts per run; skip excess slots instead of flooding"
    rows = []
    for story in batch:
        slot = eligible[story["source_key"]]
        assert slot["source_key"] not in seen, "Duplicate slot"
        seen.add(slot["source_key"])
        content = story["content"].strip()
        assert content.casefold() not in existing_texts, "Repeated prose"
        existing_texts.add(content.casefold())
        words = len(content.split())
        assert 25 <= words <= 240, "Expected 25–240 words"
        assert story["time_mode"] in (1, 2, 3, 5)
        assert 1 <= len(story["title"].strip()) <= 140
        assert 5 <= len(story["starter_sentence"].strip()) <= 300
        rows.append({key: slot[key] for key in ("id", "source_key", "author_id")} | {
            "title": story["title"].strip(), "content": content,
            "starter_sentence": story["starter_sentence"].strip(),
            "time_mode": story["time_mode"], "word_count": words,
        })
    payload = json.dumps(rows, ensure_ascii=False)
    assert "$posts$" not in payload
    return f"""-- Editorial publication only. Idempotent slots; real accounts untouched.
BEGIN;
SET LOCAL lock_timeout = '5s';
SELECT pg_advisory_xact_lock(61708104);
INSERT INTO public.sample_stories
  (id, source_key, author_id, title, content, starter_sentence, time_mode, word_count, mode, created_at, provenance)
SELECT r.id, r.source_key, r.author_id, r.title, r.content, r.starter_sentence,
       r.time_mode, r.word_count, 'normal', now(),
       'AI-written editorial fiction; created_at is the actual publication time.'
FROM jsonb_to_recordset($posts${payload}$posts$::jsonb) AS r(
  id uuid, source_key text, author_id uuid, title text, content text,
  starter_sentence text, time_mode integer, word_count integer)
JOIN public.sample_profiles p ON p.id = r.author_id AND p.published
WHERE NOT EXISTS (SELECT 1 FROM public.sample_stories s WHERE lower(trim(s.content)) = lower(trim(r.content)))
ON CONFLICT DO NOTHING;
UPDATE public.sample_profiles p SET
  total_stories = (SELECT count(*) FROM public.sample_stories s WHERE s.author_id = p.id AND NOT s.is_hidden),
  total_words = (SELECT coalesce(sum(word_count), 0) FROM public.sample_stories s WHERE s.author_id = p.id AND NOT s.is_hidden);
COMMIT;
SELECT source_key, id, title, created_at FROM public.sample_stories
WHERE source_key IN (SELECT value->>'source_key' FROM jsonb_array_elements($posts${payload}$posts$::jsonb));
"""


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--now", help="ISO timestamp for deterministic testing")
    parser.add_argument("--batch", type=Path, help="Export a JSON array of drafted stories")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    now = datetime.fromisoformat(args.now) if args.now else datetime.now(UTC)
    assert now.tzinfo is not None
    config = json.loads((ROOT / "schedule-config.json").read_text())
    bundle = json.loads((ROOT / "community.json").read_text())
    due = slots(bundle, now, datetime.fromisoformat(config["starts_at"])) if config["enabled"] else []
    if args.batch:
        assert args.output
        args.output.write_text(export(json.loads(args.batch.read_text()), due, bundle))
        print(f"Validated publication SQL: {args.output}")
    else:
        print(json.dumps(due, ensure_ascii=False, indent=2))
