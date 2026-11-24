"""Independent regressions for concrete pre-Judgment review findings.

Synthetic in-memory fixtures only; no connector, UI browser, generation or human
approval is simulated as a real production result.
"""
import copy
import json
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from shared_state import SCHEMA,StateError,validate,prepare,verify_readback
from prompt_compiler import CompileError,compile_prompt

class IndependentReviewRegressions(unittest.TestCase):
 def setUp(self):
  self.snapshot=json.loads((ROOT/'templates/shared-state.test-fixture.json').read_text(encoding='utf-8'))
  self.seed=json.loads((ROOT/'templates/library-seed.json').read_text(encoding='utf-8'))

 def intent(self,table='Decisions',id='TEST-D-ROUNDTRIP',values=None):
  return {'op_id':'INDEPENDENT-REVIEW-TEST','actor':'independent-test-agent','authorized':True,'user_message_ref':'SYNTHETIC-USER-MESSAGE','at':'2026-11-24T09:00:00Z','changes':[{'table':table,'id':id,'expected_revision':1,'values':values or {'choice':'synthetic update'}}]}

 def knowledge(self,status):
  row=copy.deepcopy(self.seed['tables']['Techniques'][0])
  row.update(project_id='TEST-CPE31',episode_id='',is_test=True,status=status)
  self.snapshot['tables']['Techniques']=[row]
  return row

 def approved_gate_fixture(self):
  w=next(x for x in self.snapshot['tables']['Workflow'] if x['gate_id']=='G0')
  w.update(status='APPROVED',evidence='synthetic observed evidence',deliverable_ref='synthetic-brief')
  for check in self.snapshot['tables']['Checklists']:
   if check['gate_id']=='G0':check.update(checked=True,evidence='synthetic observation')
  a=self.snapshot['tables']['Approvals'][0]
  a.update(workflow_id=w['id'],gate_id='G0',gate_revision=w['revision'],decision='APPROVE',approver='synthetic test human',user_message_ref='SYNTHETIC-USER-MESSAGE',evidence='synthetic test evidence',status='RECORDED')
  return w,a

 def evaluation(self):
  cols=SCHEMA['tables']['Evaluation Results']['columns']
  row={key:'' for key in cols}
  target=self.snapshot['tables']['Screenplays'][0]
  row.update(id='INDEPENDENT-EVAL-1',project_id='TEST-CPE31',episode_id=target['episode_id'],revision=1,updated_at='2026-11-24T09:00:00Z',updated_by='independent-test-agent',is_test=True,last_op_id='SYNTHETIC-EVAL',target_table='Screenplays',target_id=target['id'],target_revision=target['revision'],department='story',rubric_ref='synthetic-rubric',reviewer='independent-test-agent',technical_result='synthetic technical pass',artistic_result='synthetic artistic review',evidence='synthetic text locator',limitations='No real media or human review',decision='REVIEW_ONLY',status='DRAFT')
  self.snapshot['tables']['Evaluation Results']=[row]
  return row

 def journal(self,plan,event,id):
  cols=SCHEMA['tables']['Revision History']['columns']
  row={key:'' for key in cols}
  row.update(id=id,project_id='TEST-CPE31',episode_id='',revision=1,updated_at='2026-11-24T09:01:00Z',updated_by=plan['actor'],is_test=True,last_op_id=plan['op_id'],op_id=plan['op_id'],event=event,actor=plan['actor'],authorization_ref=plan['authorization_ref'],changes_json=json.dumps(plan['changes'],ensure_ascii=False),guards_json=json.dumps(plan['guards'],ensure_ascii=False),result='SYNTHETIC local test only',evidence_ref='synthetic-memory')
  return row

 def test_locked_knowledge_content_cannot_change(self):
  row=self.knowledge('LOCKED')
  self.assertTrue(validate(self.snapshot))
  with self.assertRaises(StateError):prepare(self.snapshot,self.intent('Techniques',row['id'],{'procedure':'overwritten locked content'}))

 def test_approved_knowledge_content_cannot_change(self):
  row=self.knowledge('APPROVED')
  with self.assertRaises(StateError):prepare(self.snapshot,self.intent('Techniques',row['id'],{'example':'overwritten approved example'}))

 def test_approved_knowledge_can_be_locked_without_content_edit(self):
  row=self.knowledge('APPROVED')
  plan=prepare(self.snapshot,self.intent('Techniques',row['id'],{'status':'LOCKED'}))
  self.assertEqual(plan['changes'][0]['after']['procedure'],row['procedure'])

 def test_correct_approval_scope_is_valid(self):
  self.approved_gate_fixture()
  self.assertTrue(validate(self.snapshot))

 def test_wrong_gate_id_does_not_approve_another_gate(self):
  _,a=self.approved_gate_fixture();a['gate_id']='G5'
  with self.assertRaises(StateError):validate(self.snapshot)

 def test_blank_episode_does_not_approve_episode_gate(self):
  _,a=self.approved_gate_fixture();a['episode_id']=''
  with self.assertRaises(StateError):validate(self.snapshot)

 def test_evaluation_target_must_exist(self):
  row=self.evaluation();row.update(target_table='NoSuchTable',target_id='NoSuchTarget',target_revision=999,status='APPROVED')
  with self.assertRaises(StateError):validate(self.snapshot)

 def test_evaluation_revision_cannot_be_from_future(self):
  self.evaluation()['target_revision']=999
  with self.assertRaises(StateError):validate(self.snapshot)

 def test_evaluation_requires_evidence(self):
  self.evaluation()['evidence']=''
  with self.assertRaises(StateError):validate(self.snapshot)

 def test_evaluation_requires_rubric_and_reviewer(self):
  row=self.evaluation()
  for key in ['rubric_ref','reviewer']:
   before=row[key];row[key]=''
   with self.assertRaises(StateError):validate(self.snapshot)
   row[key]=before

 def test_evaluation_scope_matches_target(self):
  self.evaluation()['episode_id']=''
  with self.assertRaises(StateError):validate(self.snapshot)

 def test_valid_evaluation_accepted(self):
  self.evaluation();self.assertTrue(validate(self.snapshot))

 def test_approved_evaluation_remains_valid_history_after_target_advances(self):
  row=self.evaluation();row['status']='APPROVED'
  target=self.snapshot['tables']['Screenplays'][0]
  target['revision']+=1
  self.assertLess(row['target_revision'],target['revision'])
  self.assertTrue(validate(self.snapshot))

 def test_knowledge_successor_preserves_locked_predecessor(self):
  previous=self.knowledge('LOCKED')
  successor=copy.deepcopy(previous);successor.update(id='INDEPENDENT-TECH-SUCCESSOR',status='DRAFT',supersedes_id=previous['id'],procedure='Localized revised procedure')
  self.snapshot['tables']['Techniques'].append(successor)
  self.assertTrue(validate(self.snapshot))
  self.assertEqual(previous['status'],'LOCKED')
  self.assertNotEqual(successor['procedure'],previous['procedure'])

 def test_knowledge_lineage_missing_predecessor_rejected(self):
  row=self.knowledge('DRAFT');row['supersedes_id']='NO-SUCH-PREDECESSOR'
  with self.assertRaises(StateError):validate(self.snapshot)

 def test_knowledge_lineage_cycle_rejected(self):
  row=self.knowledge('DRAFT')
  successor=copy.deepcopy(row);successor.update(id='INDEPENDENT-TECH-SUCCESSOR',supersedes_id=row['id'])
  row['supersedes_id']=successor['id'];self.snapshot['tables']['Techniques'].append(successor)
  with self.assertRaises(StateError):validate(self.snapshot)

 def test_unbound_confirmation_never_confirms_history(self):
  plan=prepare(self.snapshot,self.intent());fresh=copy.deepcopy(plan['candidate']);fresh['read_at']='2026-11-24T09:02:00Z'
  row=self.journal(plan,'CONFIRMED','INDEPENDENT-H-FAKE');row.update(actor='unrelated-agent',authorization_ref='',changes_json='{}',guards_json='{}')
  fresh['tables']['Revision History'].append(row)
  with self.assertRaises(StateError):verify_readback(plan,fresh,True)

 def test_confirmation_without_prepared_is_incomplete(self):
  plan=prepare(self.snapshot,self.intent());fresh=copy.deepcopy(plan['candidate']);fresh['read_at']='2026-11-24T09:02:00Z'
  fresh['tables']['Revision History'].append(self.journal(plan,'CONFIRMED','INDEPENDENT-H-CONFIRMED'))
  with self.assertRaises(StateError):verify_readback(plan,fresh,True)

 def test_both_bound_journal_events_confirm(self):
  plan=prepare(self.snapshot,self.intent());fresh=copy.deepcopy(plan['candidate']);fresh['read_at']='2026-11-24T09:02:00Z'
  fresh['tables']['Revision History'] += [self.journal(plan,'PREPARED','INDEPENDENT-H-PREPARED'),self.journal(plan,'CONFIRMED','INDEPENDENT-H-CONFIRMED')]
  receipt=verify_readback(plan,fresh,True)
  self.assertEqual(receipt['status'],'CONFIRMED');self.assertFalse(receipt['atomic'])

 def test_corrupt_changes_or_guards_never_confirm(self):
  plan=prepare(self.snapshot,self.intent())
  for key in ['changes_json','guards_json']:
   fresh=copy.deepcopy(plan['candidate']);fresh['read_at']='2026-11-24T09:02:00Z'
   prepared=self.journal(plan,'PREPARED','INDEPENDENT-H-PREPARED');confirmed=self.journal(plan,'CONFIRMED','INDEPENDENT-H-CONFIRMED');confirmed[key]='{}'
   fresh['tables']['Revision History'] += [prepared,confirmed]
   with self.assertRaises(StateError):verify_readback(plan,fresh,True)

 def test_seedance_extension_direction_must_be_non_null(self):
  spec={'model_id':'seedance_2_5','parameters':{'mode':'video_extension','extension_mode':None},'intent':{'initial_state':'A room','action':'Person walks'},'references':[{'id':'v1','uri':'provided.mp4','role':'video_references','rights_confirmed':True}]}
  with self.assertRaises(CompileError):compile_prompt(spec)
  spec['parameters']['extension_mode']='forward'
  self.assertEqual(compile_prompt(spec)['native_parameters']['extension_mode'],'forward')

if __name__=='__main__':unittest.main()
