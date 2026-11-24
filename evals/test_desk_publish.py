"""Release regressions for per-project stable publication, timeline cuts and safe refresh."""
import copy
import importlib.util
import json
import os
import re
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest import mock

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import desk_publish as publish
from episode_workflow import initialize_episode
from desk_pairs import dispatch as pairs_dispatch
from journal import journal_rows
from shared_state import StateError, fingerprint

example_spec = importlib.util.spec_from_file_location('publisher_example',ROOT/'examples/series-worked/run.py')
example=importlib.util.module_from_spec(example_spec)
example_spec.loader.exec_module(example)


class DeskPublication(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.example_dir=tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.example_dir.cleanup)
        cls.base=example.scenario(cls.example_dir.name)
        cls.spec={'project':'A ultima agua — ensaio','episode':'EP1','include_test':True}

    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.workspace=Path(self.temp.name)
        self.snap=copy.deepcopy(self.base)

    def publish(self, **overrides):
        return publish.dispatch('desk-publish',self.snap,{**self.spec,**overrides},self.workspace)

    @staticmethod
    def read_desk(result):
        location=Path(result['data'])
        lines=location.read_text(encoding='utf-8').splitlines()
        data=json.loads(lines[1][len('window.CPE_DESK_DATA='):-1])
        shells=json.loads(lines[2][len('window.CPE_DESK_PAGES='):-1])
        return data,shells

    def test_names_aliases_tests_and_ambiguous_projects(self):
        with self.assertRaisesRegex(StateError,'não encontrado'):
            publish.resolve_scope(self.snap,{'episode':'EP2'})
        self.assertEqual(publish.resolve_scope(self.snap,{**self.spec,'episode':'Depois da buzina'})[1]['episode_number'],2)
        added=initialize_episode(self.snap,{'project_id':'OTHER-P','project_name':'Outra produção',
                    'episode_title':'Outra história','target_seconds':30,'is_test':True},example.auth('OUTRO'))
        self.snap=added['candidate']
        with self.assertRaisesRegex(StateError,'ambíguo'):
            publish.resolve_scope(self.snap,{'episode':'EP1','include_test':True})
        desk,_=self.read_desk(self.publish())
        content=json.dumps(desk)
        self.assertNotIn('OTHER-P',content)
        self.assertNotIn('Outra produção',content)
        self.assertNotIn('Revision History',desk)

    def test_data_projection_matches_current_versions_and_actual_thumbnails(self):
        result=self.publish()
        desk,shells=self.read_desk(result)
        self.assertEqual(desk['episode']['title'],'O cantil')
        self.assertTrue(desk['series']['is_test'])
        self.assertEqual([s['label'] for s in desk['shots']],['SH01','SH02','SH03','SH04','SH05','SH06'])
        sh=desk['shots'][-1]
        self.assertEqual(sh['previous_shot'],'SH05')
        self.assertEqual(sh['states']['in']['cantil'],'Lia.esquerda')
        self.assertTrue(sh['thumbnail'].startswith('data:image/png;base64,'))
        self.assertEqual(sh['selected_take']['id'],'TAKE-06')
        self.assertTrue(sh['last_decision']['id'])
        self.assertEqual(len(desk['workflow']),16)
        self.assertIn('Screenplays',desk['materials'])
        for name,shell in shells.items():
            self.assertTrue((Path(result['studio']).parent/(name+'.html')).is_file())
            for resource in re.findall(r'(?:src|href)="(assets/[^"]+)"',shell['head']+shell['body']):
                file=Path(result['studio']).parent/resource
                import hashlib
                self.assertEqual(file.stem,hashlib.sha256(file.read_bytes()).hexdigest())
        # Both stable entry points read exactly the same one-step pointer.
        self.assertTrue(all('src="desk-data.js"' in Path(result[k]).read_text(encoding='utf-8')
                            for k in ('studio','comparator')))

    def test_same_project_same_path_renamed_episode_or_title_and_drafts_untouched(self):
        first=self.publish()
        draft=Path(first['studio']).parent/'anotacao-do-diretor.txt'
        draft.write_text('preservar a pausa',encoding='utf-8')
        self.snap['tables']['Projects'][0]['name']='Série renomeada'
        self.snap['read_at']='2090-11-24T12:00:00+00:00'
        second=self.publish(project='Série renomeada',episode='EP2')
        self.assertEqual(first['studio'],second['studio'])
        self.assertEqual(self.read_desk(second)[0]['episode']['number'],2)
        self.assertEqual(draft.read_text(encoding='utf-8'),'preservar a pausa')
        self.assertEqual(len(self.read_desk(second)[0]['shots']),0)

    def test_shared_vote_reloads_without_local_pair_and_preserves_exact_versions(self):
        state=json.loads((ROOT/'examples/takes/demo-state.json').read_text(encoding='utf-8'))
        sample=json.loads((ROOT/'examples/takes/COM-01-pair.json').read_text(encoding='utf-8'))
        shot=state['tables']['Shot List'][0]
        scope={'project_id':shot['project_id'],'episode_id':shot['episode_id'],'shot_id':shot['id'],'include_test':True}
        pair=pairs_dispatch('desk-pair',state,{**scope,'question':'Em qual take funciona a pausa?',
            'takes':[{'id':r['id'],'revision':r['revision']} for r in sample['takes'].values()]},self.workspace)['manifest']
        plan=pairs_dispatch('desk-vote',state,{**scope,'pair_id':pair['pair_id'],'choice':'B','start_ms':3800,'mark_ms':4200,
            'end_ms':4600,'reason':'A pausa antes da fala.','preference_scope':'scene','authorization':{
            'authorized':True,'actor':'ensaio','user_message_ref':'pedido-de-ensaio'}},self.workspace)
        candidate=plan['candidate']
        at=datetime.now(timezone.utc)+timedelta(seconds=1)
        candidate['read_at']=(at+timedelta(seconds=2)).isoformat()
        ep=state['tables']['Episodes'][0]
        def view():
            data=publish.project(candidate,scope,self.workspace/'outro-computador')
            self.assertFalse(data['pairs'])
            return next(s for s in data['shots'] if s['id']==shot['id'])
        def add_event(kind,when):
            candidate['tables']['Revision History'].extend(journal_rows(plan,kind,scope['project_id'],ep['id'],True,when.isoformat(),'ensaio'))
        add_event('PREPARED',at)
        self.assertFalse(view()['preferences'][0]['confirmed'])
        add_event('CONFIRMED',at+timedelta(seconds=1))
        preference=view()['preferences'][0]
        self.assertEqual(preference['choice'],'B')
        self.assertEqual(preference['mark_ms'],4200)
        self.assertEqual(preference['reason'],'A pausa antes da fala.')
        self.assertEqual(preference['scope'],'scene')
        self.assertTrue(preference['confirmed'] and preference['current'])
        self.assertEqual(preference['takes']['B']['sha256'],pair['takes']['B']['sha256'])
        self.assertIsNone(view()['selected_take'])
        candidate['tables']['Shot List'][0]['revision']+=1
        self.assertFalse(view()['preferences'][0]['current'])
        candidate['tables']['Human Feedback'][-1]['reason']='Outra coisa'
        self.assertFalse(view()['preferences'])

    def test_private_working_area_stays_outside_public_delivery(self):
        with tempfile.TemporaryDirectory() as public:
            result=self.publish(publish_root=public)
            self.assertTrue(Path(result['studio']).resolve().is_relative_to(Path(public).resolve()))
            self.assertFalse((Path(public)/'desk-pairs').exists())
            self.assertFalse((self.workspace/'mesas').exists())
        for folder in [ROOT/'private-share',self.workspace/'desk-pairs'/'test']:
            with self.assertRaises(StateError):
                self.publish(publish_root=str(folder))

    def test_older_or_inconsistent_timestamp_cannot_replace_desk(self):
        result=self.publish()
        old=Path(result['data']).read_bytes()
        self.snap['read_at']='2000-02-01T00:00:00Z'
        with self.assertRaisesRegex(StateError,'Leitura anterior'):
            self.publish()
        self.snap['read_at']=self.base['read_at']
        self.snap['tables']['Episodes'][0]['title']='Conteúdo divergente'
        with self.assertRaisesRegex(StateError,'mesmo instante'):
            self.publish()
        self.assertEqual(Path(result['data']).read_bytes(),old)

    def test_interrupted_commit_and_overlapping_writer_preserve_last_view(self):
        result=self.publish()
        old=Path(result['data']).read_bytes()
        real=publish.atomic_bytes
        def fail(path,content):
            if path.name=='desk-data.js':
                raise OSError('interrupção do ensaio')
            return real(path,content)
        with mock.patch.object(publish,'atomic_bytes',side_effect=fail):
            with self.assertRaisesRegex(OSError,'interrupção'):
                self.publish(episode='EP2')
        self.assertEqual(Path(result['data']).read_bytes(),old)
        lock=next((self.workspace/'mesas').glob('*.lock'))
        with publish.publication_lock(lock):
            with self.assertRaises((RuntimeError,BlockingIOError)):
                self.publish(episode='EP2')
        self.assertEqual(Path(result['data']).read_bytes(),old)
        self.assertEqual(self.publish(episode='EP2')['studio'],result['studio'])

    def test_authorship_fence_and_installation_separation(self):
        result=self.publish()
        directory=Path(result['studio']).parent
        owner=directory/publish.OWNER_FILE
        owner.write_text('{"project":"projeto-alheio"}',encoding='utf-8')
        old=Path(result['data']).read_bytes()
        with self.assertRaisesRegex(StateError,'outro projeto'):
            self.publish()
        self.assertEqual(Path(result['data']).read_bytes(),old)
        with self.assertRaisesRegex(StateError,'fora da instalação'):
            publish.dispatch('desk-publish',self.snap,self.spec,ROOT/'examples')
        distinct=copy.deepcopy(self.snap)
        distinct['spreadsheet_id']='OUTRA-PLANILHA-TESTE'
        other=publish.dispatch('desk-publish',distinct,self.spec,self.workspace)
        self.assertNotEqual(result['studio'],other['studio'])

    def test_temporal_scope_uses_actual_anchors_and_never_places_unknown_dialogue(self):
        shots=[{'id':'P-EP2-SH06','scene_beat':'Porta'},{'id':'P-EP2-SH07','scene_beat':'Viagem'}]
        events=[{'episode_id':'E1','sequence':74,'beat':'SH06'},
                {'episode_id':'E2','sequence':68,'beat':'SH06'}]
        p=publish.positions(shots,events,'E2')
        self.assertEqual(p['P-EP2-SH06']['previous_sequence'],67)
        self.assertEqual(p['P-EP2-SH06']['positions'],[{'sequence':68,'beat':'SH06'}])
        self.assertEqual(p['P-EP2-SH07'],{'precision':'episode','previous_sequence':0,'positions':[]})
        self.assertEqual(publish.shot_label(shots[0]['id']),'SH06')

    def test_missing_changed_or_unlicensed_media_is_identified(self):
        temp=self.workspace/'imagem.png'
        temp.write_bytes(b'outro-conteudo')
        link=[{'relation':'reference','from':{'id':'R'},'stale':False}]
        r={'id':'R','rights':'Do ensaio','uri':str(temp),'sha256':'0'*64}
        self.assertIn('alterado',publish.local_thumbnail(link,{'R':r})[1])
        temp.unlink()
        self.assertIn('indisponível',publish.local_thumbnail(link,{'R':r})[1])
        r['rights']=''
        self.assertIn('direitos',publish.local_thumbnail(link,{'R':r})[1])

