import unittest,sys,tempfile,json,math,hashlib,importlib.util
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
from optics import *
from previs import validate_geometry,plan
class OpticsTests(unittest.TestCase):
 def test_fullframe_50(self):
  v=optics({'focal_mm':50});self.assertAlmostEqual(v['fov']['horizontal_deg'],39.5977527,places=5);self.assertEqual(v['field_m'],[2.16,1.44])
 def test_crop_169(self):self.assertEqual(optics({'focal_mm':50,'aspect_ratio':16/9})['active_sensor_mm'],[36,20.25])
 def test_vertical_crop(self):
  v=optics({'focal_mm':50,'aspect_ratio':9/16});self.assertAlmostEqual(v['aspect_ratio'],9/16);self.assertAlmostEqual(v['active_sensor_mm'][0],13.5)
 def test_anamorphic_horizontal(self):
  a=optics({'focal_mm':50,'squeeze':2});b=optics({'focal_mm':50});self.assertGreater(a['fov']['horizontal_deg'],b['fov']['horizontal_deg']);self.assertEqual(a['fov']['vertical_deg'],b['fov']['vertical_deg'])
 def test_lens_change_same_position_not_perspective_claim(self):self.assertGreater(optics({'focal_mm':35})['field_m'][0],optics({'focal_mm':50})['field_m'][0])
 def test_distance_inverse(self):self.assertAlmostEqual(distance_for_field(2.16,36,50),3)
 def test_shutter_180_24(self):self.assertAlmostEqual(exposure(24,180)['exposure_seconds'],1/48)
 def test_shutter_90_24(self):self.assertAlmostEqual(exposure(24,90)['exposure_seconds'],1/96)
 def test_shutter_bad(self):self.assertRaises(ValueError,exposure,24,361)
 def test_negative_focal(self):self.assertRaises(ValueError,optics,{'focal_mm':-1})
 def test_nonfinite(self):self.assertRaises(ValueError,optics,{'focal_mm':float('nan')})
 def test_boolean_sensor(self):self.assertRaises(ValueError,optics,{'focal_mm':50,'sensor_width_mm':True})
 def test_dof_50(self):
  d=dof({'focal_mm':50,'focus_m':3,'f_stop':2.8,'coc_mm':.03});self.assertAlmostEqual(d['hyperfocal_m'],29.8119047619,places=5);self.assertLess(d['near_m'],3);self.assertGreater(d['far_m'],3)
 def test_far_infinity(self):self.assertIsNone(dof({'focal_mm':24,'focus_m':50,'f_stop':8})['far_m'])
 def test_focus_inside_lens(self):self.assertRaises(ValueError,dof,{'focal_mm':50,'focus_m':.01})
 def test_more_closed_deeper(self):self.assertLess(dof({'focal_mm':50,'focus_m':3,'f_stop':8})['near_m'],dof({'focal_mm':50,'focus_m':3,'f_stop':2})['near_m'])
@unittest.skipUnless(importlib.util.find_spec('PIL') and importlib.util.find_spec('numpy'),'Optional Pillow/NumPy unavailable')
class ImageAndSpace(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.d=Path(self.tmp.name)
  from PIL import Image
  self.im=self.d/'source.png';Image.new('RGB',(320,180),(80,120,160)).save(self.im);self.hash=hashlib.sha256(self.im.read_bytes()).hexdigest()
 def tearDown(self):self.tmp.cleanup()
 def test_analysis_no_art_score(self):
  from image_tools import analyze
  a=analyze(self.im,self.d/'scopes');self.assertEqual(a['dimensions_oriented'],[320,180]);self.assertEqual(sum(a['rgb_histograms'][0]),320*180);self.assertNotIn('artistic_score',a)
 def test_overlay_preserves_original(self):
  from image_tools import overlay
  overlay(self.im,self.d/'guide.png',{'guides':['thirds','golden-grid','golden-spiral','diagonal','triangle','perspective','headroom','leadroom','safe','symmetry','center'],'crop_ratio':2.39});self.assertEqual(hashlib.sha256(self.im.read_bytes()).hexdigest(),self.hash)
 def test_overlay_refuses_overwrite(self):
  from image_tools import overlay
  self.assertRaises(ValueError,overlay,self.im,self.im,{})
 def test_unknown_guide(self):
  from image_tools import overlay
  self.assertRaises(ValueError,overlay,self.im,self.d/'guide.png',{'guides':['fake']})
 def test_compare_same_and_size_mismatch(self):
  from image_tools import compare
  from PIL import Image
  self.assertTrue(compare(self.im,self.im)['identical_pixels']);other=self.d/'other.png';Image.new('RGB',(100,100)).save(other);self.assertFalse(compare(self.im,other)['same_dimensions'])
 def test_contact_sheet(self):
  from image_tools import contact_sheet
  self.assertEqual(contact_sheet([self.im,self.im],self.d/'sheet.png',2)['count'],2)
 def test_geometry_and_2d(self):
  s=json.loads((R/'templates/previs-room.json').read_text(encoding='utf-8'));self.assertTrue(validate_geometry(s));v=plan(s,self.d/'previs');self.assertTrue(Path(v['floorplan']).exists());self.assertFalse(v['artistic_approval'])
 def test_geometry_protected(self):
  s=json.loads((R/'templates/previs-room.json').read_text(encoding='utf-8'));s['anchors'][0]['position_m'][0]=-1;self.assertRaises(ValueError,validate_geometry,s)
 def test_duplicate_anchor(self):
  s=json.loads((R/'templates/previs-room.json').read_text(encoding='utf-8'));s['actors'][0]['id']='W1';self.assertRaises(ValueError,validate_geometry,s)
 def test_supplied_subtitles(self):
  from media_tools import subtitles
  p=self.d/'dialogue.srt';p.write_text('1\n00:00:01,000 --> 00:00:02,000\nGuarde.\n\n2\n00:00:03,000 --> 00:00:04,000\nDividimos.\n',encoding='utf-8');a=subtitles(p);self.assertEqual(a['gaps_seconds'],[1.0]);self.assertIn('NOT_ASR',a['origin'])
if __name__=='__main__':unittest.main()
