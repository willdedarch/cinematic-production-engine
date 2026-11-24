import json, pathlib, subprocess, sys, tempfile, unittest
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/'scripts'))
from route_knowledge import route
class Routes(unittest.TestCase):
 def test_all_gates_read_existing_modules(self):
  for n in range(16):
   r=route('G'+str(n),['war']);self.assertEqual(r['gate'],'G'+str(n));self.assertTrue(all(x['text'].strip() and len(x['sha256'])==64 for x in r['loaded']))
 def test_commands_route_to_department(self):
  self.assertEqual(route('CAST')['gate'],'G7');self.assertEqual(route('LOCATION')['gate'],'G8');self.assertEqual(route('PROMPTS')['gate'],'G10')
 def test_next_requires_fresh_state_resolution(self):
  with self.assertRaises(ValueError):route('NEXT')

 def test_war_aliases_retrieve_the_same_engine_without_private_profile(self):
  paths = lambda genre: [row['file'] for row in route('G10',[genre])['loaded']]
  native = paths('guerra')
  self.assertIn('engines/war-film.md',native)
  self.assertNotIn('project-profiles/project-template.md',native)
  for alias in ('War','War film','FEB','drama de guerra','Guerra histórica','Filmes de guerra'):
   self.assertEqual(paths(alias),native)

 def test_task_cli_recovers_war_in_a_mixed_genre_and_chooses_relevant_examples(self):
  root = pathlib.Path(__file__).resolve().parents[1]
  fixture = json.loads((root/'templates/shared-state.test-fixture.json').read_text(encoding='utf8'))
  project = fixture['tables']['Projects'][0]['id']
  episode = fixture['tables']['Episodes'][0]
  episode['genre'] = 'Suspense de guerra'
  with tempfile.TemporaryDirectory() as folder:
   base = pathlib.Path(folder)
   snapshot = base/'fixture.json'
   snapshot.write_text(json.dumps(fixture),encoding='utf8')
   request = base/'request.json'
   request.write_text(json.dumps({'department':' Direção ','deliverable':'Plano cinematográfico','problem':'Continuidade',
                                  'scene_complexity':'Coletiva'}),encoding='utf8')
   run = subprocess.run([sys.executable,'-B',str(root/'scripts/cpe.py'),'task','--workspace',str(base/'run'),
                         '--snapshot',str(snapshot),'--input',str(request),'--project',project,'--episode',episode['id'],
                         '--gate','G10','--model','minimax_h3','--include-test'],capture_output=True,encoding='utf8')
   self.assertEqual(run.returncode,0,run.stderr)
   result = json.loads(pathlib.Path(json.loads(run.stdout)['result']).read_text(encoding='utf8'))
  self.assertEqual(set(result['routing']['conditions']),{'suspense','guerra'})
  self.assertIn('examples/war-action-pilot/README.md',result['routing']['examples'])
  self.assertIn('examples/prompt-specs/minimax_h3.json',result['routing']['examples'])
  self.assertNotIn('examples/prompt-specs/kling3_0_turbo.json',result['retrieved_hashes'])
  self.assertIn('engines/war-film.md',result['retrieved_hashes'])
  self.assertIn('modules/performance-direction.md',result['retrieved_hashes'])
  self.assertIn('modules/continuity.md',result['retrieved_hashes'])
  self.assertIn('examples/pilot15/focal-shot.json',result['retrieved_hashes'])
  self.assertIn('references/professional-methods-1.5.md',result['retrieved_hashes'])
  self.assertEqual(result['routing']['selectors'],{'department':'direction','deliverable':'handoff',
                   'problem':'continuity','scene_complexity':'complex'})
  self.assertEqual(result['used_knowledge'],[])
