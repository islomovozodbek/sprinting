"""Add new fictional writers without rebuilding or backdating published history."""
import copy
import json
from pathlib import Path
import uuid
ROOT = Path(__file__).resolve().parent
NAMESPACE = uuid.UUID('117aac3b-8430-5ada-a88a-744b5232f8a9')

def profiles():
    rows = json.loads((ROOT / 'additional-writers.source.json').read_text())
    assert len(rows) == 30
    result = []
    for i, (username, name, voice, interests, zone) in enumerate(rows):
        cohort = 'regular' if i < 12 else 'frequent' if i < 15 else 'occasional' if i < 24 else 'never_wrote'
        result.append({
            'id': 'sample-writer-' + str(uuid.uuid5(NAMESPACE, 'writer:expansion-20261023:' + username)),
            'source_number': 121+i, 'username': username, 'display_name': name, 'bio': '',
            'avatar': {'kind':'initials','color':['#6b725b','#8a6357','#696481','#53717a'][i%4]},
            'is_synthetic': True, 'display_label': 'Fictional sample writer',
            'auth_account_created': False, 'include_in_real_metrics': False, 'leaderboard_eligible': False,
            'created_at':'2026-10-23T00:00:00Z',
            'habits': {'cohort':cohort,'cohort_label':{'regular':'Regular writer','frequent':'Frequent writer','occasional':'Occasional writer','never_wrote':'Registered, no writing'}[cohort],
                'intended_sessions_per_week': [2,3] if i<15 else [0,1] if i<24 else [0,0],
                'timezone_for_simulation':zone,'preferred_local_hours':[[7,9],[12,14],[19,22],[21,23]][i%4],
                'history_scope':'new_editorial_writer', 'schedule_note':'New voice; no backfilled stories. Scheduled publication only for regular/frequent writers.'},
            'writing_style': {'description':voice, 'recurring_interests':interests},
            'sample_stats':{'saved_sprints':0,'attempts':0,'retained_words':0,'mean_words':0,'min_words':0,'max_words':0,'last_writing_activity_at':None,'active_days':0}
        })
    assert len({p['writing_style']['description'] for p in result}) == 30
    return result

def extend(bundle):
    bundle = copy.deepcopy(bundle)
    added = profiles()
    old_ids = {p['id'] for p in bundle['profiles']}
    additions = [p for p in added if p['id'] not in old_ids]
    bundle['profiles'].extend(additions)
    assert len({p['username'].casefold() for p in bundle['profiles']}) == len(bundle['profiles'])
    bundle['summary']['profiles'] = len(bundle['profiles'])
    bundle['summary']['never_wrote'] += len(additions)
    for p in additions:
        key = p['habits']['cohort']
        bundle['summary']['cohorts'][key] = bundle['summary']['cohorts'].get(key, 0) + 1
    return bundle

if __name__ == '__main__':
    records = [{k:p[k] for k in ('username','display_name','bio')} | {'id':p['id'].removeprefix('sample-writer-'),'source_key':p['id']} for p in profiles()]
    payload = json.dumps(records,ensure_ascii=False)
    sql = '''-- Additive fictional profiles only. No auth accounts, votes, or backdated activity.
BEGIN;
SET LOCAL lock_timeout = '5s';
CREATE TEMP TABLE new_writers ON COMMIT DROP AS
SELECT * FROM jsonb_to_recordset($writers$PAYLOAD$writers$::jsonb)
AS x(id uuid, source_key text, username text, display_name text, bio text);
DO $$ BEGIN
 IF EXISTS (SELECT 1 FROM new_writers n JOIN public.profiles p ON lower(n.username)=lower(p.username)) THEN
 RAISE EXCEPTION 'Username collides with actual account'; END IF;
END $$;
INSERT INTO public.sample_profiles(id,source_key,username,display_name,bio,created_at)
SELECT id,source_key,username,display_name,bio,now() FROM new_writers
ON CONFLICT (id) DO NOTHING;
SELECT count(*) AS verified_new_profiles FROM public.community_profiles WHERE id IN (SELECT id FROM new_writers);
COMMIT;
'''.replace('PAYLOAD',payload)
    (ROOT / 'additional-writers.sql').write_text(sql)
    print('Exported 30 distinct fictional profiles; 15 eligible for recurring publication.')
