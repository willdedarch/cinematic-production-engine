"""Release checks on the two-episode rehearsal and its normal reading paths."""
import copy
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from episode_workflow import initialize_episode
from knowledge_select import genre_case, select
from series_bible import check_assumptions, canon_plan, handoff
from shared_state import StateError, fingerprint, validate

example_spec = importlib.util.spec_from_file_location('worked_series', ROOT / 'examples/series-worked/run.py')
example = importlib.util.module_from_spec(example_spec)
example_spec.loader.exec_module(example)


class SeriesRelease(unittest.TestCase):
    first = 'SERIE-AGUA-EP1'
    second = 'SERIE-AGUA-EP2'
    project = 'SERIE-AGUA'

    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.temp.cleanup)
        cls.out = Path(cls.temp.name)
        cls.snapshot = example.scenario(cls.out)

    def update_knowledge(self, snapshot=None, previous='D-CANON-3'):
        fact = {'kind':'character_knowledge','subject':'DAVI','key':'chegada','value':'uma vizinha',
                'sequence':5,'beat':'SH12','previous_decision_id':previous}
        return canon_plan(snapshot or self.snapshot, {'project_id':self.project,'episode_id':self.second,
            'authorization':example.auth('TEST-REVEAL'), 'entries':[{'decision_id':'TEST-REVEAL',
                'reason':'Davi vê a vizinha na porta.','status':'RECORDED','fact':fact}]})['candidate']

    def test_series_cli_resume_checks_project_and_test_scope(self):
        state = self.out/'snapshot.json'
        state.write_text(json.dumps(self.snapshot),encoding='utf-8')
        def run(cmd,*extra):
            return subprocess.run([sys.executable,'-B',str(ROOT/'scripts/cpe.py'),cmd,
                                   '--workspace',str(self.out/'cli'), '--snapshot',str(state),
                                   '--episode',self.second,*extra],capture_output=True,encoding='utf-8')
        self.assertNotEqual(run('bible','--project',self.project).returncode,0)
        self.assertNotEqual(run('resume','--project','OUTRA-SERIE','--include-test').returncode,0)
        result=run('resume','--project',self.project,'--include-test')
        self.assertEqual(result.returncode,0,result.stderr)
        receipt=json.loads(Path(json.loads(result.stdout)['result']).read_text(encoding='utf-8'))
        self.assertEqual(receipt['episode_handoff']['episode_number'],2)
        self.assertEqual(receipt['episode_handoff']['facts']['relationship'][0]['value'],'recíproco')

    def test_ep2_handoff_distinguishes_authority_audience_people_and_props(self):
        bible = handoff(self.snapshot,self.project,self.second,before_episode=True)
        saved = json.loads((self.out/'handoff-ep2.json').read_text(encoding='utf-8'))
        self.assertEqual(saved,bible)
        self.assertEqual((len(bible['timeline']),len(bible['proposals'])),(8,1))
        self.assertEqual(bible['facts']['relationship'][0]['previous_decision_id'],'D-EARLY-CARE')
        self.assertIn('oferta unilateral de Davi',(self.out/'EP2/episode-guide.html').read_text(encoding='utf-8'))
        self.assertEqual(bible['facts']['audience_knowledge'][0]['subject'],'AUDIENCE')
        for fact in bible['timeline']:
            decision = next(r for r in self.snapshot['tables']['Decisions'] if r['id']==fact['source']['id'])
            self.assertEqual(fact['source']['record_sha256'],fingerprint(decision))
            self.assertEqual(fact['source']['reason'],decision['rationale'])
        self.assertEqual(bible['facts']['prop'][0]['value'],'Lia.direita')
        self.assertEqual(bible['facts']['location'][0]['value'],'W1 oeste')
        self.assertTrue(bible['facts']['relationship'])
        self.assertTrue(bible['facts']['open_question'])

    def test_future_reveal_does_not_leak_and_conflicts_have_source(self):
        snapshot = self.update_knowledge()
        subject = {'kind':'character_knowledge','subject':'DAVI','key':'chegada','value':'uma vizinha'}
        for episode,position,wanted,decision in [(self.first,None,'CONFLICT','D-CANON-3'),
                                                (self.second,4,'CONFLICT','D-CANON-3'),
                                                (self.second,5,'MATCH','TEST-REVEAL')]:
            with self.subTest(episode=episode,position=position):
                bible = handoff(snapshot,self.project,episode,through_sequence=position)
                row = check_assumptions(bible,[subject])[0]
                self.assertEqual((row['status'],row['decision']['id']),(wanted,decision))
        other = {**subject,'subject':'LIA'}
        self.assertEqual(check_assumptions(bible,[other])[0]['status'],'UNKNOWN')
        with self.assertRaisesRegex(StateError,'actual predecessor'):
            self.update_knowledge(previous='')

    def test_cross_project_and_test_real_isolation(self):
        other = 'SERIE-PRODUCAO'
        episode = other+'-EP1'
        snap = initialize_episode(self.snapshot,{'project_id':other,'project_name':'Produção separada',
            'episode_title':'Outro começo','target_seconds':20},example.auth('OUTRO'))['candidate']
        self.assertFalse(next(p['is_test'] for p in snap['tables']['Projects'] if p['id']==other))
        self.assertEqual(handoff(snap,other,episode)['timeline'],[])
        with self.assertRaisesRegex(StateError,'Episode not in project'):
            handoff(snap,self.project,episode)
        self.assertTrue(validate(snap))  # Each project has a first episode.
        for row in snap['tables']['Episodes']:
            if row['id']==self.second:row['episode_number']=1
        with self.assertRaisesRegex(StateError,'Duplicate episode number'):
            handoff(snap,self.project,self.second)

    def test_new_episode_reuses_project_and_keeps_earlier_versions(self):
        before = copy.deepcopy(self.snapshot)
        brief = {'project_id':self.project,'new_episode':True,'episode_title':'EP3','target_seconds':30}
        with self.assertRaisesRegex(StateError,'Explicit test scope'):
            initialize_episode(before,brief,example.auth('TEST-EP3'))
        plan = initialize_episode(before,{**brief,'include_test':True},example.auth('TEST-EP3'))
        self.assertEqual(self.snapshot,before)
        self.assertEqual(plan['kind'],'WRITE_PLAN_NOT_SAVED')
        self.assertEqual([c['table'] for c in plan['changes']].count('Projects'),0)
        self.assertEqual(len([c for c in plan['changes'] if c['table']=='Workflow']),16)
        self.assertEqual(len([c for c in plan['changes'] if c['table']=='Checklists']),53)
        self.assertEqual(plan['episode_handoff']['episode_number'],3)
        self.assertEqual(plan['candidate']['tables']['Episodes'][:2],self.snapshot['tables']['Episodes'])

    def test_unpositioned_legacy_record_cannot_spoil_a_timed_scene(self):
        snap = copy.deepcopy(self.snapshot)
        row = next(r for r in snap['tables']['Decisions'] if r['id']=='D-CANON-3').copy()
        row.update(id='LEGACY-EP2-UNTIMED',episode_id=self.second,topic='Mistério da vizinha',choice='Ela chegou.')
        snap['tables']['Decisions'].append(row)
        self.assertIn(row['id'],[r['source']['id'] for r in handoff(snap,self.project,self.second)['earlier_decisions']])
        limited = handoff(snap,self.project,self.second,through_sequence=2)
        self.assertNotIn(row['id'],[r['source']['id'] for r in limited['earlier_decisions']])

    def test_knowledge_ranking_reasons_scope_and_genre(self):
        self.assertEqual(genre_case('comedia com pausas')['genre'],'comédia')
        self.assertIsNone(genre_case('xyz'))
        snap = copy.deepcopy(self.snapshot)
        project = snap['tables']['Projects'][0]
        episode = snap['tables']['Episodes'][1]
        def item(name,project_id,episode_id,title,department):
            return {'id':name,'project_id':project_id,'episode_id':episode_id,'status':'APPROVED',
                    'title':title,'department':department,'context':title}
        snap['tables']['Reference Library']=[
            item('LOCAL',self.project,self.second,'Pausa antes do olhar','performance'),
            item('GLOBAL','LIB-CPE31','','O corte depois da pausa','editing'),
            item('ERRADO','OUTRA-SERIE','','Pausa antes do olhar','performance'),
            item('EP1',self.project,self.first,'Pausa antes do olhar','performance')]
        results,reasons = select(snap,project,episode,'G7',[],'','Pausa antes do olhar')
        self.assertEqual([r['id'] for r in results['Reference Library']],['LOCAL','GLOBAL'])
        self.assertTrue(any('intenção' in r for r in reasons['Reference Library'][0]['why']))

    def test_demonstration_emits_six_shots_and_actual_local_media(self):
        shots = self.snapshot['tables']['Shot List']
        self.assertEqual(sorted((s['id'],s['duration_s']) for s in shots),[('SH01',8),('SH02',10),('SH03',12),('SH04',8),('SH05',12),('SH06',10)])
        sample = next(r for r in self.snapshot['tables']['Artifact Registry'] if r['id']=='TAKE-06')
        self.assertTrue(Path(sample['uri']).is_file())
        self.assertEqual(sample['status'],'REVIEW_REQUIRED')
        for shot in shots:
            manual = json.loads((self.out/(shot['id']+'-manual.json')).read_text(encoding='utf-8'))
            self.assertEqual(manual['delivery']['model_id'],'seedance_2_5')
            self.assertTrue(manual['attachment_order'])
        self.assertEqual(len(self.snapshot['tables']['Prompts']),6)
