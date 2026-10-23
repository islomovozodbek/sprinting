#!/usr/bin/env python3
"""Build and validate a local, explicitly fictional community sample.

Run: python3 scratch/fictional-community/build.py
Uses only Python's standard library. No network, credentials, or database writes.
Prose is individually authored in *.prose.json; this script never rewrites it.
"""

import collections
from datetime import date, datetime, time, timedelta, timezone
import hashlib
import json
from pathlib import Path
import random
import re
import statistics
import uuid
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
SEED = 20261019
AS_OF = datetime(2026, 10, 19, 3, tzinfo=timezone.utc)
WINDOW_START = date(2026, 10, 5)
WINDOW_END = date(2026, 10, 18)
NAMESPACE = uuid.UUID("117aac3b-8430-5ada-a88a-744b5232f8a9")
ZONE_NAMES = ["Europe/London", "America/New_York", "Asia/Tashkent", "Australia/Perth"]
COLORS = ["#6b725b", "#8a6357", "#696481", "#53717a", "#876d43", "#896b7a"]
GROUPS = {
    "never_wrote": (24, "Registered, no writing", [0, 0]),
    "tried_and_left": (18, "Tried once or twice, then left", None),
    "early_burst": (18, "Short burst, then stopped", None),
    "occasional": (42, "Occasional writer", [1, 2]),
    "regular": (15, "Regular writer", [3, 4]),
    "frequent": (3, "Frequent writer", [5, 7]),
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def iso(value):
    return value.astimezone(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def stamp(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def ident(kind, value):
    return "sample-" + kind + "-" + str(uuid.uuid5(NAMESPACE, f"{kind}:{value}"))


def cohort(number):
    if number <= 24:
        return "never_wrote", 0
    if number <= 42:
        return "tried_and_left", 1 + (number - 25) % 2
    if number <= 60:
        return "early_burst", 3 + (number - 43) % 3
    if number <= 102:
        return "occasional", 2 + (number - 61) % 3
    if number <= 117:
        return "regular", [6, 7, 7, 8, 6][(number - 103) % 5]
    return "frequent", [10, 11, 12][number - 118]


def read_prompts():
    ordinary = (REPO / "src/data/prompts.js").read_text()
    pattern = r'\{\s*"id":\s*(\d+),\s*"text":\s*("(?:\\.|[^"\\])*")\s*\}'
    regular = {int(k): json.loads(v) for k, v in re.findall(pattern, ordinary)}
    daily_text = (REPO / "src/data/dailyPrompts.js").read_text()
    daily = {int(k): json.loads(v) for k, v in re.findall(
        r'\{\s*id:\s*"d(\d+)",\s*text:\s*("(?:\\.|[^"\\])*")\s*\}', daily_text
    )}
    require(len(regular) >= 500 and len(daily) == 100, "Prompt bank parsing failed")
    return regular, daily


def resolve_prompt(reference, banks):
    if reference.startswith("r:"):
        key = int(reference[2:])
        return {"source": "regular_bank", "id": key, "text": banks[0][key]}, "regular"
    if reference.startswith("d:"):
        key = int(reference[2:])
        # These are practice copies of prompts, not fabricated daily submissions.
        return {"source": "daily_bank_practice_copy", "id": f"d{key}", "text": banks[1][key]}, "custom"
    return {"source": "custom", "id": None, "text": reference}, "custom"


def activity_days(number, group, count, rng):
    if not count:
        return []
    if group == "tried_and_left":
        first = date(2026, 7, 23) + timedelta(days=rng.randrange(42))
        return [first + timedelta(days=0 if i == 0 or number % 3 else 1) for i in range(count)]
    if group == "early_burst":
        first = date(2026, 8, 1) + timedelta(days=rng.randrange(34))
        offsets = [0, 0, 1, 3, 5] if number % 2 else [0, 1, 2, 4, 6]
        return [first + timedelta(days=d) for d in offsets[:count]]
    if group == "occasional":
        # Some return after a gap, some miss a week, most have one or two days/week.
        if number % 7 == 0:
            offsets = sorted(rng.sample(range(7, 14), count))
        elif number % 11 == 0:
            offsets = [0, 13] if count == 2 else [0, 10, 13] if count == 3 else [0, 1, 11, 13]
        else:
            first_count = count // 2
            offsets = sorted(rng.sample(range(7), first_count) + rng.sample(range(7, 14), count - first_count))
    elif group == "regular":
        first_count = count // 2
        offsets = sorted(rng.sample(range(7), first_count) + rng.sample(range(7, 14), count - first_count))
    else:
        # Frequent is not daily: skip days and occasionally write twice in a day.
        offsets = sorted(rng.sample(range(14), count - 1))
        offsets.append(rng.choice(offsets))
        offsets.sort()
    return [WINDOW_START + timedelta(days=d) for d in offsets]


def build():
    source = json.loads((ROOT / "profiles.source.json").read_text())
    require(len(source["profiles"]) == 120, "Expected exactly 120 fictional profiles")
    prose = {}
    for path in sorted(ROOT.glob("*.prose.json")):
        for number, pieces in json.loads(path.read_text()):
            require(number not in prose, f"Duplicate author {number}")
            prose[number] = pieces
    require(set(prose) == set(range(25, 121)), "Missing or unexpected writing authors")
    banks = read_prompts()
    profiles, stories, sessions, events = [], [], [], []

    def event(kind, profile, when, session_id=None, story_id=None):
        events.append({
            "id": ident("event", f"{profile['id']}:{kind}:{iso(when)}:{session_id}"),
            "kind": kind, "profile_id": profile["id"], "occurred_at": iso(when),
            "session_id": session_id, "story_id": story_id,
            "is_synthetic": True, "include_in_real_metrics": False,
        })

    for number, row in enumerate(source["profiles"], 1):
        require(len(row) == len(source["columns"]), f"Profile column mismatch at {number}")
        config = dict(zip(source["columns"], row))
        # Changing a visible handle must not recreate the writer or their history.
        stable_key = config.get("stable_key", config["username"])
        group, expected_count = cohort(number)
        pieces = prose.get(number, [])
        require(len(pieces) == expected_count, f"Wrong piece count for profile {number}")
        rng = random.Random(SEED + number * 971)
        zone_name = ZONE_NAMES[(number * 7) % len(ZONE_NAMES)]
        zone = ZoneInfo(zone_name)
        days = activity_days(number, group, expected_count, rng)
        start_times = []
        for day in days:
            low, high = config["preferred_local_hours"]
            hour = rng.randint(low, high)
            # A few sessions fall outside the preferred band.
            if rng.random() < 0.14:
                hour = rng.randint(6, 23)
            when = datetime.combine(day, time(hour, rng.randrange(60), rng.randrange(60)), zone)
            if start_times and when <= start_times[-1] + timedelta(minutes=20):
                when = start_times[-1] + timedelta(minutes=rng.randint(28, 77))
            start_times.append(when)
        if start_times:
            registered = start_times[0] - timedelta(hours=rng.randint(2, 45), minutes=rng.randrange(60))
            if group in ("occasional", "regular", "frequent") and number % 4:
                registered -= timedelta(days=rng.randint(3, 22))
        else:
            registered = datetime(2026, 7, 21, 12, tzinfo=zone) + timedelta(days=rng.randrange(88), minutes=rng.randrange(600))
        profile = {
            "id": ident("writer", stable_key), "source_number": number,
            "username": config["username"], "display_name": config["display_name"],
            "bio": config["bio"], "avatar": {"kind": "initials", "color": COLORS[number % len(COLORS)]},
            "is_synthetic": True, "display_label": "Fictional sample writer",
            "auth_account_created": False, "include_in_real_metrics": False,
            "leaderboard_eligible": False, "created_at": iso(registered),
            "habits": {
                "cohort": group, "cohort_label": GROUPS[group][1],
                "intended_sessions_per_week": GROUPS[group][2],
                "timezone_for_simulation": zone_name,
                "preferred_local_hours": config["preferred_local_hours"],
                "history_scope": "complete_short_trial" if number <= 60 else "selected_14_day_window",
                "schedule_note": (
                    "Registered only; no writing attempts recorded." if not pieces else
                    "One or two early attempts; no return in the sample." if group == "tried_and_left" else
                    "Several early attempts close together, followed by inactivity." if group == "early_burst" else
                    "Return late in the window after a skipped week." if group == "occasional" and number % 7 == 0 else
                    "Early attempts, a long gap, then a return." if group == "occasional" and number % 11 == 0 else
                    "Uneven days and times; occasional same-day sessions." if group == "frequent" else
                    "Irregularly spaced sessions across the two-week window."
                ),
            },
            "writing_style": {"description": config["voice"], "recurring_interests": config["interests"]},
        }
        event("registered", profile, registered)
        authored, attempted = [], []
        for index, (piece, started) in enumerate(zip(pieces, start_times), 1):
            require(len(piece) == 4, f"Bad prose row {number}:{index}")
            title, reference, content, minutes = piece
            require(minutes in (1, 2, 3, 5, 30), "Unsupported timer")
            prompt, mode = resolve_prompt(reference, banks)
            story_id = ident("story", f"{stable_key}:{index}")
            session_id = ident("session", f"{stable_key}:{index}")
            timer_end = started + timedelta(minutes=minutes)
            saved = timer_end + timedelta(seconds=rng.randint(7, 105))
            word_count = len(content.split())  # Matches the website's whitespace count.
            hardcore = number % 9 == 0 and index % 3 == 0
            story = {
                "id": story_id, "author_id": profile["id"], "author_username": profile["username"],
                "title": title, "content": content, "word_count": word_count,
                "prompt": prompt, "starter_sentence": prompt["text"], "time_mode": minutes,
                "mode": mode, "is_hardcore": hardcore, "session_id": session_id,
                "created_at": iso(saved), "is_synthetic": True,
                "display_label": "Fictional sample sprint · AI-written",
                "include_in_real_metrics": False, "leaderboard_eligible": False,
                "provenance": "Original AI-written fiction; not an actual timed session or user submission.",
            }
            session = {
                "id": session_id, "profile_id": profile["id"], "story_id": story_id,
                "started_at": iso(started), "ended_at": iso(timer_end), "saved_at": iso(saved),
                "timer_minutes": minutes, "mode": mode, "is_hardcore": hardcore,
                "outcome": "saved", "retained_word_count": word_count,
                "is_synthetic": True, "include_in_real_metrics": False,
            }
            authored.append(story)
            attempted.append(session)
            event("sprint_started", profile, started, session_id)
            event("sprint_saved", profile, saved, session_id, story_id)
        # A small number of explicitly simulated failures. No text is invented for erased attempts.
        if number >= 61 and number % 5 == 0:
            preceding = start_times[0] - timedelta(minutes=rng.randint(25, 55))
            failure_id = ident("session", f"{stable_key}:unsaved")
            erased = number % 10 == 0
            ending = preceding + timedelta(seconds=rng.randint(25, 54))
            attempted.append({
                "id": failure_id, "profile_id": profile["id"], "story_id": None,
                "started_at": iso(preceding), "ended_at": iso(ending), "saved_at": None,
                "timer_minutes": 3, "mode": "regular", "is_hardcore": erased,
                "outcome": "erased_then_left" if erased else "abandoned",
                "retained_word_count": 0, "is_synthetic": True, "include_in_real_metrics": False,
            })
            event("sprint_started", profile, preceding, failure_id)
            event("sprint_erased_then_left" if erased else "sprint_abandoned", profile, ending, failure_id)
        own_words = [s["word_count"] for s in authored]
        profile["sample_stats"] = {
            "saved_sprints": len(authored), "attempts": len(attempted),
            "retained_words": sum(own_words),
            "mean_words": round(statistics.mean(own_words), 1) if own_words else 0,
            "min_words": min(own_words, default=0), "max_words": max(own_words, default=0),
            "last_writing_activity_at": max((s["ended_at"] for s in attempted), default=None),
            "active_days": len({stamp(s["started_at"]).astimezone(zone).date() for s in attempted}),
        }
        profiles.append(profile)
        stories.extend(authored)
        sessions.extend(attempted)

    all_words = [s["word_count"] for s in stories]
    active_ids = {s["profile_id"] for s in sessions if stamp(s["started_at"]) >= AS_OF - timedelta(days=30)}
    source_paths = [ROOT / "profiles.source.json", *sorted(ROOT.glob("*.prose.json"))]
    bundle = {
        "schema_version": 1,
        "metadata": {
            "title": "Sprinting Ink — fictional community sample", "is_synthetic": True,
            "display_label": "Fictional sample community — AI-written stories and simulated activity",
            "provenance": "All profiles, prose and activity histories are fictional. None represent real users or measured writing sessions.",
            "as_of": iso(AS_OF), "seed": SEED,
            "ongoing_activity_window": {"from_local_date": WINDOW_START.isoformat(), "through_local_date": WINDOW_END.isoformat()},
            "history_note": "Includes earlier complete trial histories and a detailed 14-day window for ongoing writers. Earlier activity for ongoing writers is outside this sample. Counts describe included records, not lifetime or actual site usage.",
            "length_note": "The requested 15–20-word reduction informed the shorter drafts. Individual lengths vary by writer and timer; this is not a fixed subtraction applied to every piece.",
            "deployment_status": "local_review_only",
            "include_in_real_metrics": False, "leaderboard_eligible": False,
            "daily_submissions_created": 0, "auth_accounts_created": 0,
            "integration_note": "Keep provenance in the internal collection metadata. IDs deliberately use a sample prefix and are not valid Supabase auth-user IDs. Do not include sample records in real user counts, votes or leaderboards.",
            "source_sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in source_paths},
        },
        "summary": {
            "profiles": len(profiles), "writers_with_saved_text": len(prose),
            "never_wrote": sum(p["sample_stats"]["saved_sprints"] == 0 for p in profiles),
            "saved_sprints": len(stories), "sessions": len(sessions), "events": len(events),
            "simulated_active_writers_last_30_days": len(active_ids),
            "word_count": {"total": sum(all_words), "mean": round(statistics.mean(all_words), 1),
                           "median": statistics.median(all_words), "min": min(all_words), "max": max(all_words)},
            "cohorts": dict(collections.Counter(p["habits"]["cohort"] for p in profiles)),
            "timers": dict(sorted(collections.Counter(s["time_mode"] for s in stories).items())),
            "word_count_by_timer": {
                str(minutes): {
                    "min": min(words), "median": statistics.median(words),
                    "mean": round(statistics.mean(words), 1), "max": max(words),
                }
                for minutes in sorted({s["time_mode"] for s in stories})
                for words in [[s["word_count"] for s in stories if s["time_mode"] == minutes]]
            },
            "paragraph_counts": dict(sorted(collections.Counter(
                len(re.split(r"\n\s*\n", s["content"].strip())) for s in stories
            ).items())),
            "single_block_sprints": sum("\n" not in s["content"] for s in stories),
            "outcomes": dict(collections.Counter(s["outcome"] for s in sessions)),
        },
        "profiles": profiles, "stories": sorted(stories, key=lambda s: (s["created_at"], s["id"])),
        "sessions": sorted(sessions, key=lambda s: (s["started_at"], s["id"])),
        "activity": sorted(events, key=lambda e: (e["occurred_at"], e["id"])),
    }
    validate(bundle)
    return bundle


def validate(bundle):
    profiles = {p["id"]: p for p in bundle["profiles"]}
    stories = {s["id"]: s for s in bundle["stories"]}
    sessions = {s["id"]: s for s in bundle["sessions"]}
    require(len(profiles) == len(bundle["profiles"]) == 120, "Profile count/ID mismatch")
    require(len({p["username"].casefold() for p in profiles.values()}) == 120, "Duplicate username")
    require(all(re.fullmatch(r"[a-zA-Z0-9_]{3,}", p["username"]) for p in profiles.values()), "Invalid username")
    require(len(stories) == len(bundle["stories"]) == 360, "Story count/ID mismatch")
    require(len(sessions) == len(bundle["sessions"]), "Duplicate session ID")
    require(len({e["id"] for e in bundle["activity"]}) == len(bundle["activity"]), "Duplicate activity ID")
    require(bundle["summary"]["simulated_active_writers_last_30_days"] == 60, "Expected 60 ongoing sample writers")
    require(bundle["summary"]["cohorts"] == {k: v[0] for k, v in GROUPS.items()}, "Cohort mismatch")
    normalised = [re.sub(r"\W+", " ", s["content"].lower()).strip() for s in stories.values()]
    require(len(set(normalised)) == len(stories), "Duplicate story text")
    for s in stories.values():
        require(s["author_id"] in profiles and s["session_id"] in sessions, "Broken story reference")
        require(s["word_count"] == len(s["content"].split()), "Word count mismatch")
        require(bool(s["title"].strip()) and bool(s["prompt"]["text"].strip()), "Missing title/prompt")
        require(s["author_username"] == profiles[s["author_id"]]["username"], "Author mismatch")
    for profile_id, p in profiles.items():
        own = [s for s in stories.values() if s["author_id"] == profile_id]
        own_sessions = sorted((s for s in sessions.values() if s["profile_id"] == profile_id), key=lambda s: s["started_at"])
        require(p["sample_stats"]["saved_sprints"] == len(own), "Profile story count mismatch")
        require(p["sample_stats"]["retained_words"] == sum(s["word_count"] for s in own), "Profile word count mismatch")
        require(p["sample_stats"]["attempts"] == len(own_sessions), "Attempt count mismatch")
        require(stamp(p["created_at"]) <= AS_OF, "Future registration")
        for current, following in zip(own_sessions, own_sessions[1:]):
            end = current["saved_at"] or current["ended_at"]
            require(stamp(end) < stamp(following["started_at"]), "Overlapping author sessions")
        for session in own_sessions:
            start, end = stamp(session["started_at"]), stamp(session["ended_at"])
            require(stamp(p["created_at"]) <= start < end <= AS_OF, "Invalid session chronology")
            if session["outcome"] == "saved":
                require(end - start == timedelta(minutes=session["timer_minutes"]), "Timer duration mismatch")
                saved = stamp(session["saved_at"])
                require(end <= saved <= AS_OF, "Invalid saved timestamp")
                story = stories[session["story_id"]]
                require(story["session_id"] == session["id"] and story["author_id"] == profile_id, "Session/story mismatch")
                require(story["created_at"] == session["saved_at"], "Story date mismatch")
            else:
                require(session["story_id"] is None and session["retained_word_count"] == 0, "Unsaved text leak")
    for e in bundle["activity"]:
        require(e["profile_id"] in profiles and stamp(e["occurred_at"]) <= AS_OF, "Invalid activity reference/date")
        if e["session_id"]:
            require(sessions[e["session_id"]]["profile_id"] == e["profile_id"], "Activity author mismatch")
        if e["story_id"]:
            require(stories[e["story_id"]]["author_id"] == e["profile_id"], "Activity story mismatch")
    for collection in (bundle["profiles"], bundle["stories"], bundle["sessions"], bundle["activity"]):
        require(all(x["is_synthetic"] and x["include_in_real_metrics"] is False for x in collection), "Missing synthetic/metric marker")


def preview(bundle):
    template = (ROOT / "preview.template.html").read_text()
    embedded = json.dumps(bundle, ensure_ascii=False).replace("<", "\\u003c").replace("\u2028", "\\u2028").replace("\u2029", "\\u2029")
    return template.replace("__COMMUNITY_JSON__", embedded)


if __name__ == "__main__":
    from additional_writers import extend
    bundle = extend(build())
    (ROOT / "community.json").write_text(json.dumps(bundle, indent=2, ensure_ascii=False) + "\n")
    (ROOT / "preview.html").write_text(preview(bundle))
    report = {"validation": "passed", "summary": bundle["summary"], "deployment_status": "local_review_only",
              "checks": ["150 unique profiles", "390 unique prose bodies", "126 writing profiles and 24 profiles without saved text",
                         "case-insensitive unique handles matching signup format",
                         "30 initial editorial sprints with unique writers and publication events", "cohort allocations",
                         "all author/session/story links", "no future dates or overlapping sessions",
                         "registration precedes activity", "timer and save chronology", "word counts and totals",
                         "synthetic markers and real-metric exclusion on every record"],
              "rebuild": "python3 scratch/fictional-community/build.py"}
    (ROOT / "validation-report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
