import unittest,sys,tempfile,json,copy
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
from harness_runtime import *
class HarnessTests(unittest.TestCase):
 def setUp(self):self.s=json.loads((R/'templates/shared-state.test-fixture.json').read_text(encoding='utf-8'));self.tmp=tempfile.TemporaryDirectory();self.d=Path(self.tmp.name)
 def tearDown(self):self.tmp.cleanup()
 def test_policy_valid(self):self.assertEqual(policies()['production']['credits_allowed'],0)
 def test_policy_forbids_paid(self):
  p=policies();p['production']['credits_allowed']=100;s=json.loads((R/'schemas/policies.schema.json').read_text(encoding='utf-8'));self.assertRaises(StateError,schema_check,p,s)
 def test_unsupported_schema_keyword(self):self.assertRaises(StateError,schema_check,{}, {'type':'object','unsupported':True})
 def test_local_allowed(self):self.assertTrue(cost_guard('optics')['allowed'])
 def test_paid_external_prohibited(self):
  for name in ['higgsfield.generate_video','higgsfield.generate_image','runpod.gpu_rent','unknown.external','final_auto_generation']:self.assertRaises(StateError,cost_guard,name)
 def test_native_scope_required(self):self.assertRaises(StateError,cost_guard,'native_concept_image')
 def test_native_authorized_bounded(self):
  a={'authorized':True,'user_message_ref':'SIMULATED:experiment-scope','purpose':'VISUAL_DRAFT','max_variants':2};self.assertEqual(cost_guard('native_concept_image',a,1)['remaining_authorized'],1);self.assertRaises(StateError,cost_guard,'native_concept_image',a,2)
 def test_write_not_just_connector_access(self):self.assertRaises(StateError,cost_guard,'google_sheets.validated_write')
 def test_events_chain_detects_tamper(self):
  r=Run(self.d);r.event('before_stage','REQUESTED');r.event('after_stage','EXECUTED');p=r.dir/'events.jsonl';self.assertEqual(verify_events(p)['events'],2);p.write_text(p.read_text().replace('EXECUTED','APPROVED'));self.assertRaises(StateError,verify_events,p)
 def test_installation_not_state_workspace(self):self.assertRaises(StateError,Run,R/'projects')
 def test_context_actual_knowledge_and_scope(self):
  c=context(self.s,'TEST-CPE31','TEST-CPE31-EP1','G8',['design'],include_test=True);self.assertTrue(c['retrieved_hashes']);self.assertEqual(c['used_knowledge'],[]);self.assertFalse(c['remote_read_performed_by_cli'])
 def test_test_scope_explicit(self):self.assertRaises(StateError,context,self.s,'TEST-CPE31','TEST-CPE31-EP1','G0')
 def test_compact_panel_base(self):
  copy=panel_snapshot(self.s);p={'authorized':True,'spreadsheet_id':self.s['spreadsheet_id'],'base_scope_sha256':copy['scope_guards_sha256']};self.assertTrue(validate_panel_base(p,self.s)['valid_base'])
 def test_compact_panel_detects_manual_edit_without_revision(self):
  copy=panel_snapshot(self.s);p={'authorized':True,'spreadsheet_id':self.s['spreadsheet_id'],'base_scope_sha256':copy['scope_guards_sha256']};self.s['tables']['Decisions'][0]['rationale']='manual change';self.assertRaises(StateError,validate_panel_base,p,self.s)
 def test_checkpoint_recovery(self):
  x=checkpoint(self.s,self.d);saved=json.loads(Path(x['checkpoint']).read_text(encoding='utf-8'));self.assertEqual(saved['kind'],'LOCAL_UNSYNCHRONIZED_CHECKPOINT');self.assertEqual(recover(saved,self.s)['status'],'MATCHES_CURRENT_READ_COPY')
 def test_recovery_never_overwrites_divergence(self):
  x=checkpoint(self.s,self.d);saved=json.loads(Path(x['checkpoint']).read_text(encoding='utf-8'));self.s['tables']['Decisions'][0]['rationale']='changed outside';v=recover(saved,self.s);self.assertEqual(v['status'],'DIVERGENT_OR_NEWER_STATE_RECONCILE');self.assertFalse(v['overwrite_performed'])
 def test_corrupt_checkpoint(self):
  x=checkpoint(self.s,self.d);saved=json.loads(Path(x['checkpoint']).read_text(encoding='utf-8'));saved['snapshot']['tables']['Decisions'][0]['choice']='tamper';self.assertRaises(StateError,recover,saved,self.s)
 def test_import_final_requires_new_review(self):
  p=self.d/'asset.txt';p.write_text('owned fixture');x=import_asset(p,'FINAL_ASSET','ASSET-1',1,'Own test fixture',True);self.assertFalse(x['approved']);self.assertEqual(x['status'],'REVIEW_REQUIRED')
 def test_import_rights(self):
  p=self.d/'asset.txt';p.write_text('x');self.assertRaises(StateError,import_asset,p,'REFERENCE','A',1,'Unknown',False)
 def test_single_variable_experiment(self):
  e=json.loads((R/'templates/optical-experiment.json').read_text(encoding='utf-8'));x=experiment(e);self.assertTrue(x['single_variable_controlled']);self.assertIsNone(x['observed_result'])
 def test_confounded_experiment_marked(self):
  e=json.loads((R/'templates/optical-experiment.json').read_text(encoding='utf-8'));e['variants'][1]['settings']['distance_m']=5;self.assertFalse(experiment(e)['single_variable_controlled'])
 def test_native_experiment_without_authorization_not_run(self):
  e=json.loads((R/'templates/optical-experiment.json').read_text(encoding='utf-8'));e['tool']='native_image';self.assertRaises(StateError,experiment,e)
 def test_init_plan_has_all_gates_no_fake_assets(self):
  brief={'project_name':'New fiction','episode_title':'Opening','target_seconds':60};auth={'authorized':True,'user_message_ref':'SIMULATED:init','actor':'unit','op_id':'INIT-UNIT'};p=initialize(self.s,brief,auth);s=p['candidate'];self.assertEqual(len(s['tables']['Workflow']),32);self.assertEqual(len(s['tables']['Checklists']),106);self.assertEqual(len(s['tables']['Characters']),1);self.assertEqual(p['kind'],'WRITE_PLAN_NOT_SAVED')
if __name__=='__main__':unittest.main()
