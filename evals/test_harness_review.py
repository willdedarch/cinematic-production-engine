"""Independent Technical Auditor regressions. No remote I/O or Blender execution."""
import copy,json,sys,unittest,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from shared_state import SCHEMA,StateError,validate,fingerprint,prepare
from harness_runtime import validate_artistic_approval,cost_guard,checkpoint,recover
from judgment import rubric,digest
from previs import validate_geometry
from optics import dof

class IndependentHarnessReview(unittest.TestCase):
 def setUp(self):
  self.s=json.loads((ROOT/'templates/shared-state.test-fixture.json').read_text(encoding='utf-8'))
  self.s['tables']['Approvals']=[]
  for n in range(4):
   w=self.workflow('G'+str(n));w.update(status='APPROVED',deliverable_ref='SYNTHETIC-deliverable',evidence='SYNTHETIC observed evidence')
   self.checks(w['gate_id']);self.s['tables']['Approvals'].append(self.approval(w,w['revision'],'BASE-'+str(n)))
  self.w=self.workflow('G4');self.w.update(status='REVIEW_REQUIRED',deliverable_ref='TEST-SC-1',evidence='SYNTHETIC screenplay reviewed')
  self.checks('G4');self.asset=self.s['tables']['Screenplays'][0];self.asset.update(status='REVIEW_REQUIRED',text_or_ref='SYNTHETIC screenplay version one: a choice changes the relation.')
  self.assertTrue(validate(self.s))

 def workflow(self,gate):return next(w for w in self.s['tables']['Workflow'] if w['gate_id']==gate)
 def checks(self,gate):
  for c in self.s['tables']['Checklists']:
   if c['gate_id']==gate:c.update(checked=True,evidence='SYNTHETIC scoped observation',observed_or_planned='observed')
 def approval(self,w,revision,suffix):
  row={k:'' for k in SCHEMA['tables']['Approvals']['columns']}
  row.update(id='AUDIT-APPROVAL-'+suffix,project_id=w['project_id'],episode_id=w['episode_id'],revision=1,updated_at='2026-11-24T10:00:00Z',updated_by='independent-auditor',is_test=True,last_op_id='SYNTHETIC-AUDIT',workflow_id=w['id'],gate_id=w['gate_id'],gate_revision=revision,decision='APPROVE',approver='SYNTHETIC human',user_message_ref='SYNTHETIC-MESSAGE',evidence='SYNTHETIC observation',status='RECORDED')
  return row
 def intent(self,changes):return {'op_id':'INDEPENDENT-HARNESS-REVIEW','actor':'independent-auditor','authorized':True,'user_message_ref':'SYNTHETIC-MESSAGE','at':'2026-11-24T10:01:00Z','changes':changes}
 def gate_changes(self):
  approval=self.approval(self.w,self.w['revision']+1,'CURRENT')
  values={k:v for k,v in approval.items() if k not in {'id','revision','updated_at','updated_by','last_op_id'}}
  return [{'table':'Workflow','id':self.w['id'],'expected_revision':self.w['revision'],'values':{'status':'APPROVED'}},{'table':'Approvals','id':approval['id'],'expected_revision':None,'values':values}]
 def review(self,department='screenplay'):
  rr=rubric(department)
  return {'id':'INDEPENDENT-REVIEW','project_id':self.asset['project_id'],'episode_id':self.asset['episode_id'],'department':department,'reviewer':'independent-auditor','creator_id':'SYNTHETIC-creator','mode':'independent_agent','target':{'id':self.asset['id'],'revision':self.asset['revision'],'sha256':digest(self.asset['text_or_ref']),'record_sha256':fingerprint(self.asset)},'context':{'intention':'A consequential choice','genre':'drama','format':'short screenplay','target_level':4},'rubric_sha256':digest(rr),'technical':{'status':'PASS','checks':[{'criterion':'material and version','status':'PASS','observation':'SYNTHETIC current text is accessible','evidence_ref':'SYNTHETIC in-memory fixture'}]},'artistic':{'status':'RECOMMEND_APPROVAL','level':4,'rationale':'SYNTHETIC test judgment; not real artistic approval','observations':[{'criterion':criterion,'observation':'SYNTHETIC choice and reaction in the fixture','evidence_ref':'SYNTHETIC text version one','interpretation':'SYNTHETIC criterion addressed for contract test'} for criterion in rr['criteria']],'strengths':['SYNTHETIC legible choice'],'problems':[],'integration':'SYNTHETIC gesture, reaction and consequence serve the declared intention'},'adversarial':{'challenge':'Could the same decision be merely declared?','successful_choice':'SYNTHETIC action precedes the consequence'},'limitations':['Synthetic contract fixture; no actual human or audiovisual result']}

 def test_gate_approval_without_content_change_has_bound_review(self):
  p=validate_artistic_approval(self.s,self.intent(self.gate_changes()),self.review())
  self.assertEqual(p['kind'],'WRITE_PLAN_NOT_SAVED')

 def test_gate_cannot_approve_content_changed_after_review(self):
  changes=self.gate_changes()+[{'table':'Screenplays','id':self.asset['id'],'expected_revision':self.asset['revision'],'values':{'text_or_ref':'SYNTHETIC entirely different unreviewed content'}}]
  with self.assertRaises(StateError):validate_artistic_approval(self.s,self.intent(changes),self.review())

 def test_asset_approval_under_approved_gate_still_needs_current_review(self):
  self.w['status']='APPROVED';self.s['tables']['Approvals'].append(self.approval(self.w,self.w['revision'],'ALREADY-APPROVED'))
  self.assertTrue(validate(self.s))
  intent=self.intent([{'table':'Screenplays','id':self.asset['id'],'expected_revision':self.asset['revision'],'values':{'status':'APPROVED'}}])
  with self.assertRaises(StateError):validate_artistic_approval(self.s,intent)

 def test_unrelated_department_review_cannot_approve_screenplay_gate(self):
  with self.assertRaises(StateError):validate_artistic_approval(self.s,self.intent(self.gate_changes()),self.review('geometry'))

 def test_drive_import_requires_received_authorization(self):
  with self.assertRaises(StateError):cost_guard('google_drive.authorized_import')

 def test_camera_id_cannot_escape_output_directory(self):
  geometry={'room_m':[6,4,3],'anchors':[],'actors':[],'props':[],'cameras':[{'id':'../../protected-original','position_m':[1,1,1.3],'target_m':[3,2,1.3],'focal_mm':35}]}
  with self.assertRaises(ValueError):validate_geometry(geometry)

 def test_dof_at_reported_hyperfocal_has_infinite_far_limit(self):
  spec={'focal_mm':50,'f_stop':2.8,'coc_mm':.03,'focus_m':3}
  h=dof(spec)['hyperfocal_m'];spec['focus_m']=h;result=dof(spec)
  self.assertIsNone(result['far_m'])
  self.assertEqual(result['far_label'],'infinity')

 def test_dof_at_reported_hyperfocal_near_limit_is_half(self):
  spec={'focal_mm':50,'f_stop':2.8,'coc_mm':.03,'focus_m':3}
  h=dof(spec)['hyperfocal_m'];spec['focus_m']=h
  self.assertAlmostEqual(dof(spec)['near_m'],h/2,places=8)

 def test_recovery_rejects_guards_that_do_not_describe_checkpoint(self):
  from shared_state import guard
  with tempfile.TemporaryDirectory() as workspace:
   saved_path=checkpoint(self.s,workspace)['checkpoint'];saved=json.loads(Path(saved_path).read_text(encoding='utf-8'))
   current=copy.deepcopy(self.s);current['tables']['Decisions'][0]['choice']='SYNTHETIC newer value'
   saved['scope_guards']=guard(current)
   with self.assertRaises(StateError):recover(saved,current)

 def test_camera_ids_cannot_collide_in_windows_output_paths(self):
  cam={'id':'CAM','position_m':[1,1,1.3],'target_m':[3,2,1.3],'focal_mm':35}
  geometry={'room_m':[6,4,3],'anchors':[],'actors':[],'props':[],'cameras':[cam,{**cam,'id':'cam'}]}
  with self.assertRaises(ValueError):validate_geometry(geometry)

 def registry_state(self):
  """A consistent synthetic episode through G13, with original G10 material."""
  self.s['tables']['Approvals']=[]
  for n in range(14):
   w=self.workflow('G'+str(n));w.update(status='APPROVED',deliverable_ref='SYNTHETIC-deliverable-G'+str(n),evidence='SYNTHETIC observation G'+str(n))
   self.checks(w['gate_id']);self.s['tables']['Approvals'].append(self.approval(w,w['revision'],'REGISTRY-BASE-'+str(n)))
  self.w=self.workflow('G14');self.w.update(status='REVIEW_REQUIRED',deliverable_ref='AUDIT-REGISTRY-1',evidence='SYNTHETIC scoped QC report')
  self.checks('G14')
  row={key:'' for key in SCHEMA['tables']['Artifact Registry']['columns']}
  row.update(id='AUDIT-REGISTRY-1',project_id='TEST-CPE31',episode_id='TEST-CPE31-EP1',revision=1,updated_at='2026-11-24T10:00:00Z',updated_by='independent-auditor',is_test=True,last_op_id='SYNTHETIC-IMPORT',kind='FINAL_ASSET',department='direction',gate_id='G10',version=1,uri='SYNTHETIC://owned-fixture/final-video.mp4',sha256=digest('SYNTHETIC media bytes'),origin='SYNTHETIC contract fixture, no real media',rights='SYNTHETIC owned fixture',status='REVIEW_REQUIRED')
  self.s['tables']['Artifact Registry']=[row]
  self.workflow('G10')['deliverable_ref']=json.dumps({'format':'cpe-deliveries-1','targets':[
   {'id':row['id'],'table':'Artifact Registry','revision':row['revision'],'sha256':row['sha256'],'record_sha256':fingerprint(row)}]})
  for check in self.s['tables']['Checklists']:
   if check['workflow_id']==self.w['id']:
    check['evidence']=json.dumps({'observation':'SYNTHETIC '+check['criterion'],'evidence_ref':'SYNTHETIC test video at frame 1',
                                  'targets':[{'id':row['id'],'revision':row['revision'],'sha256':row['sha256']}]})
  self.assertTrue(validate(self.s));return row

 def registry_review(self,row,review_gate='G14'):
  rr=rubric('direction');r=self.review('direction')
  r['target']={'id':row['id'],'revision':row['revision'],'sha256':row['sha256'],'record_sha256':fingerprint(row)}
  r['context'].update(format='SYNTHETIC video contract, no actual playback',review_gate_id=review_gate)
  r['rubric_sha256']=digest(rr);return r

 def registry_evaluations(self,row,technical='PASS',artistic='READY_FOR_HUMAN_DECISION'):
  ids=[]
  criteria=rubric('direction')['criteria']
  technical_result={'status':technical,'target_sha256':row['sha256'],'checks':[{'criterion':'SYNTHETIC source/version integrity','status':technical,'observation':'SYNTHETIC exact owned fixture bytes','evidence_ref':'SYNTHETIC owned fixture hash'}]}
  artistic_result={'status':'RECOMMEND_APPROVAL' if artistic=='READY_FOR_HUMAN_DECISION' else artistic,'target_sha256':row['sha256'],'level':4 if artistic=='READY_FOR_HUMAN_DECISION' else None,'rationale':'SYNTHETIC contextual review only; no real artistic result','observations':[{'criterion':c,'observation':'SYNTHETIC action/response in scoped fixture','evidence_ref':'SYNTHETIC exact fixture version','interpretation':'SYNTHETIC support for criterion'} for c in criteria],'strengths':['SYNTHETIC observable relationship'],'problems':[],'integration':'SYNTHETIC sequence relates action, reaction and choice'}
  for layer in ['TECHNICAL','ARTISTIC']:
   e={key:'' for key in SCHEMA['tables']['Evaluation Results']['columns']}
   e.update(id='AUDIT-REGISTRY-EVAL-'+layer,project_id=row['project_id'],episode_id=row['episode_id'],revision=1,updated_at='2026-11-24T10:00:00Z',updated_by='independent-auditor',is_test=True,last_op_id='SYNTHETIC-REVIEW',target_table='Artifact Registry',target_id=row['id'],target_revision=row['revision'],department='direction',rubric_ref='judgment-engine/rubrics.json#RUB-DIRECTION',reviewer='independent-auditor',technical_result=json.dumps(technical_result),artistic_result=json.dumps(artistic_result),evidence='SYNTHETIC scoped review of exact fixture revision',limitations='Synthetic local contract; no audiovisual or human result',decision='REVIEW_ONLY',status='REVIEW_REQUIRED')
   self.s['tables']['Evaluation Results'].append(e);ids.append(e['id'])
  return {'technical_review_id':ids[0],'artistic_review_id':ids[1],'approval_id':next(a['id'] for a in self.s['tables']['Approvals'] if a['gate_id']=='G10')}

 def test_registry_draft_creation_is_only_a_plan(self):
  row=self.registry_state();self.s['tables']['Artifact Registry']=[]
  values={k:v for k,v in row.items() if k not in {'id','revision','updated_at','updated_by','last_op_id'}};values['status']='DRAFT'
  intent=self.intent([{'table':'Artifact Registry','id':row['id'],'expected_revision':None,'values':values}])
  p=validate_artistic_approval(self.s,intent)
  self.assertEqual(p['kind'],'WRITE_PLAN_NOT_SAVED');self.assertEqual(p['candidate']['tables']['Artifact Registry'][0]['status'],'DRAFT')

 def test_new_registry_target_cannot_be_created_as_approved(self):
  row=self.registry_state();r=self.registry_review(row);self.s['tables']['Artifact Registry']=[]
  values={k:v for k,v in row.items() if k not in {'id','revision','updated_at','updated_by','last_op_id'}};values['status']='APPROVED'
  with self.assertRaises(StateError):validate_artistic_approval(self.s,self.intent([{'table':'Artifact Registry','id':row['id'],'expected_revision':None,'values':values}]),r)

 def test_registry_approval_requires_current_review(self):
  row=self.registry_state();refs=self.registry_evaluations(row)
  with self.assertRaises(StateError):validate_artistic_approval(self.s,self.intent([{'table':'Artifact Registry','id':row['id'],'expected_revision':row['revision'],'values':{'status':'APPROVED',**refs}}]))

 def test_registry_approval_with_current_structured_reviews_is_local_plan(self):
  row=self.registry_state();refs=self.registry_evaluations(row)
  intent=self.intent([{'table':'Artifact Registry','id':row['id'],'expected_revision':row['revision'],'values':{'status':'APPROVED',**refs}}])
  p=validate_artistic_approval(self.s,intent,self.registry_review(row,'G10'))
  approved=p['candidate']['tables']['Artifact Registry'][0]
  self.assertEqual(p['kind'],'WRITE_PLAN_NOT_SAVED');self.assertEqual(approved['status'],'APPROVED');self.assertEqual(approved['gate_id'],'G10');self.assertEqual(approved['sha256'],row['sha256'])
  self.assertEqual(row['status'],'REVIEW_REQUIRED');self.assertTrue(validate(p['candidate']))

 def test_registry_approval_rejects_stale_persisted_evaluation_revision(self):
  row=self.registry_state();refs=self.registry_evaluations(row);row['revision']+=1
  intent=self.intent([{'table':'Artifact Registry','id':row['id'],'expected_revision':row['revision'],'values':{'status':'APPROVED',**refs}}])
  with self.assertRaises(StateError):validate_artistic_approval(self.s,intent,self.registry_review(row,'G10'))

 def test_registry_live_review_content_hash_must_match_artifact(self):
  row=self.registry_state();r=self.registry_review(row);r['target']['sha256']=digest('SYNTHETIC other bytes')
  with self.assertRaises(StateError):validate_artistic_approval(self.s,self.intent(self.gate_changes()),r)

 def test_registry_stale_record_hash_cannot_support_qc(self):
  row=self.registry_state();r=self.registry_review(row);r['target']['record_sha256']=digest('SYNTHETIC stale record')
  with self.assertRaises(StateError):validate_artistic_approval(self.s,self.intent(self.gate_changes()),r)

 def test_registry_qc_g14_can_review_origin_g10_without_mutating_origin(self):
  row=self.registry_state();before=copy.deepcopy(row)
  p=validate_artistic_approval(self.s,self.intent(self.gate_changes()),self.registry_review(row))
  self.assertTrue(validate(p['candidate']))
  self.assertEqual(next(w for w in p['candidate']['tables']['Workflow'] if w['gate_id']=='G14')['status'],'APPROVED')
  self.assertEqual(p['candidate']['tables']['Artifact Registry'][0],before)
  self.assertEqual(row['gate_id'],'G10')

 def test_registry_qc_requires_matching_review_gate_id(self):
  row=self.registry_state()
  with self.assertRaises(StateError):validate_artistic_approval(self.s,self.intent(self.gate_changes()),self.registry_review(row,'G13'))

 def test_registry_qc_rejects_stale_target_revision(self):
  row=self.registry_state();r=self.registry_review(row);row['revision']+=1
  with self.assertRaises(StateError):validate_artistic_approval(self.s,self.intent(self.gate_changes()),r)

 def test_registry_cannot_link_failed_reviews_as_approved_evidence(self):
  row=self.registry_state();refs=self.registry_evaluations(row,'FAIL','UNKNOWN');row.update(status='APPROVED',**refs)
  with self.assertRaises(StateError):validate(self.s)

 def test_registry_unrelated_g0_approval_cannot_approve_g10_material(self):
  row=self.registry_state();refs=self.registry_evaluations(row);refs['approval_id']=next(a['id'] for a in self.s['tables']['Approvals'] if a['gate_id']=='G0');row.update(status='APPROVED',**refs)
  with self.assertRaises(StateError):validate(self.s)

if __name__=='__main__':unittest.main()
