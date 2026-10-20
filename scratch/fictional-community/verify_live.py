#!/usr/bin/env python3
"""Verify the public data path using the site's existing anonymous API key."""
import json
from pathlib import Path
import re
from urllib.error import HTTPError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
env = {}
for line in (REPO / ".env.local").read_text().splitlines():
    match = re.match(r"([A-Z_]+)=(.*)", line)
    if match:
        env[match[1]] = match[2].strip().strip("'\"")
url = env["NEXT_PUBLIC_SUPABASE_URL"].rstrip("/")
assert url == "https://qugqybqvfhcoyotkuokb.supabase.co", "Unexpected project"
key = env["NEXT_PUBLIC_SUPABASE_ANON_KEY"]


def request(path, payload=None):
    headers = {"apikey": key, "Authorization": f"Bearer {key}"}
    body = None
    if payload is not None:
        headers["Content-Type"] = "application/json"
        body = json.dumps(payload).encode()
    with urlopen(Request(f"{url}/rest/v1/{path}", data=body, headers=headers), timeout=30) as response:
        return json.load(response)


profiles = request("community_profiles?is_synthetic=eq.true&select=id,username,display_name,total_stories")
stories = request("community_stories?is_synthetic=eq.true&select=id,author_id,author_username,content,word_count,is_hidden")
expected = json.loads((ROOT / "community.json").read_text())
assert len(profiles) == 120 and len(stories) == 360
profile_map = {p["id"]: p for p in profiles}
expected_profiles = {p["id"].removeprefix("sample-writer-"): p for p in expected["profiles"]}
expected_stories = {s["id"].removeprefix("sample-story-"): s for s in expected["stories"]}
assert set(profile_map) == set(expected_profiles)
assert {s["id"] for s in stories} == set(expected_stories)
for p in profiles:
    assert p["username"] == expected_profiles[p["id"]]["username"]
    assert p["display_name"] == expected_profiles[p["id"]]["display_name"]
    assert p["total_stories"] == sum(s["author_id"] == p["id"] for s in stories)
for s in stories:
    assert s["content"] == expected_stories[s["id"]]["content"]
    assert s["word_count"] == len(s["content"].split())
    assert s["author_username"] == profile_map[s["author_id"]]["username"]
    assert s["is_hidden"] is False
assert request("community_stories?is_hidden=eq.true&select=id") == []
real_profiles = request("profiles?select=id")
real_stories = request("stories?select=id")
assert not set(profile_map) & {p["id"] for p in real_profiles}
assert not set(expected_stories) & {s["id"] for s in real_stories}
try:
    request("rpc/vote_sample_story", {"p_story_id": stories[0]["id"], "p_direction": "up"})
    raise AssertionError("Anonymous vote unexpectedly accepted")
except HTTPError as error:
    assert error.code in (401, 403), f"Unexpected vote rejection: {error.code}"
print(json.dumps({
    "result": "passed", "public_profiles": len(profiles), "public_stories": len(stories),
    "original_profiles": len(real_profiles), "original_stories": len(real_stories),
    "all_content_and_links_match": True, "hidden_stories_excluded": True,
    "anonymous_voting_blocked": True, "real_user_tables_separate": True,
}, indent=2))
