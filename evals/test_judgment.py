import json,unittest,sys,copy
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from judgment import *
class JudgmentTests(unittest.TestCase):
 def raw_review(self):
  return {'id':'r1','project_id':'p','episode_id':'e','department':'story','reviewer':'critic-1','creator_id':'creator-1','mode':'independent_agent','target':{'id':'a','revision':1,'sha256':digest('fixture')},'context':{'intention':'dignidade na partilha','genre':'war drama','format':'60s','target_level':4},'technical':{'status':'PASS','checks':[{'criterion':'causalidade espacial','status':'PASS','observation':'W1/E1/N1 conservados','evidence_ref':'fixture:line1'}]},'artistic':{'status':'CHANGES_REQUESTED','level':3,'rationale':'Escolha legível, mas reação de Lia apenas descrita','observations':[{'criterion':'emoção encenada','observation':'Lia não age depois da oferta','evidence_ref':'fixture:line2','interpretation':'A relação não se transforma de modo observável'}],'strengths':['geografia clara'],'problems':['consequência incompleta'],'integration':''},'adversarial':{'challenge':'A emoção aparece em ação?','successful_choice':'A oferta tem custo material'},'limitations':['Texto didático, sem atuação filmada']}
 def session(self):return blind_packets([{'material_id':'m1','text':'Texto curto com escolha'},{'material_id':'m2','text':'Texto muito longo sem consequência'}],{'intention':'escolha legível'})
 def review(self):
  r=self.raw_review();rr=rubric('story');r['rubric_sha256']=digest(rr);r['artistic']['observations']=[{**r['artistic']['observations'][0],'criterion':c} for c in rr['criteria']];return r
 def votes(self,s,choices):return [{'reviewer':'critic','packet_id':p['packet_id'],'choice':c,'rationale':'A consequência muda a relação','evidence':['gesto no texto']} for p,c in zip(s['public_packets'],choices)]
 def test_technical_pass_does_not_approve(self):self.assertEqual(validate_review(self.review())['recommendation'],'CHANGES_REQUESTED')
 def test_unknown_art_has_no_score(self):
  r=self.review();r['artistic'].update(status='UNKNOWN',level=None);self.assertEqual(validate_review(r)['recommendation'],'INCOMPLETE_EVIDENCE')
 def test_no_evidence_rejected(self):
  r=self.review();r['artistic']['observations'][0]['evidence_ref']='';self.assertRaises(JudgmentError,validate_review,r)
 def test_excellence_needs_integration(self):
  r=self.review();r['artistic'].update(level=4,status='RECOMMEND_APPROVAL');self.assertRaises(JudgmentError,validate_review,r)
 def test_ready_still_not_approved(self):
  r=self.review();r['artistic'].update(level=4,status='RECOMMEND_APPROVAL',integration='Gesto e espaço constroem reciprocidade, em vez de declará-la');x=validate_review(r);self.assertEqual(x['recommendation'],'READY_FOR_HUMAN_DECISION');self.assertFalse(x['approved'])
 def test_independence_not_self(self):
  r=self.review();r['reviewer']=r['creator_id'];self.assertRaises(JudgmentError,validate_review,r)
 def test_blind_packets_strip_metadata(self):
  s=blind_packets([{'material_id':'v1','text':'x','author':'name','version':'best'},{'material_id':'v2','text':'y','author':'name2'}],{});self.assertEqual(set(s['public_packets'][0]['alternatives'][0]),{'label','text'});self.assertNotIn('best',json.dumps(s['public_packets']))
 def test_reversal_maps_correct_winner(self):
  s=self.session();self.assertEqual(consolidate(s,self.votes(s,['A','B']))['outcome'],'m1')
 def test_tie(self):
  s=self.session();self.assertEqual(consolidate(s,self.votes(s,['TIE','TIE']))['outcome'],'TIE')
 def test_both_fail(self):
  s=self.session();self.assertEqual(consolidate(s,self.votes(s,['BOTH_FAIL','BOTH_FAIL']))['outcome'],'BOTH_FAIL')
 def test_position_sensitive_unresolved(self):
  s=self.session();self.assertEqual(consolidate(s,self.votes(s,['A','A']))['outcome'],'UNRESOLVED')
 def test_one_order_not_enough(self):
  s=self.session();self.assertRaises(JudgmentError,consolidate,s,self.votes(s,['A']))
 def test_duplicate_votes(self):
  s=self.session();v=self.votes(s,['A','B']);self.assertRaises(JudgmentError,consolidate,s,v+v)
 def test_no_fabricated_human_metrics(self):
  x=metrics([{'human_origin':'SIMULATED','agent_decision':'APPROVE','human_decision':'APPROVE'}]);self.assertEqual(x['real_human_n'],0);self.assertIsNone(x['human_agreement'])
 def test_empty_baseline(self):self.assertIsNone(metrics([])['false_approval_rate'])
 def test_loop_limit_never_approves(self):
  x=revision_decision({'round':2,'max_rounds':2});self.assertFalse(x['auto_approve']);self.assertEqual(x['next'],'PRESENT_UNRESOLVED_TO_USER')
 def test_protected_change_rejected(self):self.assertRaises(JudgmentError,revision_decision,{'round':0,'changed_elements':['E1'],'protected_elements':['E1']})
 def test_department_selective(self):self.assertNotIn('Cinematography Critic',roles('dialogue'))
 def test_review_binds_actual_rubric(self):
  r=self.review();r['rubric_sha256']='stale';self.assertRaises(JudgmentError,validate_review,r)
 def test_partial_criteria_rejected(self):
  r=self.review();r['artistic']['observations'].pop();self.assertRaises(JudgmentError,validate_review,r)
 def test_28_rubrics_and_140_calibrators(self):
  rubrics=json.loads((ROOT/'judgment-engine/rubrics.json').read_text(encoding='utf-8'))['rubrics'];ex=json.loads((ROOT/'judgment-engine/calibration-examples.json').read_text(encoding='utf-8'))['examples'];self.assertEqual({r['department'] for r in rubrics},set(ROLES));self.assertEqual(len(ex),140)
 def test_holdout_packet_excludes_calibration(self):
  s={'department':'story','target':{'id':'holdout','revision':1,'path':str(ROOT/'judgment-engine/benchmark-public-packets.json')},'context':{'intention':'test'},'holdout':True};p=review_packet(s);self.assertEqual(p['calibration'],[]);self.assertTrue(p['rubric_sha256']);self.assertIsNone(p['observed_quality'])
 def test_empty_diagnosis_not_validated(self):
  d={k:'' for k in ['symptom','evidence','probable_cause','alternatives','missing_evidence','confidence','repair','risks','protected','verification']};d.update(symptom='Plano parece plano',confidence='LOW',alternatives=[''],verification=['']);self.assertRaises(JudgmentError,diagnosis,d)
 def test_duplicate_human_labels_not_inflate_n(self):
  r={'id':'feedback-1','human_origin':'REAL_USER','user_message_ref':'fixture:real-label-example','evidence_ref':'fixture:observation','agent_decision':'APPROVE','human_decision':'REJECT'};self.assertRaises(JudgmentError,metrics,[r,r])
if __name__=='__main__':unittest.main()
