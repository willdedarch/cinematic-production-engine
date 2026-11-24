import copy,json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from prompt_compiler import compile_prompt,CompileError

class CinematicPlanTests(unittest.TestCase):
    def spec(self):
        return {'model_id':'seedance_2_5','parameters':{'duration':8},
                'intent':{'initial_state':'Duas pessoas junto à mesa','action':'Uma oferece a manta'},
                'cinematic_plan':{'objective':'Tornar o custo da oferta legível','space':'mesa ao centro',
                    'cast':{'P1':'Ada','P2':'Ivo'},'duration_s':8,'protected':'A janela fica a oeste',
                    'beats':[{'id':'B1','start_s':0,'end_s':4,'subjects':['P1'],
                              'action':'Ada estende a manta','entry':{'manta':'Ada'},'exit':{'manta':'entre ambos'}},
                             {'id':'B2','start_s':4,'end_s':8,'subjects':['P1','P2'],
                              'action':'Ivo recolhe uma ponta','entry':{'manta':'entre ambos'},'exit':{'manta':'Ivo'}}]}}
    def test_preserves_authoring_and_translates_timed_actions(self):
        spec=self.spec();original=copy.deepcopy(spec);out=compile_prompt(spec)
        self.assertEqual(spec,original);self.assertIn('4–8 s',out['prompt'])
        self.assertIn('Ivo recolhe',out['prompt']);self.assertEqual(out['native_parameters'],{'duration':8})
        self.assertFalse(out['generation_tested']);self.assertEqual(out['credits_consumed'],0)
    def test_rejects_handover_reset_and_allows_reviewed_exception(self):
        spec=self.spec();spec['cinematic_plan']['beats'][1]['entry']['manta']='em outra sala'
        with self.assertRaisesRegex(CompileError,'state jump'):compile_prompt(spec)
        spec['cinematic_plan']['beats'][1]['continuity_exception']='Elipse solicitada pelo diretor; reapresentar'
        self.assertTrue(any('director review' in w for w in compile_prompt(spec)['warnings']))
    def test_rejects_unsupported_reference_in_a_beat(self):
        spec=self.spec();spec['cinematic_plan']['beats'][0]['references']=['unattached']
        with self.assertRaisesRegex(CompileError,'outside the attachment'):compile_prompt(spec)
    def test_rejects_drift_of_duration_and_unknown_actor(self):
        spec=self.spec();spec['cinematic_plan']['duration_s']=10
        with self.assertRaises(CompileError):compile_prompt(spec)
        spec=self.spec();spec['cinematic_plan']['beats'][0]['subjects']=['SomeoneElse']
        with self.assertRaises(CompileError):compile_prompt(spec)
    def test_rejects_bad_times_and_structures(self):
        for value in (float('nan'),True,9):
            spec=self.spec();spec['cinematic_plan']['beats'][0]['end_s']=value
            with self.subTest(value=value),self.assertRaises(CompileError):compile_prompt(spec)
        spec=self.spec();spec['cinematic_plan']['beats'][1]['start_s']=3
        with self.assertRaises(CompileError):compile_prompt(spec)
        spec=self.spec();spec['cinematic_plan']['beats'][0]['subjects']=[{}]
        with self.assertRaises(CompileError):compile_prompt(spec)
    def test_warns_unwritten_interval_without_inventing_action(self):
        spec=self.spec();spec['cinematic_plan']['beats'][1]['start_s']=5
        output=compile_prompt(spec)
        self.assertTrue(any('no authored' in w for w in output['warnings']))
    def test_old_spec_keeps_its_previous_prompt(self):
        spec=self.spec();spec.pop('cinematic_plan')
        self.assertEqual(compile_prompt(spec)['prompt'],'Initial state: Duas pessoas junto à mesa\nAction: Uma oferece a manta')

if __name__=='__main__':unittest.main()
