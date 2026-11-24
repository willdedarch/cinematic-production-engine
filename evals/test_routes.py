import pathlib,sys,unittest
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
