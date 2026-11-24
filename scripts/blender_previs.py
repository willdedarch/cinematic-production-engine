"""Run only in a fresh background Blender process, never via the live user scene."""
import bpy,json,sys,math
from pathlib import Path
from mathutils import Vector
def main():
 if not bpy.app.background:raise RuntimeError('Isolated background process required; live session untouched')
 print('CPE_PREVIS_STARTED',flush=True)
 args=sys.argv[sys.argv.index('--')+1:];s=json.loads(Path(args[0]).read_text(encoding='utf-8'));out=Path(args[1]).resolve()
 sys.path.insert(0,str(Path(__file__).parent));from previs import validate_geometry,camera_path
 validate_geometry(s);bpy.ops.wm.read_factory_settings(use_empty=True);scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
 owner=bpy.data.collections.new('CPE_TECHNICAL_PREVIS');scene.collection.children.link(owner)
 def box(name,center,size,color):
  verts=[(x*size[0]/2,y*size[1]/2,z*size[2]/2) for x,y,z in [(-1,-1,-1),(-1,-1,1),(-1,1,-1),(-1,1,1),(1,-1,-1),(1,-1,1),(1,1,-1),(1,1,1)]];faces=[(0,4,6,2),(1,3,7,5),(0,1,5,4),(2,6,7,3),(0,2,3,1),(4,5,7,6)];mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update();obj=bpy.data.objects.new(name,mesh);owner.objects.link(obj);obj.location=center;obj.color=(*color,1);obj['cpe_owned']=True;return obj
 w,h,z=s['room_m'];box('CPE_FLOOR',(w/2,h/2,-.1),(w,h,.2),(.29,.31,.30));box('CPE_NORTH',(w/2,h+.05,z/2),(w,.1,z),(.5,.5,.48))
 # Deliberate cutaway: other walls are wire guides rather than moved geometry.
 for a in s.get('anchors',[]):box('CPE_'+a['id'],a['position_m'],(.15,.15,.25),(.7,.55,.3))
 for a in s.get('actors',[]):
  pos=a['position_m'];box('CPE_'+a['id'],(pos[0],pos[1],.85),(.42,.28,1.7),(.25,.48,.51))
 for a in s.get('props',[]):box('CPE_'+a['id'],a['position_m'],(.15,.10,.25),(.55,.4,.55))
 scene.render.engine='BLENDER_WORKBENCH';scene.display.shading.light='STUDIO';scene.display.shading.color_type='OBJECT';scene.display.shading.show_shadows=True;scene.render.resolution_x=960;scene.render.resolution_y=540;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.render.fps=24
 renders=[];cams=[]
 for c in s['cameras']:
  data=bpy.data.cameras.new('CPE_'+c['id']);data.lens=c['focal_mm'];data.sensor_width=c.get('sensor_width_mm',36);data.sensor_fit='HORIZONTAL';cam=bpy.data.objects.new(data.name,data);owner.objects.link(cam);cam.location=c['position_m'];cam.rotation_euler=(Vector(c['target_m'])-cam.location).to_track_quat('-Z','Y').to_euler();cam['cpe_owned']=True;scene.camera=cam;bpy.context.view_layer.update()
  assert abs(cam.data.lens-c['focal_mm'])<1e-6
  keys=camera_path(c,s['room_m'],s.get('allow_external_camera',False))
  if keys:
   # Every straight segment between points in an axis-aligned box stays inside it.
   # Use linear interpolation for all XYZ channels to avoid overshoot between keys.
   for key in keys:
    cam.location=key['position_m']
    cam.keyframe_insert(data_path='location',frame=key['frame'])
   animation=cam.animation_data
   if getattr(animation,'action_slot',None):
    curves=[curve for layer in animation.action.layers for strip in layer.strips
            if hasattr(strip,'channelbag') for bag in [strip.channelbag(animation.action_slot)]
            if bag is not None for curve in bag.fcurves]
   else:
    curves=list(animation.action.fcurves)
   position_curves=[curve for curve in curves if curve.data_path=='location']
   if len(position_curves)!=3:raise RuntimeError(f"{c['id']}: cannot verify all three animated coordinates")
   for curve in position_curves:
    for point in curve.keyframe_points:point.interpolation='LINEAR'
    curve.update()
   scene.frame_end=max(scene.frame_end,keys[-1]['frame'])
   for first,last in zip(keys,keys[1:]):
    middle=(first['frame']+last['frame'])/2
    scene.frame_set(math.floor(middle),subframe=middle%1)
    expected=(Vector(first['position_m'])+Vector(last['position_m']))/2
    actual=cam.evaluated_get(bpy.context.evaluated_depsgraph_get()).matrix_world.translation
    if (actual-expected).length>1e-4:
     raise RuntimeError(f"{c['id']}: camera position at frame {middle} is {tuple(actual)}, expected {tuple(expected)}")
  scene.frame_set(1);scene.render.filepath=str(out/(c['id']+'.png'));bpy.ops.render.render(write_still=True);renders.append(scene.render.filepath);cams.append({'id':c['id'],'focal_mm':data.lens,'sensor_width_mm':data.sensor_width,'angle_x':data.angle_x})
  if keys:cams[-1].update(trajectory=keys,interpolation='LINEAR',path_midpoints_verified=len(keys)-1)
 blend=out/'technical-previs.blend';bpy.ops.wm.save_as_mainfile(filepath=str(blend));count=len(owner.objects);bpy.ops.wm.open_mainfile(filepath=str(blend));assert len(bpy.data.collections['CPE_TECHNICAL_PREVIS'].objects)==count
 result={'status':'RENDERED_REOPENED_REQUIRES_VISUAL_REVIEW','kind':'TECHNICAL_PREVIS','blender_version':bpy.app.version_string,'owned_objects':count,'blend':str(blend),'renders':renders,'cameras':cams,'limits':['Workbench cutaway graybox; no physical lens character, DOF or lighting validation.','No final assets or facial identity generated.']};(out/'blender-result.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print('RESULT '+json.dumps(result))
if __name__=='__main__':main()
