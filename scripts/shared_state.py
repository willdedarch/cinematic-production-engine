#!/usr/bin/env python3
"""Offline validation and write-plan preparation. Does not connect or write to Google.

The agent executes connector operations separately. An in-memory plan is never a receipt.
"""
import argparse, copy, datetime as dt, hashlib, json,re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SCHEMA=json.loads((ROOT/'schemas/shared-state.tables.json').read_text(encoding='utf-8'))
GATES=json.loads((ROOT/'orchestration/gates.json').read_text(encoding='utf-8'))
BY={g['id']:g for g in GATES}
DONE={'APPROVED','LOCKED','SKIPPED'}
ASSETS={'Screenplays','Characters','Locations','Props','Cinematography','Shot List','Prompts'}
PROTECTED=ASSETS|{'Reference Library','Examples','Techniques','Creative Preferences','Model Compatibility','Production Lessons','Director Profiles','Genre Profiles','Visual Standards','Evaluation Results','Prompt Library','Pairwise Comparisons','Human Feedback','Failure Diagnostics','Revision Results'}
PROTECTED|={'Artifact Registry','Experiments','Tool Capabilities','Execution Evidence','Checkpoints'}

class StateError(ValueError):pass
class Conflict(StateError):pass

def require(ok,message):
 if not ok:raise StateError(message)

def canonical(value):return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False)
def fingerprint(row):return hashlib.sha256(canonical(row).encode('utf-8')).hexdigest()
def timestamp(value):
 require(isinstance(value,str),'Timestamp must be ISO 8601 text')
 try:v=dt.datetime.fromisoformat(value.replace('Z','+00:00'))
 except ValueError:raise StateError('Invalid ISO timestamp')
 require(v.tzinfo is not None,'Timestamp requires timezone')
 return v
def index(snapshot):return {n:{r['id']:r for r in rows} for n,rows in snapshot['tables'].items()}

def validate(snapshot):
 require(snapshot.get('schema_version')=='3.1.0','Unsupported shared schema')
 timestamp(snapshot.get('read_at'))
 require(bool(snapshot.get('spreadsheet_id')),'Missing spreadsheet binding')
 require(set(snapshot.get('tables',{}))==set(SCHEMA['tables']),'Incomplete table coverage')
 ids=set()
 for name,rows in snapshot['tables'].items():
  require(isinstance(rows,list),name+': rows must be a list')
  spec=SCHEMA['tables'][name]
  for r in rows:
   require(set(r)==set(spec['columns']),name+': missing/unknown columns')
   require(isinstance(r['id'],str) and bool(r['id'].strip()),'Missing stable id')
   require(r['id'] not in ids,'Duplicate global id: '+r['id']);ids.add(r['id'])
   for k,t in spec['types'].items():
    v=r[k]
    if v=='' and k not in spec['required']:continue
    ok={'string':isinstance(v,str),'boolean':type(v) is bool,'integer':type(v) is int,'number':type(v) in (int,float)}[t]
    require(ok,f'{name}/{r["id"]}: invalid type {k}')
    if t=='number':require(abs(v)<float('inf'),f'{k}: must be finite')
   require(type(r['revision']) is int and r['revision']>=1,'Revision must be positive integer')
   require(bool(r['updated_by'].strip()),'Missing executor')
   timestamp(r['updated_at'])
   for k,options in spec['enums'].items():require(r[k] in options,f'{name}: invalid {k}')
 ix=index(snapshot);forward_scopes={}
 for name,rows in snapshot['tables'].items():
  for r in rows:
   pending={}
   if name=='Revision History' and (r['project_id'] not in ix['Projects'] or (r['episode_id'] and r['episode_id'] not in ix['Episodes'])):
    from history_integrity import pending_new_scope
    if r['op_id'] not in forward_scopes:forward_scopes[r['op_id']]=pending_new_scope(snapshot,r['op_id'])
    pending=forward_scopes[r['op_id']]
   p=ix['Projects'].get(r['project_id']) or pending.get(('Projects',r['project_id']));require(p is not None,'Missing project: '+r['project_id'])
   require(p['is_test']==r['is_test'],'Test/production scopes mixed')
   if r['episode_id']:
    e=ix['Episodes'].get(r['episode_id']) or pending.get(('Episodes',r['episode_id']));require(e is not None and e['project_id']==r['project_id'],'Episode scope mismatch')
   if name=='Projects':require(r['id']==r['project_id'] and not r['episode_id'] and r['name'].strip(),'Project identity/name missing')
   if name=='Episodes':require(r['id']==r['episode_id'] and r['title'].strip() and type(r['episode_number']) is int and r['episode_number']>0,'Episode identity/title/number invalid')
   if name=='Projects':require(r['credits_allowed']==0 and r['generation_mode']=='manual','Paid/automatic generation prohibited')
   for k,dest in SCHEMA['tables'][name]['foreign_keys'].items():
    if r[k]:
     target=ix[dest].get(r[k]);require(target is not None and target['project_id']==r['project_id'],'Broken foreign key: '+k)
   if r.get('supersedes_id'):
    visited={r['id']};parent=r
    while parent.get('supersedes_id'):
     key=parent['supersedes_id'];require(key not in visited,'Version lineage cycle');visited.add(key);parent=ix[name][key]
   for k,dest in [('character_ids','Characters'),('prop_ids','Props')]:
    if k in r and r[k]:
     for id in r[k].split(','):
      target=ix[dest].get(id);require(target is not None and target['project_id']==r['project_id'],'Broken list reference '+id)
   if name in ('Prompts','Continuity'):
    tab=r.get('target_table',r.get('entity_table'));key=r.get('target_id',r.get('entity_id'))
    target=ix.get(tab,{}).get(key);require(target is not None and target['project_id']==r['project_id'],'Broken entity reference')
   if name in ASSETS and r['status'] in {'APPROVED','LOCKED'}:
    ref=r.get('asset_ref',r.get('text_or_ref',r.get('prompt_text',r.get('intent',r.get('purpose')))))
    require(bool(ref and ref.strip()),name+': no deliverable')
   if name=='Checklists' and r['checked']:
    require(bool(r['evidence'].strip()) and r['observed_or_planned']!='not_accessible','Checked item lacks accessible evidence')
   if name=='Decisions' and r['status']=='RECORDED':require(bool(r['user_message_ref'].strip()),'Decision requires received user message')
   if name=='Approvals' and r['status']=='RECORDED':
    require(r['decision']!='PENDING' and r['approver'].strip() and r['user_message_ref'].strip() and r['evidence'].strip(),'Approval lacks human evidence')
    w=ix['Workflow'].get(r['workflow_id'])
    require(w is not None and all(r[k]==w[k] for k in ['project_id','episode_id','gate_id']),'Approval scope/gate mismatch')
   if name=='Evaluation Results':
    target=ix.get(r['target_table'],{}).get(r['target_id'])
    require(target is not None and target['project_id']==r['project_id'] and target['episode_id']==r['episode_id'],'Evaluation target/scope missing')
    require(type(r['target_revision']) is int and 1<=r['target_revision']<=target['revision'],'Evaluation revision invalid')
    require(r['rubric_ref'].strip() and r['reviewer'].strip() and r['evidence'].strip(),'Evaluation requires rubric, reviewer and evidence')
    if r['status'] in {'APPROVED','LOCKED'}:require(r['artistic_result'].strip() and r['technical_result'].strip(),'Complete review required; historical revisions remain valid history')
   if name in {'Failure Diagnostics','Human Feedback'}:
    target=ix.get(r['target_table'],{}).get(r['target_id'])
    require(target is not None and target['project_id']==r['project_id'] and target['episode_id']==r['episode_id'],'Diagnostic/feedback target mismatch')
    require(type(r['target_revision']) is int and 1<=r['target_revision']<=target['revision'],'Diagnostic/feedback revision invalid')
   if name=='Human Feedback':
    require(r['human_decision'] in {'APPROVE','REJECT','TIE','BOTH_FAIL','REVISE','PREFER_A','PREFER_B'} and r['user_message_ref'].strip() and r['reason'].strip() and r['evidence'].strip() and r['preference_scope'] in {'deliverable','scene','episode','project','genre','model','global'},'Human feedback needs actual message, reason, evidence and scope')
    if r['preference_scope']=='scene':
     evidence=json.loads(r['evidence']);shot=evidence.get('shot',{});origin=ix['Shot List'].get(shot.get('id'))
     require(r['target_table']=='Pairwise Comparisons' and evidence.get('kind')=='TAKE_PREFERENCE' and
             evidence.get('preference_scope')=='scene' and origin and origin['episode_id']==r['episode_id'] and
             shot.get('scene_beat') and type(shot.get('revision')) is int and 1<=shot['revision']<=origin['revision'] and
             (shot['revision']!=origin['revision'] or shot.get('sha256')==fingerprint(origin)),
             'Scene preference must reference its reviewed shot and scene')
   if name=='Failure Diagnostics':require(r['symptom'].strip() and r['evidence'].strip() and r['alternative_causes'].strip() and r['confidence'] in {'LOW','MEDIUM','HIGH'} and r['verification'].strip(),'Diagnosis lacks evidence/differential/test')
   if name=='Revision Results':
    for prefix in ['previous','current']:
     target=ix.get(r['target_table'],{}).get(r[prefix+'_id']);require(target is not None and target['project_id']==r['project_id'] and target['episode_id']==r['episode_id'],'Revision comparison target/scope mismatch');require(type(r[prefix+'_revision']) is int and 1<=r[prefix+'_revision']<=target['revision'],'Revision comparison version invalid')
   if name=='Pairwise Comparisons':
    target=ix['Examples'][r['target_id']];require(type(r['target_revision']) is int and 1<=r['target_revision']<=target['revision'],'Pairwise target revision invalid')
   if name=='Experiments':
    require(type(r['authorized_max_variants']) is int and 1<=r['authorized_max_variants']<=4,'Experiment variant limit invalid')
    try:variants=json.loads(r['variants_json'])
    except ValueError:raise StateError('Experiment variants JSON invalid')
    require(isinstance(variants,list) and 1<=len(variants)<=r['authorized_max_variants'],'Experiment variants outside scope')
    if r['tool']=='native_image' and r['observed'].strip():require(r['authorization_ref'].strip(),'Native experiment result lacks specific authorization')
   if name=='Artifact Registry':
    require(type(r['version']) is int and r['version']>=1 and r['uri'].strip() and re.fullmatch('[0-9a-f]{64}',r['sha256']) and r['origin'].strip() and r['rights'].strip(),'Artifact provenance/hash/version missing')
    if r['status'] in {'APPROVED','LOCKED'}:
     require(r['technical_review_id'] and r['artistic_review_id'] and r['approval_id'],'Imported/preview/final assets require two review layers and human approval')
     for k in ['technical_review_id','artistic_review_id']:
      e=ix['Evaluation Results'][r[k]];require(e['target_table']=='Artifact Registry' and e['target_id']==r['id'] and e['episode_id']==r['episode_id'],'Artifact review target mismatch')
     try:
      technical=json.loads(ix['Evaluation Results'][r['technical_review_id']]['technical_result']);artistic=json.loads(ix['Evaluation Results'][r['artistic_review_id']]['artistic_result'])
     except (ValueError,TypeError):raise StateError('Artifact review results must be structured JSON')
     require(isinstance(technical,dict) and technical.get('status')=='PASS' and technical.get('target_sha256')==r['sha256'] and isinstance(technical.get('checks'),list) and bool(technical['checks']) and all(isinstance(c,dict) for c in technical['checks']),'Artifact technical review did not pass this material hash')
     require(all(c.get('status') in {'PASS','NOT_APPLICABLE'} and c.get('observation') and (c.get('evidence_ref') or c['status']=='NOT_APPLICABLE') for c in technical['checks']) and any(c.get('status')=='PASS' for c in technical['checks']),'Artifact technical checks not supported')
     require(isinstance(artistic,dict) and artistic.get('status')=='RECOMMEND_APPROVAL' and artistic.get('target_sha256')==r['sha256'] and type(artistic.get('level')) is int and 1<=artistic['level']<=5 and artistic.get('rationale') and isinstance(artistic.get('observations'),list) and bool(artistic['observations']) and all(isinstance(c,dict) for c in artistic['observations']),'Artifact artistic review did not recommend this material hash')
     require(all(c.get('observation') and c.get('evidence_ref') and c.get('interpretation') for c in artistic['observations']),'Artifact artistic evidence missing')
     a=ix['Approvals'][r['approval_id']];require(a['status']=='RECORDED' and a['decision'] in {'APPROVE','LOCK'} and a['episode_id']==r['episode_id'] and a['gate_id'] in {r['gate_id'],'G13','G14'},'Artifact approval scope/gate missing')
   if name=='Revision History':
    require(r['op_id'].strip() and r['actor'].strip(),'Journal identity missing')
    for k in ['changes_json','guards_json']:
     try:json.loads(r[k])
     except (ValueError,TypeError):raise StateError('Journal JSON invalid')
 for e in snapshot['tables']['Episodes']:
  wf=[r for r in snapshot['tables']['Workflow'] if r['episode_id']==e['id']]
  require(len(wf)==16 and {r['gate_id'] for r in wf}==set(BY),'Episode requires exactly 16 unique gates')
  wb={r['gate_id']:r for r in wf}
  for w in wf:
   g=BY[w['gate_id']]
   require(w['depends_on']==','.join(g['depends']) and w['skippable']==g['skippable'],'Gate contract changed')
   ck=sorted([c for c in snapshot['tables']['Checklists'] if c['workflow_id']==w['id']],key=lambda c:c['item_index'])
   require(len(ck)==len(g['checks']) and [c['item_index'] for c in ck]==list(range(1,len(ck)+1)),'Checklist coverage invalid')
   require(all(c['episode_id']==e['id'] and c['gate_id']==g['id'] and c['criterion']==g['checks'][i] for i,c in enumerate(ck)),'Checklist identity mismatch')
   if w['status'] in DONE:
    require(all(wb[d]['status'] in DONE for d in g['depends']),'Dependency pending')
    require(bool(w['evidence'].strip()) and bool(w['deliverable_ref'].strip()),'Gate evidence/deliverable missing')
    if w['status']=='SKIPPED':require(g['skippable'] and bool(w['reason'].strip()),'Critical gate/reason missing')
    else:require(all(c['checked'] for c in ck),'Checklist incomplete')
    action={'APPROVED':'APPROVE','LOCKED':'LOCK','SKIPPED':'SKIP'}[w['status']]
    require(any(a['workflow_id']==w['id'] and all(a[k]==w[k] for k in ['project_id','episode_id','gate_id']) and a['gate_revision']==w['revision'] and a['decision']==action and a['status']=='RECORDED' for a in snapshot['tables']['Approvals']),'No approval for current gate revision')
 from series_bible import validate_canon_ledger
 from shot_workflow import validate_shot_links
 from creative_intent import validate_ledger
 validate_canon_ledger(snapshot)
 validate_shot_links(snapshot)
 validate_ledger(snapshot)
 from desk_queue import ledger
 ledger(snapshot)
 return True

def guard(snapshot):
 """Conservative whole-scope guard includes membership, values and revisions.

 Catches inserts/deletes and edits made in Sheets without incrementing revision.
 The connector must reconstruct the complete scope immediately before writing.
 """
 validate(snapshot)
 return {n:{r['id']:fingerprint(r) for r in sorted(rows,key=lambda r:r['id'])} for n,rows in snapshot['tables'].items() if n!='Revision History'}

def check_guards(plan,fresh,require_prepared=False):
 from history_integrity import verify_journal
 validate(fresh)
 if fresh['spreadsheet_id']!=plan['spreadsheet_id']:raise Conflict('Wrong spreadsheet')
 if guard(fresh)!=plan['guards']:raise Conflict('State changed; prepare a new plan')
 if require_prepared:require(timestamp(fresh['read_at'])>=timestamp(plan['prepared_at']),'Prewrite read predates plan')
 verify_journal(plan,fresh,require_prepared=require_prepared,prewrite=True)
 from desk_guard import verify_new
 verify_new(fresh,plan['candidate'],plan['changes'],plan['authorization_ref'])
 from takes import verify_vote_sources
 verify_vote_sources(plan,fresh)
 from shot_workflow import verify_return_sources
 verify_return_sources(plan)
 return True

def prepare(snapshot,intent,review=None):
 """Plan an authorized state change and verify creative approvals. No remote write."""
 from approval_guard import bind_reviews
 from journal_codec import cell_units
 validate(snapshot)
 require(intent.get('authorized') is True and bool(intent.get('user_message_ref')),'Received authorization required')
 require(bool(intent.get('actor')) and bool(intent.get('op_id')),'Operation/actor missing')
 timestamp(intent.get('at'))
 require(bool(intent.get('changes')),'Empty operation')
 op=intent['op_id']
 prior=[r for r in snapshot['tables']['Revision History'] if r['op_id']==op]
 require(not prior,'Existing operation: reconcile by read; never blindly replay')
 intent=bind_reviews(snapshot,intent,review)
 projected=copy.deepcopy(snapshot);ix=index(projected);changes=[];seen=set()
 for change in intent['changes']:
  table,id=change['table'],change['id'];require(table in SCHEMA['tables'] and table!='Revision History','Use journal events separately')
  require((table,id) not in seen,'Duplicate change target');seen.add((table,id))
  old=ix[table].get(id);expected=change.get('expected_revision')
  require((old is None and expected is None) or (old is not None and type(expected) is int and old['revision']==expected),'Stale revision')
  patch=change['values'];require(isinstance(patch,dict),'Patch must be object')
  require(not any(k in patch for k in ['id','revision','updated_at','updated_by','last_op_id']),'Immutable/system fields in patch')
  require(set(patch)<=set(SCHEMA['tables'][table]['columns']),'Unknown patch field')
  require(all(cell_units(v)<=50000 for v in patch.values() if isinstance(v,str)),'Business cell exceeds Sheets limit. Store a versioned document and its reference before planning')
  if old:
   require(not any(k in patch for k in ['project_id','episode_id','is_test']),'Cannot move record scope')
   if table in PROTECTED and table not in ASSETS and old.get('status') in {'APPROVED','LOCKED'}:
    require(old['status']=='APPROVED' and patch=={'status':'LOCKED'},'Preserve approved/locked knowledge; create linked successor')
   if table in ASSETS:
    before,after=old['status'],patch.get('status',old['status'])
    if before=='LOCKED' or (before=='APPROVED' and not (set(patch)=={'status'} and after=='LOCKED')):raise StateError('Preserve approved asset; create a linked successor version')
    allowed_assets={'DRAFT':{'DRAFT','REVIEW_REQUIRED','ARCHIVED'},'REVIEW_REQUIRED':{'REVIEW_REQUIRED','DRAFT','CHANGES_REQUESTED','APPROVED'},'APPROVED':{'LOCKED'},'LOCKED':set(),'CHANGES_REQUESTED':{'DRAFT','REVIEW_REQUIRED','ARCHIVED'},'ARCHIVED':set()}
    require(after in allowed_assets[before],'Invalid asset transition')
   if table=='Approvals' and old['status']=='RECORDED':raise StateError('Approval history is immutable')
   if table=='Decisions' and old['status']=='RECORDED' and old['topic'] in {'CPE_CANON_V1','CPE_SHOT_LINK_V1','CPE_DESK_PROPOSAL_V1','CPE_DESK_RESULT_V1','CPE_CREATIVE_INTENT_V1'}:
    raise StateError('Recorded series and shot facts are immutable: create a successor decision')
   if table=='Workflow':
    before,after=old['status'],patch.get('status',old['status'])
    allowed={'PENDING':{'IN_PROGRESS','REVIEW_REQUIRED','SKIPPED','CHANGES_REQUESTED'},'IN_PROGRESS':{'REVIEW_REQUIRED','SKIPPED','CHANGES_REQUESTED'},'REVIEW_REQUIRED':{'APPROVED','CHANGES_REQUESTED','SKIPPED'},'APPROVED':{'LOCKED','CHANGES_REQUESTED'},'LOCKED':{'CHANGES_REQUESTED'},'SKIPPED':{'CHANGES_REQUESTED'},'CHANGES_REQUESTED':{'IN_PROGRESS','REVIEW_REQUIRED','SKIPPED'}}
    require(after in allowed[before] or (after==before and before not in DONE),'Invalid gate transition')
    if after=='CHANGES_REQUESTED':require(bool(patch.get('reason','').strip()),'Revision requires explicit reason')
   new={**old,**patch}
  else:
   new={k:'' for k in SCHEMA['tables'][table]['columns']};new.update(patch);new['id']=id
  new.update(revision=(old['revision']+1 if old else 1),updated_at=intent['at'],updated_by=intent['actor'],last_op_id=op)
  if old:projected['tables'][table]=[new if r['id']==id else r for r in projected['tables'][table]]
  else:projected['tables'][table].append(new)
  ix[table][id]=new;changes.append({'table':table,'id':id,'before':copy.deepcopy(old),'after':copy.deepcopy(new)})
 # Asset approval/locking is coupled to a currently satisfied department gate.
 for c in changes:
  if c['table'] in ASSETS and c['after']['status'] in {'APPROVED','LOCKED'}:
   row=c['after']
   require(any(w['episode_id']==row['episode_id'] and w['gate_id']==row['gate_id'] and w['status'] in {'APPROVED','LOCKED'} for w in projected['tables']['Workflow']),'Asset approval requires current department gate approval')
  if c['table']=='Artifact Registry' and c['after']['status'] in {'APPROVED','LOCKED'}:
   require(c['before'] is not None,'Import/create a draft and review it before approving a registered asset')
   if c['after']['status']=='LOCKED':require(c['before']['status']=='APPROVED','Approve a registered asset before locking')
   if c['before']['status']!='APPROVED':
    for key in ['technical_review_id','artistic_review_id']:
     ev=ix['Evaluation Results'].get(c['after'][key]);require(ev is not None and ev['target_revision']==c['before']['revision'],'Registered approval requires reviews of the preimage revision')
 # Revision invalidates all descendants, including locked ones, without erasing assets.
 for c in changes:
  if c['table']=='Workflow' and c['before'] and c['after']['status']=='CHANGES_REQUESTED':
   affected={c['after']['gate_id']}
   for g in GATES:
    if any(d in affected for d in g['depends']):affected.add(g['id'])
   for w in projected['tables']['Workflow']:
    if w['episode_id']==c['after']['episode_id'] and w['gate_id'] in affected:
     require((w['gate_id']==c['after']['gate_id'] or (w['id'] in {x['id'] for x in changes if x['table']=='Workflow'})) and w['status']=='CHANGES_REQUESTED','Revision must invalidate every descendant')
     ck=[r for r in projected['tables']['Checklists'] if r['workflow_id']==w['id']]
     require(all(not r['checked'] for r in ck),'Revision must reset descendant checklists')
 validate(projected)
 from desk_guard import verify_new
 verify_new(snapshot,projected,changes,intent['user_message_ref'])
 for entry in changes:
  if entry['table']=='Approvals' and entry['after']['status']=='RECORDED':
   require(entry['after']['user_message_ref']==intent['user_message_ref'],'Approval must cite the received authorization')
  if entry['table']=='Decisions' and entry['after']['topic']=='CPE_CANON_V1' and entry['after']['status']=='RECORDED':
   require(entry['after']['user_message_ref']==intent['user_message_ref'],'Story fact must cite the received authorization')
  if entry['table']=='Decisions' and entry['after']['topic']=='CPE_SHOT_LINK_V1' and entry['after']['status']=='RECORDED':
   from shot_workflow import new_link
   new_link(projected,entry['after'],intent['user_message_ref'])
  if entry['table']=='Decisions' and entry['after']['topic']=='CPE_CREATIVE_INTENT_V1' and entry['after']['status']=='RECORDED':
   from creative_intent import check_new
   check_new(snapshot,projected,entry['after'],intent['user_message_ref'])
  if entry['table']=='Checklists' and entry['before']:
   key=entry['before']['workflow_id']
   original=next(w for w in snapshot['tables']['Workflow'] if w['id']==key)
   if original['status'] in DONE and ix['Workflow'][key]['status'] in DONE:
    raise StateError('Reopen the gate before editing its approved checklist evidence')
 from approval_guard import verify_observations
 verify_observations(projected,changes,intent['user_message_ref'])
 plan={'schema_version':'3.1.0','kind':'WRITE_PLAN_NOT_SAVED','spreadsheet_id':snapshot['spreadsheet_id'],'op_id':op,'actor':intent['actor'],'authorization_ref':intent['user_message_ref'],'prepared_at':intent['at'],'guards':guard(snapshot),'changes':changes,'candidate':projected}
 plan['history_baseline']={r['id']:fingerprint(r) for r in snapshot['tables']['Revision History']}
 from history_integrity import verify_journal
 verify_journal(plan,snapshot)
 return plan

def verify_readback(plan,fresh,history_confirmed=False):
 """Compare data and the scope, not merely the connector's success flag."""
 validate(fresh)
 require(fresh['spreadsheet_id']==plan['spreadsheet_id'],'Wrong readback spreadsheet')
 require(timestamp(fresh['read_at'])>=timestamp(plan['prepared_at']),'Readback predates operation')
 expected=plan['candidate']
 require(guard(fresh)==guard(expected),'Readback mismatch or concurrent change: reconciliation required')
 from history_integrity import verify_journal
 verify_journal(plan,fresh,require_prepared=history_confirmed,require_confirmed=history_confirmed)
 return {'status':'CONFIRMED' if history_confirmed else 'DATA_VERIFIED_HISTORY_PENDING','op_id':plan['op_id'],'read_at':fresh['read_at'],'revisions':{c['id']:c['after']['revision'] for c in plan['changes']},'atomic':False}

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('command',choices=['validate','guard','prepare','prewrite','verify','inspect-incident','retain-readback']);p.add_argument('snapshot',type=Path);p.add_argument('--intent',type=Path);p.add_argument('--review',type=Path);p.add_argument('--plan',type=Path);p.add_argument('--output',type=Path);a=p.parse_args()
 s=json.loads(a.snapshot.read_text(encoding='utf-8'))
 if a.command=='validate':result={'valid':validate(s),'saved':False}
 elif a.command in {'inspect-incident','retain-readback'}:
  from reconciliation import observed_versions,reconcile
  plan=json.loads(a.plan.read_text(encoding='utf-8'))
  result=observed_versions(plan,s) if a.command=='inspect-incident' else reconcile(plan,s,json.loads(a.intent.read_text(encoding='utf-8')))
 elif a.command=='guard':result=guard(s)
 elif a.command=='prepare':result=prepare(s,json.loads(a.intent.read_text(encoding='utf-8')),json.loads(a.review.read_text(encoding='utf-8')) if a.review else None)
 elif a.command=='prewrite':result={'ready_to_write':check_guards(json.loads(a.plan.read_text(encoding='utf-8')),s,require_prepared=True),'atomic':False}
 else:result=verify_readback(json.loads(a.plan.read_text(encoding='utf-8')),s,True)
 text=json.dumps(result,ensure_ascii=False,indent=2)
 if a.output:
  require(not a.output.exists(),'Refusing to overwrite local evidence');a.output.write_text(text+'\n',encoding='utf-8')
 else:print(text)
if __name__=='__main__':main()
