import copy,json,pathlib,sys,unittest
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/'scripts'))
from shared_state import validate,prepare,check_guards,verify_readback,StateError,Conflict,fingerprint,GATES
ROOT=pathlib.Path(__file__).resolve().parents[1]

class Shared(unittest.TestCase):
 def setUp(self):
  self.s=json.loads((ROOT/'templates/shared-state.test-fixture.json').read_text(encoding='utf-8'));self.s['spreadsheet_id']='TEST-SHEET'
 def intent(self,changes=None):return dict(op_id='OP-TEST-1',actor='test-agent',authorized=True,user_message_ref='test-user-message',at='2026-11-24T01:00:00Z',changes=changes or [dict(table='Decisions',id='TEST-D-ROUNDTRIP',expected_revision=1,values={'choice':'TEST-CHANGE','status':'RECORDED'})])
 def test_initial(self):self.assertTrue(validate(self.s))
 def test_duplicate_key(self):
  self.s['tables']['Decisions'].append(copy.deepcopy(self.s['tables']['Decisions'][0]))
  with self.assertRaises(StateError):validate(self.s)
 def test_foreign_project(self):
  self.s['tables']['Props'][0]['project_id']='ABSENT'
  with self.assertRaises(StateError):validate(self.s)
 def test_test_isolation(self):
  self.s['tables']['Props'][0]['is_test']=False
  with self.assertRaises(StateError):validate(self.s)
 def test_no_credits(self):
  self.s['tables']['Projects'][0]['credits_allowed']=1
  with self.assertRaises(StateError):validate(self.s)
 def test_manual_only(self):
  self.s['tables']['Projects'][0]['generation_mode']='automatic'
  with self.assertRaises(StateError):validate(self.s)
 def test_checklist_evidence(self):
  self.s['tables']['Checklists'][0]['checked']=True
  with self.assertRaises(StateError):validate(self.s)
 def test_inaccessible_not_checked(self):
  self.s['tables']['Checklists'][0].update(checked=True,evidence='not seen',observed_or_planned='not_accessible')
  with self.assertRaises(StateError):validate(self.s)
 def test_approval_requires_message(self):
  self.s['tables']['Approvals'][0].update(status='RECORDED',decision='APPROVE')
  with self.assertRaises(StateError):validate(self.s)
 def test_prepare_immutable_source(self):
  before=copy.deepcopy(self.s);p=prepare(self.s,self.intent());self.assertEqual(before,self.s);self.assertEqual(p['kind'],'WRITE_PLAN_NOT_SAVED');self.assertEqual(p['candidate']['tables']['Decisions'][0]['revision'],2)
 def test_missing_authorization(self):
  i=self.intent();i['authorized']=False
  with self.assertRaises(StateError):prepare(self.s,i)
 def test_stale_revision(self):
  i=self.intent();i['changes'][0]['expected_revision']=0
  with self.assertRaises(StateError):prepare(self.s,i)
 def test_conflict_manual_edit_without_revision(self):
  p=prepare(self.s,self.intent());fresh=copy.deepcopy(self.s);fresh['tables']['Decisions'][0]['rationale']='edited in sheets'
  with self.assertRaises(Conflict):check_guards(p,fresh)
 def test_conflict_membership(self):
  p=prepare(self.s,self.intent());fresh=copy.deepcopy(self.s);r=copy.deepcopy(fresh['tables']['Decisions'][0]);r['id']='NEW-ID';fresh['tables']['Decisions'].append(r)
  with self.assertRaises(Conflict):check_guards(p,fresh)
 def test_sort_rows_not_conflict(self):
  p=prepare(self.s,self.intent());fresh=copy.deepcopy(self.s);fresh['tables']['Workflow'].reverse();self.assertTrue(check_guards(p,fresh))
 def test_wrong_binding(self):
  p=prepare(self.s,self.intent());fresh=copy.deepcopy(self.s);fresh['spreadsheet_id']='OTHER'
  with self.assertRaises(Conflict):check_guards(p,fresh)
 def test_partial_write_never_confirmed(self):
  p=prepare(self.s,self.intent());self.s['read_at']='2026-11-24T02:00:00Z'
  with self.assertRaises(StateError):verify_readback(p,self.s)
 def test_readback_no_journal_not_complete(self):
  p=prepare(self.s,self.intent());fresh=p['candidate'];fresh['read_at']='2026-11-24T02:00:00Z';r=verify_readback(p,fresh);self.assertEqual(r['status'],'DATA_VERIFIED_HISTORY_PENDING');self.assertFalse(r['atomic'])
  with self.assertRaises(StateError):verify_readback(p,fresh,True)
 def test_no_blind_retry(self):
  self.s['tables']['Revision History'][0]['op_id']='OP-TEST-1'
  with self.assertRaises(StateError):prepare(self.s,self.intent())
 def test_immutable_locked_asset(self):
  self.s['tables']['Characters'][0].update(status='LOCKED',asset_ref='test-reference.svg')
  with self.assertRaises(StateError):prepare(self.s,self.intent([dict(table='Characters',id='TEST-CH-1',expected_revision=1,values={'identity':'changed'})]))
 def test_no_direct_gate_approval(self):
  with self.assertRaises(StateError):prepare(self.s,self.intent([dict(table='Workflow',id='TEST-WF-G0',expected_revision=1,values={'status':'APPROVED'})]))
 def test_cannot_skip_critical(self):
  with self.assertRaises(StateError):prepare(self.s,self.intent([dict(table='Workflow',id='TEST-WF-G0',expected_revision=1,values={'status':'SKIPPED','evidence':'reuse','reason':'reuse','deliverable_ref':'fixture'})]))
 def test_revision_requires_descendants(self):
  with self.assertRaises(StateError):prepare(self.s,self.intent([dict(table='Workflow',id='TEST-WF-G0',expected_revision=1,values={'status':'CHANGES_REQUESTED','reason':'change'})]))
 def test_missing_table_coverage(self):
  del self.s['tables']['Props']
  with self.assertRaises(StateError):validate(self.s)
 def test_unknown_column(self):
  self.s['tables']['Decisions'][0]['unexpected']='x'
  with self.assertRaises(StateError):validate(self.s)
 def test_bool_not_revision(self):
  self.s['tables']['Decisions'][0]['revision']=True
  with self.assertRaises(StateError):validate(self.s)
 def test_readback_predates_write(self):
  p=prepare(self.s,self.intent())
  with self.assertRaises(StateError):verify_readback(p,p['candidate'])

if __name__=='__main__':unittest.main()
