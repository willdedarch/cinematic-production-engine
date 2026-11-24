import json, pathlib, subprocess, sys, tempfile, unittest
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/'scripts'))
from route_knowledge import route
from knowledge_select import select
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
  self.assertNotIn('examples/pilot15/focal-shot.json',native)
  for alias in ('War','War film','FEB','Filmes de guerra'):
   self.assertEqual(paths(alias),native)
  drama = route('G10',['drama de guerra'])
  self.assertEqual(drama['selection']['genres'],['drama','guerra'])
  self.assertIn('engines/war-film.md',[v['file'] for v in drama['loaded']])
  historical = route('G10',['Guerra histórica'])
  self.assertEqual(historical['selection']['genres'],['guerra','historical'])
  self.assertIn('references/reference-analysis.md',[v['file'] for v in historical['loaded']])

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

 def test_all_genres_retrieve_specialization_case_and_rubric(self):
  matrix = {
   'historical':('Histórica','Historical','references/reference-analysis.md','wardrobe'),
   'drama':('Dramas','Drama','modules/dramaturgy.md','emotion'),
   'ação':('Filmes de ação','Action','knowledge/collective-direction.md','shot-design'),
   'suspense':('Suspense','Suspense film','modules/suspense-engine.md','suspense'),
   'thriller':('Thrillers','Thriller film','modules/editorial-sound.md','editing'),
   'terror':('Terror','Horror','knowledge/light.md','atmosphere'),
   'terror psicológico':('TERROR PSICOLOGICO','Psychological horror','modules/audience-psychology.md','suspense'),
   'ficção científica':('Ficções científicas','SCI-FI','modules/continuity.md','living-world'),
   'épico':('Épicos','Epic films','knowledge/collective-direction.md','composition'),
   'noir':('Filmes noir','Neo-noir','knowledge/light.md','lighting'),
   'realismo':('Realista','Realism','modules/performance-direction.md','performance'),
   'naturalismo':('Naturalista','Naturalistic','departments/cinematography.md','lighting'),
   'guerra':('Guerras','War film','engines/war-film.md','direction'),
   'comédia':('Comédias','Comedy','modules/dialogue-engine.md','dialogue'),
   'romance':('Romances','Romantic film','modules/emotional-engine.md','emotion'),
   'documentário':('Documentários','Documentary','references/reference-analysis.md','editing'),
   'fantasia':('Fantasias','Fantasy','engines/living-world.md','living-world'),
   'aventura':('Aventuras','Adventure','departments/locations.md','locations'),
   'crime':('Policial','Crime drama','modules/continuity.md','continuity'),
   'mistério':('Mistérios','Mystery','modules/suspense-engine.md','suspense'),
   'sobrevivência':('Sobrevivência','Survival','modules/continuity.md','props'),
  }
  for primary,(pt,en,specialization,rubric) in matrix.items():
   for word in (pt,en):
    with self.subTest(label=word, expected=primary):
     output = route('G2',[word])
     self.assertEqual(output['selection']['primary_genre'], primary)
     self.assertEqual(output['selection']['secondary_genres'], [])
     self.assertIn(specialization,{v['file'] for v in output['loaded']})
     self.assertEqual(output['genre_case']['genre'],primary)
     self.assertTrue(output['genre_case']['beats'])
     self.assertIn(rubric,{v['department'] for v in output['rubrics']})
     self.assertEqual(output['selection']['intent_mode'],'genre_default')

 def test_action_first_replaces_survival_examples_and_model_demo(self):
  modes = [route('PREVIS',['Guerra de ação'],model_id='seedance_2_5'),
           route('PREVIS',['War film'],model_id='seedance_2_5',intention='Visible combat'),
           route('PREVIS',['Drama de Guerra'],model_id='seedance_2_5',creative_profile='action_led_war')]
  for result in modes:
   self.assertEqual(result['selection']['intent_mode'],'action_led_war')
   self.assertEqual(result['genre_case']['case_id'],'WAR-ACTION-16')
   self.assertEqual(result['selection']['examples'][0],'examples/action-study/README.md')
   self.assertIn('examples/action-study/focal-shot.json',result['selection']['examples'])
   self.assertFalse(any(v['file'].startswith(('examples/pilot15/','examples/prompt-specs/','examples/last-water/','examples/war-action-pilot/'))
                        for v in result['loaded']))
  survival = route('IDEATE',['Sobrevivência'])
  self.assertIn('examples/last-water/production.md',survival['selection']['examples'])
  self.assertNotIn('examples/action-study/README.md',survival['selection']['examples'])
  suspense = route('IDEATE',['Suspense'],creative_profile='action_led_war')
  self.assertEqual(suspense['selection']['intent_mode'],'genre_default')
  quiet = route('IDEATE',['Guerra'],intention='Não quero ação intensa. Priorize a observação.')
  self.assertEqual(quiet['selection']['intent_mode'],'genre_default')

 def test_recovered_library_examples_respect_action_context(self):
  def sample(key,title,context,origin='LIB-CPE31'):
   return {'id':key,'title':title,'context':context,'kind':'CASE_STUDY','project_id':origin,'episode_id':'',
           'department':'integrated','status':'APPROVED'}
  tables = {name:[] for name in ('Techniques','Examples','Reference Library','Creative Preferences','Production Lessons',
                                 'Model Compatibility','Human Feedback','Failure Diagnostics','Evaluation Results')}
  tables['Examples'] = [sample('QUIET','A última água','Partilha do cantil'),
                        sample('ACTION','A ruptura visível','Ficção de guerra e ação física'),
                        sample('LOCAL','Uma pausa aprovada','Decisão desta série','P-ONE')]
  project, episode = {'id':'P-ONE'},{'id':'E-ONE','genre':'Guerra'}
  selected, evidence = select({'tables':tables},project,episode,'G2',[], '', 'ação cinematográfica',
                              classification={'genres':['guerra','ação'],'intent_mode':'action_led_war'})
  self.assertEqual({v['id'] for v in selected['Examples']},{'LOCAL','ACTION'})
  self.assertTrue(any(v['id']=='ACTION' and 'gênero: ação, guerra' in v['why'] for v in evidence['Examples']))

 def test_analyze_context_cli_recovers_attention_and_character_modules(self):
  root = pathlib.Path(__file__).resolve().parents[1]
  fixture = json.loads((root/'templates/shared-state.test-fixture.json').read_text(encoding='utf8'))
  project=fixture['tables']['Projects'][0]
  episode=fixture['tables']['Episodes'][0]
  episode['genre']='Ficção científica / Noir'
  with tempfile.TemporaryDirectory() as folder:
   base = pathlib.Path(folder)
   snapshot = base/'fixture.json'
   snapshot.write_text(json.dumps(fixture),encoding='utf8')
   request=base/'request.json'
   request.write_text(json.dumps({'intention':'Analisar abertura com ameaça e alteração visual','secondary_genres':['Drama']}),encoding='utf8')
   run=subprocess.run([sys.executable,'-B',str(root/'scripts/cpe.py'),'task','--task','ANALYZE','--workspace',str(base/'run'),
                       '--snapshot',str(snapshot),'--input',str(request),'--project',project['id'],'--episode',episode['id'],
                       '--include-test'],capture_output=True,encoding='utf8')
   self.assertEqual(run.returncode,0,run.stderr)
   result=json.loads(pathlib.Path(json.loads(run.stdout)['result']).read_text(encoding='utf8'))
  self.assertEqual(result['routing']['genres'],['ficção científica','noir','drama'])
  self.assertEqual(result['routing']['primary_genre'],'ficção científica')
  self.assertEqual(result['genre_example']['genre'],'ficção científica')
  self.assertTrue({'modules/viral-intelligence.md','engines/virality-lab.md','modules/character-engine.md',
                   'harness/media-analysis.md'}<=set(result['retrieved_hashes']))
  self.assertIn('retention',{r['department'] for r in result['rubrics']})

 def test_every_approved_module_is_reachable_from_router(self):
  root = pathlib.Path(__file__).resolve().parents[1]
  all_paths={p['file'] for command in [*(f'G{i}' for i in range(16)),'ANALYZE'] for p in route(command)['loaded']}
  modules={path.relative_to(root).as_posix() for path in (root/'modules').glob('*.md')}
  self.assertLessEqual(modules,all_paths)
