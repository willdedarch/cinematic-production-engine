"""Retained A/B presentations and readback-only retry on the 1.3 desk."""
import copy
from datetime import datetime,timezone,timedelta
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from desk_pairs import dispatch, presentable_pairs, project_media
from journal import journal_rows
from judgment import take_preferences
from shared_state import check_guards,StateError

class DesktopPairs(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.ws=Path(self.temp.name)
        self.snapshot=json.loads((ROOT/'examples/takes/demo-state.json').read_text(encoding='utf8'))
        base=json.loads((ROOT/'examples/takes/COM-01-pair.json').read_text(encoding='utf8'))
        self.pid,self.eid=base['project_id'],base['episode_id']
        self.scope={'project_id':self.pid,'episode_id':self.eid,'shot_id':'TEST-SH-1','include_test':True}
        self.spec={**self.scope,'takes':[{'id':r['id'],'revision':1} for r in base['takes'].values()],'question':'Em qual take a pausa funciona?'}
        self.vote={**self.scope,'authorization':{'actor':'SYNTHETIC','user_message_ref':'SIMULAÇÃO-A','authorized':True},
            'choice':'B','start_ms':3800,'mark_ms':4200,'end_ms':4600,'reason':'Sintético · pausa de ensaio.','preference_scope':'scene'}

    def present(self,spec=None,state=None):
        manifest=dispatch('desk-pair',state or self.snapshot,spec or self.spec,self.ws)['manifest']
        self.vote.update({key:manifest[key] for key in ('pair_id','pair_sha256')})
        return manifest

    def submit(self,spec=None,state=None):
        return dispatch('desk-vote',state or self.snapshot,spec or self.vote,self.ws)

    def test_presentation_survives_refresh_and_projects_identical_bytes(self):
        orig=self.present()
        again=self.present()
        self.assertEqual(orig,again)
        items=presentable_pairs(self.snapshot,self.pid,self.eid,self.ws)
        self.assertEqual(len(items),1)
        import base64
        for label,take in orig['takes'].items():
            raw=base64.b64decode(items[0]['media'][label].split(',',1)[1])
            self.assertEqual(hashlib.sha256(raw).hexdigest(),take['sha256'])
        self.assertEqual(items[0]['manifest']['shot']['id'],'TEST-SH-1')

    def test_ambiguous_pair_requires_explicit_selection(self):
        first=self.present()
        self.present({**self.spec,'question':'Outro critério?'})
        unpinned={key:value for key,value in self.vote.items() if key not in ('pair_id','pair_sha256')}
        ask=self.submit(unpinned)
        self.assertEqual(ask['kind'],'PAIR_CLARIFICATION')
        self.assertEqual(len(ask['choices']),2)
        plan=self.submit({**unpinned,'pair_id':first['pair_id'],'pair_sha256':first['pair_sha256']})
        self.assertEqual(len(plan['changes']),3)
        with self.assertRaisesRegex(StateError,'versão do par'):
            self.submit({**unpinned,'question':first['question'],'pair_hint':first['pair_id'][-8:]})

    def test_choice_cannot_be_rebound_to_an_inverted_presentation(self):
        with patch('takes.secrets.SystemRandom'):
            original=self.present()
        stale=copy.deepcopy(self.vote)
        with patch('takes.secrets.SystemRandom') as random_factory:
            random_factory.return_value.shuffle.side_effect=lambda choices: choices.reverse()
            inverted=self.present({**self.spec,'presentation_ref':'segunda apresentação'})
        self.assertEqual(original['takes']['A'],inverted['takes']['B'])
        self.assertNotEqual(original['pair_sha256'],inverted['pair_sha256'])
        with self.assertRaisesRegex(StateError,'versão do par'):
            self.submit({**stale,'pair_id':inverted['pair_id']})

    def test_scene_scope_excludes_other_scene_and_project(self):
        self.present()
        plan=self.submit()
        candidate=copy.deepcopy(plan['candidate'])
        shot=candidate['tables']['Shot List'][0]
        second={**shot,'id':'TEST-SAME-SCENE'}
        third={**shot,'id':'TEST-DIFFERENT-SCENE','scene_beat':'CENA 2'}
        candidate['tables']['Shot List'].extend([second,third])
        self.assertEqual(len(take_preferences(candidate,self.pid,self.eid,[second['id']],include_test=True)),1)
        self.assertEqual(take_preferences(candidate,self.pid,self.eid,[third['id']],include_test=True),[])
        self.assertEqual(take_preferences(candidate,'OUTRA',self.eid,[second['id']],include_test=True),[])
        self.assertEqual(take_preferences(candidate,self.pid,self.eid,include_test=True),[])

    def test_retry_reuses_plan_and_distinguishes_partial_and_confirmed(self):
        self.present()
        plan=self.submit()
        retry=copy.deepcopy(self.vote)
        retry['authorization']['user_message_ref']='SIMULAÇÃO-B-REPETIÇÃO'
        self.assertEqual(self.submit(retry),plan)
        now=datetime.now(timezone.utc)+timedelta(seconds=1)
        events=journal_rows(plan,'PREPARED',self.pid,self.eid,True,now.isoformat(),'Teste')
        state=copy.deepcopy(self.snapshot)
        state['read_at']=(now+timedelta(seconds=2)).isoformat()
        state['tables']['Revision History'].extend(events)
        self.assertEqual(self.submit(retry,state)['kind'],'RECONCILIATION_REQUIRED')
        state=copy.deepcopy(plan['candidate'])
        state['read_at']=(now+timedelta(seconds=2)).isoformat()
        state['tables']['Revision History'].extend(events)
        state['tables']['Revision History'].extend(journal_rows(plan,'CONFIRMED',self.pid,self.eid,True,(now+timedelta(seconds=1)).isoformat(),'Teste'))
        outcome=self.submit(retry,state)
        self.assertEqual(outcome['kind'],'ALREADY_CONFIRMED')
        self.assertFalse(outcome['remote_write'])
        self.assertEqual(outcome['op_id'],plan['op_id'])

    def test_changed_shot_or_replaced_media_stops_decision(self):
        first=self.spec['takes'][0]
        row=next(r for r in self.snapshot['tables']['Artifact Registry'] if r['id']==first['id'])
        path=self.ws/'material.mp4'
        path.write_bytes((ROOT/row['uri']).read_bytes())
        self.present({**self.spec,'takes':[{**first,'path':str(path)},self.spec['takes'][1]]})
        plan=self.submit()
        self.assertTrue(check_guards(plan,self.snapshot))
        altered=copy.deepcopy(self.snapshot);altered['tables']['Shot List'][0]['revision']+=1
        with self.assertRaisesRegex(StateError,'plano mudou'):self.submit(state=altered)
        path.write_bytes(b'outros bytes')
        items=presentable_pairs(self.snapshot,self.pid,self.eid,self.ws)
        self.assertFalse(items[0]['media'])
        self.assertIn('substituído',items[0]['unavailable'])
        with self.assertRaisesRegex(StateError,'substituída'):self.submit()
        with self.assertRaisesRegex(StateError,'substituída'):check_guards(plan,self.snapshot)

    def test_large_media_published_as_lazy_verified_local_chunks(self):
        chunks=self.ws/'media';source=self.ws/'source.mp4'
        source.write_bytes(b'X'*(8*1024*1024+1))
        take={'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'mime':'video/mp4'}
        url=project_media(source,take,chunks)
        self.assertEqual(url,'media/'+take['sha256']+'.js')
        payload=(self.ws/url).read_text(encoding='utf8')
        import base64
        key,parts=json.loads('['+payload.removeprefix('window.CPE_MEDIA_CHUNKS(').removesuffix(');')+']')
        self.assertEqual(key,hashlib.sha256(b''.join(base64.b64decode(p) for p in parts)).hexdigest())
        self.assertGreater(len(parts),1)
        (self.ws/url).write_text('partes danificadas',encoding='utf8')
        self.assertEqual(project_media(source,take,chunks),url)
        self.assertEqual((self.ws/url).read_text(encoding='utf8'),payload)
        source.write_bytes(b'Y'*(8*1024*1024+1))
        with self.assertRaisesRegex(StateError,'substituído'):project_media(source,take,chunks)

if __name__=='__main__':unittest.main()

