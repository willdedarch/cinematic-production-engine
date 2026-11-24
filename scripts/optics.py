"""Ideal thin-lens planning. Millimetres for sensor/focal/CoC; metres for focus/field."""
import math
def positive(v,name):
 if type(v) not in (int,float) or not math.isfinite(v) or v<=0:raise ValueError(name+' must be finite and positive')
 return float(v)
def optics(spec):
 w=positive(spec.get('sensor_width_mm',36),'sensor width');h=positive(spec.get('sensor_height_mm',24),'sensor height');f=positive(spec['focal_mm'],'focal');q=positive(spec.get('squeeze',1),'squeeze');d=positive(spec.get('distance_m',3),'distance')
 ratio=positive(spec.get('aspect_ratio',w*q/h),'aspect ratio');vw=min(w*q,h*ratio);vh=min(h,w*q/ratio);aw=vw/q;ah=vh
 angles={k:math.degrees(2*math.atan(dim/(2*f))) for k,dim in [('horizontal_deg',vw),('vertical_deg',vh),('diagonal_deg',math.hypot(vw,vh))]}
 return {'active_sensor_mm':[aw,ah],'desqueezed_effective_mm':[vw,vh],'aspect_ratio':vw/vh,'fov':angles,'physical_diagonal_crop_factor':math.hypot(36,24)/math.hypot(aw,ah),'equivalent_full_frame_horizontal_mm':f*36/vw,'equivalent_full_frame_diagonal_mm':f*math.hypot(36,24)/math.hypot(vw,vh),'field_m':[d*vw/f,d*vh/f],'distance_m':d,'assumptions':['Rectilinear ideal lens at infinity; subject field approximation ignores focus extension/breathing.','Anamorphic squeeze idealized horizontally; aberration, bokeh and distortion not simulated.','Equivalences describe angle of view, not depth of field, perspective or lens character.']}
def distance_for_field(field_width_m,effective_sensor_width_mm,focal_mm):return positive(field_width_m,'field')*positive(focal_mm,'focal')/positive(effective_sensor_width_mm,'sensor')
def dof(spec):
 f=positive(spec['focal_mm'],'focal');N=positive(spec.get('f_stop',2.8),'f stop');c=positive(spec.get('coc_mm',.03),'circle of confusion');s=1000*positive(spec['focus_m'],'focus');
 if s<=f:raise ValueError('Focus must exceed focal length')
 H=f*f/(N*c)+f;near=s*(H-f)/(H+s-2*f);den=H-s;far=s*(H-f)/den if den>max(1e-9,H*1e-12) else None
 return {'hyperfocal_m':H/1000,'near_m':near/1000,'far_m':far/1000 if far is not None else None,'far_label':'infinity' if far is None else 'finite','coc_mm':c,'assumptions':['Thin lens approximation; chosen CoC depends on viewing conditions, output size and acuity.','No claim of physical compliance from a generative model.']}
def exposure(fps,angle):
 fps=positive(fps,'fps');angle=positive(angle,'shutter angle')
 if angle>360:raise ValueError('Shutter angle above 360')
 t=angle/(360*fps);return {'fps':fps,'shutter_angle_deg':angle,'exposure_seconds':t,'reciprocal_seconds':1/t}
