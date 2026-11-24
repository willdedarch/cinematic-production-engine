import unittest,sys,copy
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from prompt_compiler import compile_prompt,CompileError,CAT
class CompilerTests(unittest.TestCase):
 def spec(self,m='kling3_0_turbo'):
  return {'model_id':m,'intent':{'initial_state':'Davi em W1 com cantil fechado','action':'Oferece sem mudar a mão','camera':'Fixa a oeste do eixo','protected':'E1 e N1'},'parameters':{},'aspect_ratio':'16:9'}
 def ref(self,role):return {'id':role,'role':role,'uri':'provided/image.png','rights_confirmed':True}
 def test_eight_adapters(self):
  for mid,m in CAT['models'].items():
   s=self.spec(mid)
   if m['output_type']=='image':s['intent']={'subject':'Davi','space':'W1/E1/N1','light':'E1','protected':'geometria 6×4'}
   self.assertEqual(compile_prompt(s)['credits_consumed'],0)
 def test_unknown_model(self):
  s=self.spec('unverified');self.assertRaises(CompileError,compile_prompt,s)
 def test_unknown_native_parameter(self):
  s=self.spec();s['parameters']['focal_length']=35;self.assertRaises(CompileError,compile_prompt,s)
 def test_fraction_duration(self):
  s=self.spec();s['parameters']['duration']=3.4;self.assertRaises(CompileError,compile_prompt,s)
 def test_duration_bounds(self):
  s=self.spec();s['parameters']['duration']=16;self.assertRaises(CompileError,compile_prompt,s)
 def test_boolean_number(self):
  s=self.spec();s['parameters']['duration']=True;self.assertRaises(CompileError,compile_prompt,s)
 def test_bad_ratio(self):
  s=self.spec();s['aspect_ratio']='21:9';self.assertRaises(CompileError,compile_prompt,s)
 def test_unsupported_end(self):
  s=self.spec();s['references']=[self.ref('end_image')];self.assertRaises(CompileError,compile_prompt,s)
 def test_rights(self):
  s=self.spec();s['references']=[self.ref('start_image')];s['references'][0]['rights_confirmed']=False;self.assertRaises(CompileError,compile_prompt,s)
 def test_seedance_t2v_ref(self):
  s=self.spec('seedance_2_5');s['references']=[self.ref('start_image')];self.assertRaises(CompileError,compile_prompt,s)
 def test_seedance_omni(self):
  s=self.spec('seedance_2_5');s['parameters']['mode']='omni_reference';s['references']=[self.ref('start_image')];self.assertIn('reference_manifest',compile_prompt(s))
 def test_seedance_extension_requires_direction(self):
  s=self.spec('seedance_2_5');s['parameters']['mode']='video_extension';self.assertRaises(CompileError,compile_prompt,s)
 def test_minimax_end_requires_start(self):
  s=self.spec('minimax_h3');s['references']=[self.ref('end_image')];self.assertRaises(CompileError,compile_prompt,s)
 def test_gpt_svg_ref(self):
  s=self.spec('gpt_image_2_6');s['intent']={'subject':'Davi'};s['parameters']['output_format']='svg';s['references']=[self.ref('image_references')];self.assertRaises(CompileError,compile_prompt,s)
 def test_ref_limits(self):
  s=self.spec('seedream_v5_pro');s['intent']={'subject':'Davi'};s['references']=[{**self.ref('image_references'),'id':str(i)} for i in range(11)];self.assertRaises(CompileError,compile_prompt,s)
 def test_compilation_preserves_source(self):
  s=self.spec();old=copy.deepcopy(s);compile_prompt(s);self.assertEqual(s,old)
 def test_no_fake_bindings(self):self.assertNotIn('@image',compile_prompt(self.spec())['prompt'])
if __name__=='__main__':unittest.main()
