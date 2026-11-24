import json,unittest,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
from route_knowledge import route
class Knowledge(unittest.TestCase):
 def load(self,p):return json.loads((R/p).read_text(encoding='utf-8'))
 def test_all_sources_resolve(self):
  sources={x['id'] for x in self.load('references/source-index.json')}
  for card in self.load('knowledge/techniques.json'):self.assertTrue(set(card['sources'])<=sources)
 def test_operational_cards_not_empty(self):
  cards=self.load('knowledge/techniques.json');self.assertEqual(len(cards),21)
  for c in cards:
   for k in ['when','procedure','tradeoff','example','validation','observed_result']:self.assertGreater(len(c[k]),20)
 def test_visuals_exist_and_disclaim(self):
  for c in self.load('references/visual-library.json'):
   file=R/c['uri'];self.assertTrue(file.is_file())
   self.assertTrue(c['limitations'])
   if c['kind']=='TECHNICAL_DIAGRAM':
    self.assertIn('<svg',file.read_text(encoding='utf-8'));self.assertIn('Diagrama',file.read_text(encoding='utf-8'))
   else:
    self.assertTrue(c['kind'].startswith('SYNTHETIC_'));self.assertEqual(file.read_bytes()[:8],b'\x89PNG\r\n\x1a\n')
 def test_contrastive_has_differential(self):
  cases=self.load('knowledge/failure-library.json');self.assertEqual(len(cases),21)
  for c in cases:self.assertNotEqual(c['bad'],c['excellent']);self.assertIn('Confirmar',c['differential'])
 def test_every_gate_reads_real_files(self):
  for i in range(16):
   r=route('G'+str(i));self.assertTrue(all(x['sha256'] and x['text'] for x in r['loaded']))
 def test_g5_uses_new_knowledge(self):self.assertIn('knowledge/optics.md',[x['file'] for x in route('G5')['loaded']])
 def test_all_fixed_competencies(self):self.assertEqual(len(self.load('benchmarks/golden-dataset.json')['scenarios']),24)
 def test_all_exports_manual(self):
  for p in (R/'examples/prompt-exports').glob('*.json'):self.assertEqual(json.loads(p.read_text(encoding='utf-8'))['kind'],'MANUAL_PRODUCTION_EXPORT_NOT_EXECUTED')
if __name__=='__main__':unittest.main()
