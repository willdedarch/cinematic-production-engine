import unittest, sys, pathlib
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/'scripts'))
from studio_state import new,change,validate,BY
class Studio(unittest.TestCase):
 def setUp(self):self.s=new('test','1')
 def approve(self,s,id):return change(change(s,id,'review','checked with evidence',[True]*len(BY[id]['checks'])),id,'approve')
 def test_initial(self):self.assertTrue(validate(self.s))
 def test_no_credits(self):
  self.s['credits_allowed']=1
  with self.assertRaises(AssertionError):validate(self.s)
 def test_no_approval_without_review(self):
  with self.assertRaises(AssertionError):change(self.s,'G0','approve')
 def test_dependency(self):
  with self.assertRaises(AssertionError):self.approve(self.s,'G1')
 def test_checklist(self):
  with self.assertRaises(AssertionError):change(change(self.s,'G0','review','evidence'),'G0','approve')
 def test_evidence(self):
  with self.assertRaises(AssertionError):change(change(self.s,'G0','review','',[True]*4),'G0','approve')
 def test_skip_critical(self):
  with self.assertRaises(AssertionError):change(self.s,'G0','skip','reason')
 def test_skip_permitted(self):self.assertEqual(change(self.approve(self.s,'G0'),'G1','skip','reuse')['gates']['G1']['status'],'SKIPPED')
 def test_lock(self):self.assertEqual(change(self.approve(self.s,'G0'),'G0','lock')['gates']['G0']['status'],'LOCKED')
 def test_invalidation(self):
  s=self.approve(self.approve(self.s,'G0'),'G1');s=change(s,'G1','lock');s=change(s,'G0','revise','change');self.assertEqual(s['gates']['G1']['status'],'CHANGES_REQUESTED');self.assertEqual(s['gates']['G1']['revision'],2)
 def test_revision_reason(self):
  with self.assertRaises(AssertionError):change(self.s,'G0','revise')
 def test_full_path(self):
  s=self.s
  for id in BY:s=self.approve(s,id)
  self.assertTrue(validate(s))
