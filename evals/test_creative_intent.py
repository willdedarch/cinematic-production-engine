"""Regression for authored action hierarchy, versioned prompts and independent observation."""
from copy import deepcopy
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from creative_intent import apply_to_review, audit, current, plan, review, target_intent
from episode_workflow import initialize_episode
from shared_state import SCHEMA, StateError, index, prepare
from shot_workflow import handoff


PROFILE = {'kind':'action_led_war','action_percent':65,'story_percent':35}
EVENTS = [
    {'id':'A1','shot_id':'SA1','class':'ACTION','start_s':0,'end_s':13,'on_screen':True,
     'action':'O impacto parte o vidro e derruba a luminária em quadro.',
     'consequence':'O corredor fica às escuras.'},
    {'id':'D1','shot_id':'SA2','class':'STORY','start_s':13,'end_s':20,'on_screen':True,
     'action':'Iara reconhece a voz no gravador.','consequence':'Ela muda de ideia sobre a mensagem.'},
]


def authorization(op):
    return {'authorized':True,'actor':'Synthetic regression','user_message_ref':'fixture-'+op,'op_id':op}


class IntentTests(unittest.TestCase):
    def setUp(self):
        self.at = datetime.now(timezone.utc).isoformat()
        empty = {'schema_version':'3.1.0','spreadsheet_id':'LOCAL-INTENT-FIXTURE','read_at':self.at,
                 'tables':{table:[] for table in SCHEMA['tables']}}
        self.base = initialize_episode(empty,{'project_id':'TEST-INTENT','project_name':'Regression',
            'episode_id':'TEST-INTENT-EP1','episode_title':'Fixture','genre':'guerra de ação','target_seconds':20,
            'is_test':True},authorization('INIT'))['candidate']
        self.project='TEST-INTENT'
        self.episode='TEST-INTENT-EP1'
        shot = {'table':'Shot List','id':'SA1','expected_revision':None,'values':{
            'project_id':self.project,'episode_id':self.episode,'is_test':True,'gate_id':'G10','version':'v1',
            'status':'DRAFT','scene_beat':'Corredor','order':1,'duration_s':13,'purpose':'Alterar o espaço em quadro.',
            'action':EVENTS[0]['action'],'camera_blocking':'Luminária e corredor no mesmo quadro',
            'sound_edit':'Ataque em sincronia com a mudança de luz','start_end_state':'{"in":{},"out":{}}'}}
        self.base = prepare(self.base,{**authorization('SHOT'),'at':self.at,'changes':[shot]})['candidate']
        self.input = {'project_id':self.project,'episode_id':self.episode,'profile':PROFILE,'events':EVENTS,
                      'decision_id':'INTENT-1','authorization':authorization('INTENT')}
        self.state = plan(self.base,self.input)['candidate']
        self.binding = current(self.state,self.project,self.episode)
        self.request = {'shot_id':'SA1','model_id':'seedance_2_5','parameters':{'mode':'t2v'},
            'cinematic_plan':{'cast':{'I':'Iara'},'duration_s':13,'beats':[{'id':'B1','start_s':0,'end_s':13,
                'subjects':['I'],'action':EVENTS[0]['action'],'event_ids':['A1']}]}}

    def test_editorial_share_is_scoped_to_a_recorded_episode(self):
        self.assertIsNone(current(self.base,self.project,self.episode))
        result = audit(PROFILE,EVENTS)
        self.assertEqual((result['action_s'],result['story_s']),(13,7))
        changed = deepcopy(EVENTS)
        changed[0]['on_screen']=False
        with self.assertRaisesRegex(StateError,'require physical action on screen'):
            audit(PROFILE,changed)
        changed=deepcopy(EVENTS)
        changed[0]['end_s']=changed[1]['start_s']=7
        self.assertFalse(audit(PROFILE,changed)['ratio_matches'])
        with self.assertRaisesRegex(StateError,'preserve 65/35'):
            plan(self.base,{**self.input,'events':changed})

    def test_cli_prompt_for_two_models_preserves_the_approved_action(self):
        with tempfile.TemporaryDirectory() as d:
            temp=Path(d)
            state=temp/'state.json'
            state.write_text(json.dumps(self.state),encoding='utf8')
            common=[]
            for model,parameters in [('seedance_2_5',{'mode':'t2v'}),('minimax_h3',{})]:
                data=temp/(model+'.json')
                data.write_text(json.dumps({**self.request,'model_id':model,'parameters':parameters}),encoding='utf8')
                result=subprocess.run([sys.executable,'-B',str(ROOT/'scripts/cpe.py'),'shot-handoff',
                    '--workspace',str(temp/'work'),'--snapshot',str(state),'--input',str(data)],
                    capture_output=True,check=True,encoding='utf8')
                receipt=json.loads(result.stdout)
                packet=json.loads(Path(receipt['result']).read_text(encoding='utf8'))
                prompt=Path(receipt['prompt_file']).read_text(encoding='utf8').rstrip('\n')
                self.assertEqual(prompt,packet['delivery']['prompt'])
                self.assertIn(EVENTS[0]['action'],prompt)
                self.assertEqual(packet['creative_intent']['decision'],self.binding['decision'])
                common.append(packet['production_brief']['model_neutral_prompt'])
            self.assertEqual(*common)

    def test_handoff_refuses_missing_or_shifted_event(self):
        removed=deepcopy(self.request)
        removed['cinematic_plan']['beats'][0]['event_ids']=[]
        with self.assertRaisesRegex(StateError,'omits approved event'):
            handoff(self.state,removed)
        shifted=deepcopy(self.request)
        shifted['cinematic_plan']['beats'][0]['start_s']=1
        with self.assertRaisesRegex(StateError,'timing changes approved event'):
            handoff(self.state,shifted)
        substituted=deepcopy(self.request)
        substituted['cinematic_plan']['beats'][0]['action']='Iara lê na tela: '+EVENTS[0]['action']
        with self.assertRaisesRegex(StateError,'action changes approved event'):
            handoff(self.state,substituted)

    def test_episode_duration_cannot_leave_the_approved_timeline_behind(self):
        change={'table':'Episodes','id':self.episode,'expected_revision':1,'values':{'target_seconds':40}}
        with self.assertRaisesRegex(StateError,'without a matching creative intent'):
            prepare(self.state,{**authorization('DURATION'),'at':self.at,'changes':[change]})
        longer=deepcopy(EVENTS)
        longer[0]['end_s']=longer[1]['start_s']=26
        longer[1]['end_s']=40
        spec={**self.input,'decision_id':'INTENT-2','events':longer,'replaces':self.binding['decision'],
              'episode_revision':1,'authorization':authorization('INTENT-2')}
        updated=plan(self.state,spec)['candidate']
        self.assertEqual(index(updated)['Episodes'][self.episode]['target_seconds'],40)

    def test_approved_action_replaces_conflicting_card_summary_in_prompt(self):
        contradicted='Iara relata o impacto já fora do corredor.'
        change={'table':'Shot List','id':'SA1','expected_revision':1,'values':{'action':contradicted}}
        edited=prepare(self.state,{**authorization('CARD'),'at':self.at,'changes':[change]})['candidate']
        packet=handoff(edited,self.request)
        self.assertEqual(packet['production_brief']['action'],EVENTS[0]['action'])
        self.assertNotIn(contradicted,packet['delivery']['prompt'])
        self.assertNotIn(contradicted,packet['production_brief']['model_neutral_prompt'])

    def test_fractional_episode_offsets_do_not_shift_shot_beats(self):
        opening={**EVENTS[1],'id':'D0','shot_id':'SA0','start_s':0,'end_s':0.3}
        continuation={**EVENTS[0],'id':'A2','start_s':2.3,'end_s':13.3}
        revised=[opening,{**EVENTS[0],'start_s':0.3,'end_s':2.3},continuation,{**EVENTS[1],'start_s':13.3}]
        state=plan(self.base,{**self.input,'events':revised})['candidate']
        request=deepcopy(self.request)
        beat=request['cinematic_plan']['beats'][0]
        request['cinematic_plan']['beats']=[{**beat,'end_s':2},
           {**beat,'id':'B2','start_s':2,'event_ids':['A2']}]
        packet=handoff(state,request)
        self.assertEqual([event['id'] for event in packet['creative_intent']['events']],['A1','A2'])

    def test_review_rejects_substitution_and_withholds_incomplete_evidence(self):
        shot=index(self.state)['Shot List']['SA1']
        active=target_intent(self.state,'Shot List',shot)
        technical_ready={'recommendation':'READY_FOR_HUMAN_DECISION','approved':False}
        base={'decision':active['decision'],'intensity':'OBSERVED','pacing':'FIT','evidence_ref':'paper / B1'}
        for status, expected in [('AUDIBLE_ONLY','REJECT'),('DIALOGUE_ONLY','REJECT'),('OMITTED','REJECT'),
                                 ('REPLACED','REJECT'),('VISIBLE','MATCH'),('UNKNOWN','UNKNOWN')]:
            with self.subTest(status=status):
                observation={**base,'events':[{'id':'A1','status':status,'evidence_ref':'B1 00:02',
                                                'consequence_observed':True}]}
                outcome=review(active,observation)
                self.assertEqual(outcome['outcome'],expected)
                self.assertFalse(outcome['approved'])
                if expected=='REJECT':
                    result=apply_to_review(technical_ready,active,{'intent_review':observation})
                    self.assertEqual(result['recommendation'],'CHANGES_REQUESTED')
        self.assertEqual(apply_to_review(technical_ready,active,{})['recommendation'],'INCOMPLETE_EVIDENCE')


if __name__=='__main__':
    unittest.main()
