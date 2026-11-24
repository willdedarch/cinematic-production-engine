import copy, sys, unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from validate_plan import validate

def example():
    return dict(episode=1,version='draft',language='pt-BR',status='draft',target_seconds=15,speech_wps=2.5,sources=[dict(id='F1',locator='fictional example',kind='fiction')],beats=[dict(id='B1',start=0,end=10,action='Uma carta chega.',change='A decisão muda.',cause='A espera termina.',spoken_words=10,action_seconds=5,pause_seconds=1,overlap_seconds=1,source_ids=['F1'])])
class Tests(unittest.TestCase):
    def test_valid(self): self.assertEqual(validate(example()),[])
    def test_empty(self):
        x=example(); x['beats']=[]; self.assertTrue(validate(x)); self.assertEqual(validate(x,True),[])
    def test_duration(self):
        x=example(); x['target_seconds']=5; self.assertTrue(validate(x))
    def test_speech(self):
        x=example(); x['beats'][0]['spoken_words']=100; self.assertTrue(validate(x))
    def test_overlap(self):
        x=example(); x['beats'][0]['overlap_seconds']=20; self.assertTrue(validate(x))
    def test_reference(self):
        x=example(); x['beats'][0]['source_ids']=['missing']; self.assertTrue(validate(x))
    def test_duplicate(self):
        x=example(); x['beats'].append(copy.deepcopy(x['beats'][0])); self.assertTrue(validate(x))
    def test_gap(self):
        x=example(); x['beats'][0]['start']=1; self.assertTrue(validate(x))
    def test_invalid_types(self):
        x=example(); x['speech_wps']=False; x['beats'][0]['start']='0'; self.assertTrue(validate(x))
    def test_invalid_source(self):
        x=example(); x['sources'][0]['kind']='verified by magic'; self.assertTrue(validate(x))
    def test_nonfinite(self):
        x=example(); x['target_seconds']=float('nan'); self.assertTrue(validate(x))
    def test_nonobject(self): self.assertTrue(validate([]))
if __name__=='__main__': unittest.main()
