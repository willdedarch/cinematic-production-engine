#!/usr/bin/env python3
"""Executed local rehearsal with synthetic user messages; no independent agent or Google write."""
import copy,datetime,json,pathlib,sys,subprocess,tempfile
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from shared_state import prepare,check_guards,verify_readback,fingerprint,StateError,GATES
from approval_guard import CREATIVE_GATES,file_sha256
from journal import journal_rows
from judgment import rubric,digest
from route_knowledge import route

def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
s=json.loads((ROOT/'templates/shared-state.test-fixture.json').read_text(encoding='utf-8'));s['spreadsheet_id']='LOCAL-REHEARSAL-NOT-GOOGLE'
events=[];sequence=0
def change(table,id,values):
 row=next((r for r in s['tables'][table] if r['id']==id),None)
 return dict(table=table,id=id,expected_revision=row['revision'] if row else None,values=values)
def journal(plan,event):
 return journal_rows(plan,event,'TEST-CPE31','TEST-CPE31-EP1',True,now(),'behavioral-results.json')
def rehearsal_review(changes):
 gate=next((w for c in changes for w in s['tables']['Workflow']
            if c['table']=='Workflow' and c['id']==w['id'] and c['values'].get('status')=='APPROVED'),None)
 location=any(c['table']=='Locations' and c['values'].get('status') in {'APPROVED','LOCKED'} for c in changes)
 if not location and (not gate or gate['gate_id'] not in CREATIVE_GATES):return None
 key='TEST-LOC-1' if location else gate['deliverable_ref']
 row=next(r for table in ['Locations','Artifact Registry'] for r in s['tables'][table] if r['id']==key)
 source=(ROOT/(row.get('asset_ref') or row['uri'])).resolve()
 department=row.get('department') or 'geometry'
 rr=rubric(department)
 observation='Synthetic rehearsal checks the identity of this version of '+source.name
 return dict(id='LOCAL-REVIEW-'+key,project_id=row['project_id'],episode_id=row['episode_id'],
    department=department,reviewer='local-rehearsal',creator_id='local-rehearsal',mode='separate_pass',
    target=dict(id=key,revision=row['revision'],uri=str(source),sha256=file_sha256(source),record_sha256=fingerprint(row)),
    context=dict(intention='Rehearse authorization and dependency checks',genre='didactic',format='text or geometry diagram'),
    rubric_sha256=digest(rr),technical=dict(status='PASS',checks=[dict(criterion='local fixture',status='PASS',observation=observation,evidence_ref=source.name)]),
    artistic=dict(status='RECOMMEND_APPROVAL',level=3,rationale='Synthetic response for the rehearsal',strengths=['Scoped fixture'],problems=[],
      observations=[dict(criterion=c,observation=observation,evidence_ref=source.name,interpretation='Synthetic fixture for this criterion') for c in rr['criteria']]),
    adversarial=dict(challenge='Would the validator accept another revision?',successful_choice='The review binds the current hash.'),
    limitations=['Simulated human messages and reviews. Artistic acceptance remains pending.'])
def execute(changes,label):
 global s,sequence
 sequence+=1;op='LOCAL-'+str(sequence)
 intent=dict(op_id=op,actor='behavioral-runner',authorized=True,user_message_ref='SIMULATED-USER-'+op,at=now(),changes=changes)
 p=prepare(s,intent,rehearsal_review(changes));check_guards(p,copy.deepcopy(s));s['tables']['Revision History'].extend(journal(p,'PREPARED'))
 s['read_at']=now();check_guards(p,s,require_prepared=True)
 history=copy.deepcopy(s['tables']['Revision History']);s=p['candidate'];s['tables']['Revision History']=history;s['read_at']=now();verify_readback(p,s)
 s['tables']['Revision History'].extend(journal(p,'CONFIRMED'));s['read_at']=now();receipt=verify_readback(p,s,True)
 events.append(dict(step=label,operation=op,receipt=receipt,native=False));return p
def approval(gate,action='APPROVE'):
 w=next(w for w in s['tables']['Workflow'] if w['gate_id']==gate);id='BEH-AP-'+gate+'-'+str(sequence+1)
 status={'APPROVE':'APPROVED','LOCK':'LOCKED'}[action]
 vals=dict(project_id=w['project_id'],episode_id=w['episode_id'],is_test=True,workflow_id=w['id'],gate_id=gate,gate_revision=w['revision']+1,decision=action,approver='SYNTHETIC TEST USER',user_message_ref='SIMULATED-USER-LOCAL-'+str(sequence+1),evidence='Didactic text/diagram scope only',status='RECORDED')
 return [change('Workflow',w['id'],dict(status=status)),change('Approvals',id,vals)]
def review(gate,complete=True):
 w=next(w for w in s['tables']['Workflow'] if w['gate_id']==gate)
 loaded=route(gate,['war']);events.append(dict(step='knowledge_route',gate=gate,files=[{'file':x['file'],'sha256':x['sha256']} for x in loaded['loaded']]))
 uri='examples/last-water/production.md'
 delivery=uri+'#'+gate
 changes=[]
 if gate=='G8':delivery='TEST-LOC-1'
 elif gate in CREATIVE_GATES:
  delivery='REHEARSAL-MATERIAL-'+gate
  changes.append(change('Artifact Registry',delivery,dict(project_id=w['project_id'],episode_id=w['episode_id'],is_test=True,
       kind='REFERENCE',department='story',gate_id=gate,version=1,uri=uri,sha256=file_sha256(ROOT/uri),
       origin='Bundled teaching fixture',rights='Original example in package',status='DRAFT')))
 changes.append(change('Workflow',w['id'],dict(status='REVIEW_REQUIRED',deliverable_ref=delivery,evidence='Synthetic rehearsal of the teaching example')))
 for c in s['tables']['Checklists']:
  if c['workflow_id']==w['id']:changes.append(change('Checklists',c['id'],dict(checked=complete,evidence='Synthetic exercise: '+uri if complete else '',observed_or_planned='observed' if complete else 'planned')))
 execute(changes,'review '+gate)

for g in GATES[:7]:review(g['id']);execute(approval(g['id']),'synthetic approval '+g['id'])
execute([change('Screenplays','TEST-SC-1',dict(title='A última água — didático',text_or_ref='examples/last-water/production.md#G4',status='REVIEW_REQUIRED'))],'screenplay reference')
review('G7',False)
try:prepare(s,dict(op_id='REJECT-CAST',actor='behavioral-runner',authorized=True,user_message_ref='SIMULATED',at=now(),changes=approval('G7')),rehearsal_review(approval('G7')))
except StateError as e:events.append(dict(step='unseen casting approval rejected',reason=str(e)))
else:raise AssertionError('Unseen casting should remain pending')
execute([change('Locations','TEST-LOC-1',dict(asset_ref='examples/last-water/geo.svg',anchors='W1,N1,E1',dimensions='6m x 4m',status='REVIEW_REQUIRED'))],'import own geometry diagram by reference')
review('G8');execute(approval('G8'),'synthetic geometry-scope approval')
execute([change('Locations','TEST-LOC-1',dict(status='APPROVED'))],'synthetic approval of didactic geometry only')
execute([change('Locations','TEST-LOC-1',dict(status='LOCKED'))],'lock didactic geometry')
try:prepare(s,dict(op_id='REJECT-LOCK',actor='behavioral-runner',authorized=True,user_message_ref='SIMULATED',at=now(),changes=[change('Locations','TEST-LOC-1',{'anchors':'move door'})]))
except StateError as e:events.append(dict(step='locked edit rejected',reason=str(e)))
else:raise AssertionError('Locked edit accepted')
execute([change('Decisions','BEH-REUSE',dict(project_id='TEST-CPE31',episode_id='TEST-CPE31-EP1',is_test=True,gate_id='G8',topic='Reuse',choice='TEST-LOC-1 / revision 4',rationale='Reuse same didactic GEO; no new asset',user_message_ref='SIMULATED-REUSE',status='RECORDED'))],'reuse locked geometry by stable reference')
review('G9');execute(approval('G9'),'synthetic props text-scope approval')
execute([change('Shot List','TEST-SH-1',dict(purpose='Partilha aceita; draft pending visual casting',action='Receive cap with left hand; flask stays right',status='REVIEW_REQUIRED'))],'shot list and prompts prepared as draft')
review('G10')
try:prepare(s,dict(op_id='REJECT-DEP',actor='behavioral-runner',authorized=True,user_message_ref='SIMULATED',at=now(),changes=approval('G10')),rehearsal_review(approval('G10')))
except StateError as e:events.append(dict(step='G10 approval rejected with G7 pending',reason=str(e)))
else:raise AssertionError('Dependency bypass accepted')
affected={'G8'}
for g in GATES:
 if any(d in affected for d in g['depends']):affected.add(g['id'])
cs=[]
for w in s['tables']['Workflow']:
 if w['gate_id'] in affected:
  cs.append(change('Workflow',w['id'],dict(status='CHANGES_REQUESTED',reason='SIMULATED revision: camera obstructs door; preserve GEO anchors')))
  for c in s['tables']['Checklists']:
   if c['workflow_id']==w['id']:cs.append(change('Checklists',c['id'],dict(checked=False,evidence='',observed_or_planned='planned')))
execute(cs,'revision with downstream invalidation and preserved locked asset')
assert next(r for r in s['tables']['Locations'] if r['id']=='TEST-LOC-1')['status']=='LOCKED'
out=pathlib.Path(sys.argv[1]) if len(sys.argv)>1 else pathlib.Path(tempfile.mkdtemp(prefix='cpe-rehearsal-'))/'behavioral-results.json';out.parent.mkdir(parents=True,exist_ok=True)
snapshotfile=out.with_name('behavioral-snapshot.json');snapshotfile.write_text(json.dumps(s,ensure_ascii=False,indent=2),encoding='utf-8')
fresh=subprocess.run([sys.executable,str(ROOT/'scripts/shared_state.py'),'validate',str(snapshotfile)],capture_output=True,text=True,check=True)
events.append(dict(step='interruption and resume in new Python process',result=json.loads(fresh.stdout),independent_chat_session=False))
result=dict(status='EXECUTED_LOCAL_REHEARSAL',synthetic_user=True,independent_agent=False,native_integration=False,paid_generations=0,steps=events,operations=sequence,visual_acceptance='PENDING HUMAN',casting_gate='REVIEW_REQUIRED',g10_after_revision='CHANGES_REQUESTED')
out.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps({'status':result['status'],'operations':sequence,'events':len(events),'report':str(out)}))
