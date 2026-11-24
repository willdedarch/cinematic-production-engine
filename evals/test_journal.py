import unittest,json,copy,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
from shared_state import prepare,verify_readback,StateError
from journal import journal_rows
class ChunkJournal(unittest.TestCase):
 def setup_plan(self):
  s=json.loads((R/'templates/shared-state.test-fixture.json').read_text(encoding='utf-8'));old=s['tables']['Decisions'][0];new={k:v for k,v in old.items() if k not in {'id','revision','updated_at','updated_by','last_op_id'}};new.update(choice='Y'*39000,status='DRAFT')
  i={'op_id':'CHUNK-TEST','actor':'test','authorized':True,'user_message_ref':'SIMULATED:unit','at':'2026-11-25T00:00:00Z','changes':[{'table':'Decisions','id':old['id'],'expected_revision':1,'values':{'choice':'X'*39000}},{'table':'Decisions','id':'TEST-LARGE-NEW','expected_revision':None,'values':new}]};p=prepare(s,i);f=copy.deepcopy(p['candidate']);f['read_at']='2026-11-25T01:00:00Z'
  for event in ['PREPARED','CONFIRMED']:f['tables']['Revision History']+=journal_rows(p,event,'TEST-CPE31','TEST-CPE31-EP1',True,'2026-11-25T00:30:00Z','fixture:chunk')
  return p,f
 def test_large_operation_chunked_and_verified(self):
  p,f=self.setup_plan();self.assertEqual(len(f['tables']['Revision History']),5);self.assertEqual(verify_readback(p,f,True)['status'],'CONFIRMED')
 def test_missing_chunk_not_confirmed(self):
  p,f=self.setup_plan();f['tables']['Revision History'].pop();self.assertRaises(StateError,verify_readback,p,f,True)
 def test_digest_tamper_not_confirmed(self):
  p,f=self.setup_plan();f['tables']['Revision History'][-1]['guards_json']='{"algorithm":"sha256-canonical","digest":"wrong"}';self.assertRaises(StateError,verify_readback,p,f,True)
 def test_cells_below_limit(self):
  _,f=self.setup_plan()
  for r in f['tables']['Revision History']:self.assertLess(len(r['changes_json']),45000)
if __name__=='__main__':unittest.main()
