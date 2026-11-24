"""Record editorial intent and check its lineage through shots and reviews."""
from collections import defaultdict
import json
import math
import re

from shared_state import canonical, fingerprint, index, prepare, require, timestamp, validate

TOPIC = 'CPE_CREATIVE_INTENT_V1'
ACTION_PROFILE = 'action_led_war'
HIERARCHY = ('visible_physical_action', 'story_characters_dialogue', 'everyday_context')


def same_time(a, b):
    return math.isclose(a,b,rel_tol=0,abs_tol=1e-6)


def audit(profile, events):
    """Measure authored timeline seconds. Perceived intensity still needs direct review."""
    require(isinstance(profile, dict) and set(profile) == {'kind', 'action_percent', 'story_percent'}
            and profile['kind'] == ACTION_PROFILE, 'Invalid action-led war profile')
    targets = (profile['action_percent'], profile['story_percent'])
    require(all(type(percent) in (int, float) and 0 <= percent <= 100 for percent in targets)
            and same_time(sum(targets), 100), 'Creative profile percentages must be between 0 and 100 and sum to 100')
    require(isinstance(events, list) and events, 'An authored event timeline is required')
    end = 0
    totals = {'ACTION': 0, 'STORY': 0}
    ids, seen_shots = set(), set()
    active_shot = None
    for event in events:
        fields = {'id','shot_id','class','start_s','end_s','on_screen','action','consequence'}
        require(isinstance(event, dict) and set(event)==fields, 'Invalid creative event fields')
        for key in ('id','shot_id'):
            require(isinstance(event[key],str) and re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,79}',event[key]),
                    'Creative events need stable identifiers')
        require(event['id'] not in ids, 'Duplicate creative event')
        ids.add(event['id'])
        shot = event['shot_id']
        if shot != active_shot:
            require(shot not in seen_shots, 'A shot must occupy one contiguous interval')
            seen_shots.add(shot)
            active_shot = shot
        start, stop = event['start_s'], event['end_s']
        require(all(type(t) in (int,float) and math.isfinite(t) for t in (start,stop)) and same_time(start,end) and stop>start,
                'Creative event timeline needs contiguous positive durations')
        category = event['class']
        require(isinstance(category,str) and category in totals and type(event['on_screen']) is bool,
                'Declare event class and visibility')
        require(all(isinstance(event[k],str) and event[k].strip() for k in ('action','consequence')),
                'Each event needs an authored action and consequence')
        require(category!='ACTION' or event['on_screen'], 'Action minutes require physical action on screen')
        totals[category] += stop-start
        end = stop
    action = totals['ACTION'] / end * 100
    story = totals['STORY'] / end * 100
    return {'kind':'AUTHORED_TIMELINE_AUDIT','duration_s':end,'action_s':totals['ACTION'],'story_s':totals['STORY'],
            'action_percent':round(action,6),'story_percent':round(story,6), 'hierarchy':list(HIERARCHY),
            'ratio_matches':same_time(action, targets[0]) and same_time(story, targets[1]), 'artistic_approval':False}


def _require_ratio(profile, measured):
    action, story = profile['action_percent'], profile['story_percent']
    require(measured['ratio_matches'], f'Creative timeline must preserve {action:g}/{story:g}')


def decode(row):
    try:
        value = json.loads(row['choice'])
    except (ValueError,TypeError) as error:
        raise ValueError('Malformed recorded creative intent') from error
    require(isinstance(value,dict) and set(value)=={'profile','events','replaces'}, 'Malformed recorded creative intent')
    _require_ratio(value['profile'], audit(value['profile'], value['events']))
    require(row['episode_id'] and row['user_message_ref'].strip() and row['rationale'].strip(),
            'Creative intent needs an episode and authorization trace')
    return value


def validate_ledger(snapshot):
    by_episode = defaultdict(list)
    for row in snapshot['tables']['Decisions']:
        if row['topic']==TOPIC and row['status']=='RECORDED':
            by_episode[row['episode_id']].append(row)
    for rows in by_episode.values():
        prior = None
        ordered = sorted(rows,key=lambda item:(timestamp(item['updated_at']),item['id']))
        for row in ordered:
            value = decode(row)
            require(value['replaces']==prior, 'Creative intent revisions are disconnected')
            prior={'id':row['id'],'revision':row['revision'],'sha256':fingerprint(row)}
        ep = index(snapshot)['Episodes'].get(ordered[-1]['episode_id'])
        require(ep and same_time(ep['target_seconds'],value['events'][-1]['end_s']),
                'Episode duration changed without a matching creative intent')


def current(snapshot, project_id, episode_id):
    rows = [row for row in snapshot['tables']['Decisions'] if row['topic']==TOPIC and row['status']=='RECORDED'
            and row['project_id']==project_id and row['episode_id']==episode_id]
    if not rows:
        return None
    row = max(rows,key=lambda r:(timestamp(r['updated_at']),r['id']))
    return {'decision':{'id':row['id'],'revision':row['revision'],'sha256':fingerprint(row)}, **decode(row)}


def check_new(snapshot, projected, row, message_ref):
    current_intent = current(snapshot,row['project_id'],row['episode_id'])
    prior = current_intent['decision'] if current_intent else None
    data = decode(row)
    require(data['replaces']==prior and row['user_message_ref']==message_ref,
            'Creative decision needs the current prior version and authorization')
    ep = index(projected)['Episodes'].get(row['episode_id'])
    require(ep and same_time(ep['target_seconds'],data['events'][-1]['end_s']), 'Creative timeline differs from episode duration')


def plan(snapshot, spec):
    validate(snapshot)
    episode = index(snapshot)['Episodes'].get(spec['episode_id'])
    require(episode and episode['project_id']==spec['project_id'], 'Creative intent belongs to the selected episode')
    measured = audit(spec['profile'],spec['events'])
    _require_ratio(spec['profile'], measured)
    authorization = spec['authorization']
    prior = current(snapshot,episode['project_id'],episode['id'])
    expected = prior['decision'] if prior else None
    require(spec.get('replaces')==expected, 'Creative intent changed. Review its latest version first')
    values = {'project_id':episode['project_id'],'episode_id':episode['id'],'is_test':episode['is_test'],
              'gate_id':'G2','topic':TOPIC,'status':'RECORDED',
              'choice':canonical({'profile':spec['profile'],'events':spec['events'],'replaces':expected}),
              'rationale':spec.get('reason') or 'Direção e distribuição de tempo confirmadas para o episódio.',
              'user_message_ref':authorization['user_message_ref']}
    from shot_workflow import stamp
    changes = [{'table':'Decisions','id':spec['decision_id'],'expected_revision':None,'values':values}]
    if not same_time(measured['duration_s'],episode['target_seconds']):
        require(spec.get('episode_revision')==episode['revision'], 'Creative timeline differs from episode duration')
        changes.append({'table':'Episodes','id':episode['id'],'expected_revision':episode['revision'],
                        'values':{'target_seconds':measured['duration_s']}})
    return prepare(snapshot,{**authorization,'at':stamp(),'changes':changes})


def shot_intent(snapshot, shot):
    intent = current(snapshot,shot['project_id'],shot['episode_id'])
    if not intent:
        return None
    events = [event for event in intent['events'] if event['shot_id']==shot['id']]
    require(events, 'Shot has no matching events in the current creative intent')
    return {'decision':intent['decision'],'profile':intent['profile'],'events':events}


def check_shot_binding(binding, shot, cinematic_plan):
    events = binding['events']
    require(cinematic_plan is not None, 'This shot needs a timed plan for its approved events')
    require(same_time(events[-1]['end_s']-events[0]['start_s'],shot['duration_s']), 'Shot duration differs from the intent timeline')
    expected = {event['id']:event for event in events}
    coverage = defaultdict(list)
    for beat in cinematic_plan['beats']:
        for event_id in beat.get('event_ids',[]):
            require(event_id in expected, 'Beat references an event outside the approved shot')
            coverage[event_id].append((beat['start_s'],beat['end_s'],beat['action']))
    offset = events[0]['start_s']
    for event in events:
        intervals = coverage[event['id']]
        require(intervals, 'Shot omits approved event '+event['id'])
        required_start, required_end = event['start_s']-offset, event['end_s']-offset
        require(same_time(intervals[0][0],required_start) and same_time(intervals[-1][1],required_end)
                and all(same_time(a[1],b[0]) for a,b in zip(intervals,intervals[1:])),
                'Beat timing changes approved event '+event['id'])
        required_action = event['action'].split()
        require(any(required_action==fragment[2].split() for fragment in intervals),
                'Beat action changes approved event '+event['id'])


def prompt_lines(binding):
    if binding is None:
        return ''
    lines = ['Acontecimentos aprovados para este plano']
    for event in binding['events']:
        place = 'em quadro' if event['on_screen'] else 'fora de quadro'
        lines.append(f"{event['id']} · {place} · {event['action']} Consequência: {event['consequence']}")
    return '\n'.join(lines)


def target_intent(snapshot, table, row):
    if table not in {'Screenplays','Shot List','Prompts','Artifact Registry'}:
        return None
    intent = current(snapshot,row['project_id'],row['episode_id'])
    if not intent:
        return None
    shot_ids = None
    if table == 'Shot List':
        shot_ids = {row['id']}
    if table == 'Prompts' and row['target_table']=='Shot List':
        shot_ids = {row['target_id']}
    if table == 'Artifact Registry':
        from shot_workflow import TOPIC as SHOT_TOPIC, ref
        pin = ref(table,row)
        links = []
        for decision in snapshot['tables']['Decisions']:
            if decision['topic']==SHOT_TOPIC and decision['status']=='RECORDED':
                link = json.loads(decision['choice'])
                if link['relation']=='take' and link['to']['table']==table and link['to']['id']==row['id']:
                    links.append(link)
        if links:
            shot_ids = {link['from']['id'] for link in links if link['to']==pin}
            require(shot_ids, 'Renew the shot link for this material version before review')
        elif row['kind'] not in {'FINAL_ASSET','PRODUCTION_EXPORT'}:
            return None
    if shot_ids is not None:
        intent['events'] = [event for event in intent['events'] if event['shot_id'] in shot_ids]
        require(intent['events'], 'Target has no matching events in the current creative intent')
    return intent


def review(intent, observations):
    """Validate a direct review's event evidence. The CLI does not inspect acting itself."""
    require(isinstance(observations,dict) and observations.get('decision')==intent['decision'],
            'Creative review must bind the current intent decision')
    entries = observations.get('events')
    require(isinstance(entries,list), 'Creative review needs event observations')
    statuses = {'VISIBLE','PRESENT','AUDIBLE_ONLY','OMITTED','REPLACED','DIALOGUE_ONLY','UNKNOWN'}
    expected = {event['id']:event for event in intent['events']}
    results = {}
    for obs in entries:
        require(isinstance(obs,dict) and isinstance(obs.get('id'),str) and obs['id'] in expected and obs['id'] not in results
                and isinstance(obs.get('status'),str) and obs['status'] in statuses, 'Invalid creative event observation')
        status = obs['status']
        require(status=='UNKNOWN' or (isinstance(obs.get('evidence_ref'),str) and obs['evidence_ref'].strip()),
                'Creative observations must identify a beat, frame or timecode')
        event = expected[obs['id']]
        if status=='UNKNOWN':
            verdict = 'UNKNOWN'
        elif status in {'OMITTED','REPLACED','DIALOGUE_ONLY'} or (event['on_screen'] and status!='VISIBLE'):
            verdict = 'REJECT'
        elif obs.get('consequence_observed') is not True:
            verdict = 'REVISE'
        else:
            verdict = 'MATCH'
        results[obs['id']] = verdict
    for event_id in expected.keys()-results.keys():
        results[event_id] = 'UNKNOWN'
    intensity = observations.get('intensity','UNKNOWN')
    pacing = observations.get('pacing','UNKNOWN')
    require(intensity in ('OBSERVED','DECLARED_ONLY','UNKNOWN') and pacing in ('FIT','REVISE','UNKNOWN'),
            'Invalid intensity or pacing review')
    require((intensity=='UNKNOWN' and pacing=='UNKNOWN') or
            (isinstance(observations.get('evidence_ref'),str) and observations['evidence_ref'].strip()),
            'Intensity and pacing observations need evidence')
    marks = set(results.values())
    ready = marks=={'MATCH'} and intensity=='OBSERVED' and pacing=='FIT'
    outcome = ('REJECT' if 'REJECT' in marks or intensity=='DECLARED_ONLY' else
               'REVISE' if 'REVISE' in marks or pacing=='REVISE' else 'MATCH' if ready else 'UNKNOWN')
    return {'kind':'CREATIVE_INTENT_REVIEW','outcome':outcome,'events':results,'approved':False}


def apply_to_review(result, intent, authored):
    if intent is None:
        return result
    observations = authored.get('intent_review', {'decision':intent['decision'],'events':[]})
    judgment = review(intent,observations)
    recommendation = result['recommendation']
    if judgment['outcome'] in {'REJECT','REVISE'}:
        recommendation = 'CHANGES_REQUESTED'
    elif judgment['outcome']=='UNKNOWN' and recommendation=='READY_FOR_HUMAN_DECISION':
        recommendation = 'INCOMPLETE_EVIDENCE'
    return {**result,'recommendation':recommendation,'creative_review':judgment}
