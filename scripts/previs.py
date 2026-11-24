"""Portable spatial study and optional isolated Blender job. No user's scene is edited."""
from pathlib import Path
import json,math,subprocess,shutil,re,os
from optics import optics

def camera_path(cam,room,allow_external):
 """Return keyframes for straight-line camera travel in the approved room."""
 path=cam.get('path',[])
 if not isinstance(path,list):
  raise ValueError(f"{cam['id']}: camera path must be a list")
 if not path:return []
 keys=[]
 for step in path:
  if not isinstance(step,dict):raise ValueError(f"{cam['id']}: camera keyframe must be an object")
  frame=step.get('frame')
  if type(frame) is not int or frame<1 or (keys and frame<=keys[-1]['frame']):
   raise ValueError(f"{cam['id']}: positive, strictly increasing camera frames required; got {frame}")
  point=step.get('position_m')
  if not isinstance(point,(list,tuple)) or len(point)!=3 or any(type(value) not in (int,float) or not math.isfinite(value) for value in point):
   raise ValueError(f"{cam['id']}: invalid camera position at frame {frame}")
  if not allow_external and any(value<0 or value>bound for value,bound in zip(point,room)):
   raise ValueError(f"{cam['id']}: camera leaves approved room at keyframe {frame}")
  keys.append({'frame':frame,'position_m':list(point)})
 if keys[0]['frame']>1:
  keys.insert(0,{'frame':1,'position_m':list(cam['position_m'])})
 elif keys[0]['position_m']!=list(cam['position_m']):
  raise ValueError(f"{cam['id']}: frame 1 contradicts the camera starting position")
 return keys
def validate_geometry(s):
 def safe_id(value):
  return isinstance(value,str) and bool(re.fullmatch(r'[A-Za-z][A-Za-z0-9_.-]{0,63}',value)) and value.split('.')[0].upper() not in {'CON','PRN','AUX','NUL',*[f'COM{i}' for i in range(1,10)],*[f'LPT{i}' for i in range(1,10)]}
 room=s.get('room_m',[])
 if len(room)!=3 or not all(type(x) in (int,float) and math.isfinite(x) and x>0 for x in room):raise ValueError('Positive room width/depth/height required')
 if type(s.get('allow_external_camera',False)) is not bool:raise ValueError('allow_external_camera must be a boolean')
 ids=set()
 for group in ['anchors','actors','props']:
  for item in s.get(group,[]):
   if not safe_id(item.get('id')) or item['id'].casefold() in ids:raise ValueError('Unique safe spatial IDs required')
   ids.add(item['id'].casefold());pos=item['position_m']
   if len(pos)!=3 or not all(type(x) in (int,float) and math.isfinite(x) for x in pos) or not all(0<=x<=bound for x,bound in zip(pos,room)):raise ValueError('Landmark/object outside approved room')
 for cam in s.get('cameras',[]):
  if not safe_id(cam.get('id')) or cam['id'].casefold() in ids:raise ValueError('Unique safe camera ID required')
  ids.add(cam['id'].casefold())
  for p in [cam['position_m'],cam['target_m']]:
   if len(p)!=3 or not all(type(x) in (int,float) and math.isfinite(x) for x in p):raise ValueError('Camera vectors malformed')
  if cam['position_m']==cam['target_m']:raise ValueError('Camera target equals position')
  if not s.get('allow_external_camera',False) and not all(0<=x<=bound for x,bound in zip(cam['position_m'],room)):raise ValueError('Camera outside room; do not expand approved geometry')
  optics({key:cam[key] for key in ('focal_mm','sensor_width_mm','sensor_height_mm') if key in cam})
  camera_path(cam,room,s.get('allow_external_camera',False))
 return True
def plan(s,out_dir):
 validate_geometry(s);out=Path(out_dir).resolve()
 if out.exists() and any(out.iterdir()):raise ValueError('New previs directory required')
 out.mkdir(parents=True,exist_ok=True)
 from image_tools import modules
 np,Image,Ops,Draw,Font=modules();im=Image.new('RGB',(1100,820),'#172028');d=Draw.Draw(im);w,h,z=s['room_m'];scale=min(900/w,610/h)
 def p(v):return (90+v[0]*scale,730-v[1]*scale)
 d.rectangle((*p([0,h]),*p([w,0])),outline='#d6c49b',width=4);d.text((70,28),f'TECHNICAL PREVIS / room {w:g} x {h:g} x {z:g} m / origin SW',fill='#e5e0d5')
 for group,color in [('anchors','#d8b978'),('actors','#8cb8bd'),('props','#bc9cbd')]:
  for item in s.get(group,[]):
   x,y=p(item['position_m']);d.ellipse((x-9,y-9,x+9,y+9),fill=color);d.text((x+12,y-12),item['id'],fill=color)
 studies=[]
 for ci,cam in enumerate(s.get('cameras',[])):
  color=['#e3a970','#8eb8d9','#b7c985','#c69fca'][ci%4];x,y=p(cam['position_m']);tx,ty=p(cam['target_m']);d.line((x,y,tx,ty),fill=color,width=3);angle=math.atan2(ty-y,tx-x);calc=optics({'focal_mm':cam['focal_mm'],'sensor_width_mm':cam.get('sensor_width_mm',36),'sensor_height_mm':cam.get('sensor_height_mm',20.25),'distance_m':math.dist(cam['position_m'],cam['target_m'])});half=math.radians(calc['fov']['horizontal_deg']/2)
  for a in [angle-half,angle+half]:d.line((x,y,x+230*math.cos(a),y+230*math.sin(a)),fill=color,width=2)
  d.text((70+ci*240,75),cam['id']+' / '+str(cam['focal_mm'])+' mm',fill=color);d.text((x+10,y+12+ci*20),cam['id'],fill=color);studies.append({'camera_id':cam['id'],'optics':calc})
  keys=camera_path(cam,s['room_m'],s.get('allow_external_camera',False))
  if keys:
   trajectory=[p(key['position_m']) for key in keys]
   if len(trajectory)>1:d.line(trajectory,fill=color,width=4)
   for point in trajectory:d.ellipse((point[0]-3,point[1]-3,point[0]+3,point[1]+3),fill=color)
   studies[-1].update(path=keys,interpolation='LINEAR')
 d.text((70,780),'Schematic top view. No photorealism, physical light or generated identity claim.',fill='#b9c1c7');im.save(out/'floorplan.png')
 (out/'geometry.json').write_text(json.dumps(s,ensure_ascii=False,indent=2),encoding='utf-8');result={'kind':'TECHNICAL_PREVIS','method':'DETERMINISTIC_2D','geometry_valid':True,'studies':studies,'floorplan':str(out/'floorplan.png'),'artistic_approval':False};(out/'result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8');return result
def blender(s,out_dir,executable=None):
 validate_geometry(s)
 if not s.get('cameras'):raise ValueError('Blender previs requires at least one camera')
 executable=executable or os.environ.get('CPE_BLENDER') or shutil.which('blender')
 if not executable:return {'status':'UNAVAILABLE','alternative':'Use deterministic 2D plan; no installation'}
 exe=Path(executable)
 if not exe.is_file():return {'status':'UNAVAILABLE','alternative':'Use deterministic 2D plan; no installation'}
 out=Path(out_dir).resolve()
 if out.exists() and any(out.iterdir()):raise ValueError('New Blender output directory required')
 out.mkdir(parents=True,exist_ok=True);(out/'geometry.json').write_text(json.dumps(s),encoding='utf-8')
 script=Path(__file__).with_name('blender_previs.py')
 try:r=subprocess.run([str(exe),'--background','--factory-startup','--disable-autoexec','--python-exit-code','1','--python',str(script),'--',str(out/'geometry.json'),str(out)],capture_output=True,text=True,timeout=120,shell=False)
 except subprocess.TimeoutExpired:return {'status':'UNKNOWN_OUTCOME_TIMEOUT','recovery':'Inspect output before retry; do not replay blindly'}
 except OSError as error:return {'status':'STARTUP_FAILED','reason':str(error),'alternative':'Use deterministic 2D plan'}
 (out/'blender.log').write_text(r.stdout+'\n'+r.stderr,encoding='utf-8');result_file=out/'blender-result.json'
 if r.returncode or not result_file.is_file():
  entered_script='CPE_PREVIS_STARTED' in r.stdout
  return {'status':'PREVIS_FAILED' if entered_script else 'STARTUP_NOT_CONFIRMED','exit_code':r.returncode,
          'entered_previs_script':entered_script,'log':str(out/'blender.log'),'alternative':'Use deterministic 2D plan'}
 try:
  result=json.loads(result_file.read_text(encoding='utf-8'))
  verify_blender_files(result,out,[cam['id'] for cam in s['cameras']])
 except (ValueError,TypeError,KeyError,OSError) as error:
  return {'status':'PREVIS_FAILED','reason':str(error),'entered_previs_script':True,'log':str(out/'blender.log')}
 return result

def verify_blender_files(result,out,camera_ids):
 """Confirm the new files belong to this invocation before reporting success."""
 if result['status']!='RENDERED_REOPENED_REQUIRES_VISUAL_REVIEW' or result['owned_objects']<len(camera_ids):
  raise ValueError('Missing confirmation that the previs project reopened')
 blend=out/'technical-previs.blend'
 if Path(result['blend']).resolve()!=blend or not blend.is_file() or not blend.stat().st_size:
  raise ValueError('Previs project is absent or empty')
 expected=[out/(camera_id+'.png') for camera_id in camera_ids]
 if [cam['id'] for cam in result['cameras']]!=camera_ids or [Path(p).resolve() for p in result['renders']]!=expected:
  raise ValueError('Renders do not match the requested cameras')
 for render in expected:
  with render.open('rb') as image:
   if image.read(8)!=b'\x89PNG\r\n\x1a\n':raise ValueError('Expected a PNG render for '+render.stem)
