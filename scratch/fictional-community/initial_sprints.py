"""Validate/export the 30 initial editorial sprints; no database credentials."""
import collections
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import re
import statistics
import uuid
ROOT = Path(__file__).resolve().parent
NAMESPACE = uuid.UUID('117aac3b-8430-5ada-a88a-744b5232f8a9')


def records():
    from additional_writers import profiles
    authors = {p['username']:p for p in profiles()}
    source = json.loads((ROOT/'initial-sprints.source.json').read_text())
    publication = json.loads((ROOT/'initial-sprints.publication.json').read_text())
    assert len(source) == 30 and {s['username'] for s in source} == set(authors)
    assert len({s['content'].strip().casefold() for s in source}) == 30
    result = []
    for s in source:
        p = authors[s['username']]
        sid = str(uuid.uuid5(NAMESPACE, 'initial-sprint-20261023:' + s['username']))
        words = len(s['content'].split())
        assert 25 <= words <= 240 and s['time_mode'] in (1,2,3,5)
        assert s['title'].strip() and s['starter_sentence'].strip()
        result.append({
            'id':'sample-story-'+sid,'author_id':p['id'],'author_username':p['username'],
            **{k:s[k] for k in ('title','content','starter_sentence','time_mode')},
            'word_count':words, 'mode':'custom','is_hardcore':False,'session_id':None,
            'prompt':{'source':'custom','id':None,'text':s['starter_sentence']},
            'created_at':publication.get('published_at',{}).get(sid,publication['prepared_at']),
            'is_synthetic':True,'include_in_real_metrics':False,'leaderboard_eligible':False,
            'display_label':'Fictional sample sprint · AI-written',
            'provenance':'Original AI-written fiction. Publication time, not an actual timed session.'
        })
    return result


def extend_initial(bundle):
    initial = records()
    existing = {s['id']:s for s in bundle['stories']}
    for s in initial:
        if s['id'] in existing:
            assert existing[s['id']]['content'] == s['content'], 'Unexpected changed initial story'
        else:
            bundle['stories'].append(s)
    assert len({s['id'] for s in bundle['stories']}) == len(bundle['stories'])
    assert len({re.sub(r'\W+',' ',s['content'].lower()).strip() for s in bundle['stories']}) == len(bundle['stories'])
    authors = {p['id']:p for p in bundle['profiles']}
    for s in initial:
        p = authors[s['author_id']]
        own = [x for x in bundle['stories'] if x['author_id']==p['id']]
        words = [x['word_count'] for x in own]
        p['sample_stats'].update(saved_sprints=len(own),retained_words=sum(words),mean_words=round(statistics.mean(words),1),min_words=min(words),max_words=max(words),last_writing_activity_at=max(x['created_at'] for x in own),active_days=len({x['created_at'][:10] for x in own}))
        if p['habits']['cohort']=='never_wrote':
            p['habits'].update(cohort='tried_and_left',cohort_label='Tried once or twice, then left')
        p['habits']['schedule_note']='Initial editorial sprint published; recurring schedule applies only to regular/frequent writers.'
        eid='sample-event-'+str(uuid.uuid5(NAMESPACE,'initial-publication:'+s['id']))
        if not any(e['id']==eid for e in bundle['activity']):
            bundle['activity'].append({'id':eid,'kind':'editorial_published','profile_id':p['id'],'occurred_at':s['created_at'],'session_id':None,'story_id':s['id'],'is_synthetic':True,'include_in_real_metrics':False})
    bundle['stories'].sort(key=lambda s:(s['created_at'],s['id']))
    bundle['activity'].sort(key=lambda e:(e['occurred_at'],e['id']))
    summary=bundle['summary']; stories=bundle['stories']; words=[s['word_count'] for s in stories]
    latest=max(s['created_at'] for s in stories)
    cutoff=datetime.fromisoformat(latest.replace('Z','+00:00'))-timedelta(days=30)
    summary.update(saved_sprints=len(stories),events=len(bundle['activity']),writers_with_saved_text=len({s['author_id'] for s in stories}),never_wrote=sum(p['sample_stats']['saved_sprints']==0 for p in bundle['profiles']),simulated_active_writers_last_30_days=len({s['author_id'] for s in stories if datetime.fromisoformat(s['created_at'].replace('Z','+00:00'))>=cutoff}),cohorts=dict(collections.Counter(p['habits']['cohort'] for p in bundle['profiles'])),word_count={'total':sum(words),'mean':round(statistics.mean(words),1),'median':statistics.median(words),'min':min(words),'max':max(words)},timers=dict(sorted(collections.Counter(s['time_mode'] for s in stories).items())),single_block_sprints=sum('\n' not in s['content'] for s in stories),paragraph_counts=dict(sorted(collections.Counter(len(re.split(r'\n\s*\n',s['content'].strip())) for s in stories).items())))
    summary['word_count_by_timer']={str(t):{'min':min(w),'median':statistics.median(w),'mean':round(statistics.mean(w),1),'max':max(w)} for t in sorted({s['time_mode'] for s in stories}) for w in [[s['word_count'] for s in stories if s['time_mode']==t]]}
    bundle['metadata']['as_of']=latest
    bundle['metadata']['initial_editorial_sprints']=30
    bundle['metadata']['history_note']='Original 360-story sample plus 30 initial editorial sprints published in October 2026. Recurring posts are stored live and are not all included in this local preview. Initial editorial publications have no fabricated timed-session logs.'
    return bundle


def export():
    rows=[{**{k:s[k] for k in ('title','content','starter_sentence','word_count','time_mode','mode','is_hardcore')},'id':s['id'].removeprefix('sample-story-'),'source_key':s['id'],'author_id':s['author_id'].removeprefix('sample-writer-')} for s in records()]
    payload=json.dumps(rows,ensure_ascii=False)
    assert '$initial$' not in payload
    sql='''-- Explicitly requested initial batch: 30 fictional stories, one per new writer.
-- Idempotent inserts; actual publication timestamps. Does not alter votes or real stories.
BEGIN;
SET LOCAL lock_timeout = '5s';
INSERT INTO public.sample_stories (id,source_key,author_id,title,content,starter_sentence,word_count,time_mode,mode,is_hardcore,created_at,provenance)
SELECT id,source_key,author_id,title,content,starter_sentence,word_count,time_mode,mode,is_hardcore,now(),
 'Original AI-written fiction; timestamp is actual editorial publication, not a real writing session.'
FROM jsonb_to_recordset($initial$PAYLOAD$initial$::jsonb)
AS x(id uuid,source_key text,author_id uuid,title text,content text,starter_sentence text,word_count integer,time_mode integer,mode text,is_hardcore boolean)
ON CONFLICT (id) DO NOTHING;
UPDATE public.sample_profiles p SET
 total_stories=(SELECT count(*) FROM public.sample_stories s WHERE s.author_id=p.id AND NOT s.is_hidden),
 total_words=(SELECT coalesce(sum(word_count),0) FROM public.sample_stories s WHERE s.author_id=p.id AND NOT s.is_hidden)
WHERE id IN (SELECT (value->>'author_id')::uuid FROM jsonb_array_elements($initial$PAYLOAD$initial$::jsonb));
COMMIT;
SELECT id,author_username,title,word_count,created_at FROM public.community_stories
WHERE id IN (SELECT (value->>'id')::uuid FROM jsonb_array_elements($initial$PAYLOAD$initial$::jsonb)) ORDER BY author_username;
'''.replace('PAYLOAD',payload)
    (ROOT/'initial-sprints.sql').write_text(sql)
    print('Validated and exported 30 initial sprints.')

if __name__=='__main__':
    export()
