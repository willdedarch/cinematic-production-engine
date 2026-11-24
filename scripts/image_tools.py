"""Optional Pillow/NumPy derivatives. Numeric indicators never grade cinematic quality."""
from pathlib import Path
import hashlib,json,math
def modules():
 try:
  import numpy as np
  from PIL import Image,ImageOps,ImageDraw,ImageFont
 except ImportError:raise RuntimeError('Pillow/NumPy unavailable; use textual/visual review. No installation performed.')
 return np,Image,ImageOps,ImageDraw,ImageFont
def fresh_path(out,source=None):
 out=Path(out).resolve()
 if out.exists() or (source and out==Path(source).resolve()):raise ValueError('Preserve original/history; choose a new derivative path')
 out.parent.mkdir(parents=True,exist_ok=True);return out
def read_image(path):
 np,Image,Ops,Draw,Font=modules();p=Path(path);raw=p.read_bytes()
 with Image.open(p) as im:
  im.verify()
 with Image.open(p) as im:
  info={'format':im.format,'mode':im.mode,'dimensions_raw':list(im.size),'icc_present':bool(im.info.get('icc_profile')),'gamma_tag':im.info.get('gamma'),'exif_present':bool(im.getexif()),'sha256':hashlib.sha256(raw).hexdigest()};rgb=Ops.exif_transpose(im).convert('RGB').copy()
 return rgb,info
def analyze(path,out_dir=None):
 np,Image,Ops,Draw,Font=modules();im,meta=read_image(path);arr=np.asarray(im).astype(float);y=.2126*arr[:,:,0]+.7152*arr[:,:,1]+.0722*arr[:,:,2]
 lap=-4*y+np.roll(y,1,0)+np.roll(y,-1,0)+np.roll(y,1,1)+np.roll(y,-1,1)
 hist=[np.histogram(arr[:,:,i],bins=256,range=(0,256))[0].tolist() for i in range(3)];lum=np.histogram(y,bins=256,range=(0,256))[0].tolist();palette=im.quantize(colors=8).convert('RGB').getcolors(im.width*im.height)
 result={**meta,'dimensions_oriented':list(im.size),'aspect_ratio':im.width/im.height,'rgb_histograms':hist,'luma_histogram':lum,'mean_encoded_luma':float(y.mean()),'encoded_luma_stddev':float(y.std()),'possible_channel_clipping_fraction':float((arr>=254).any(axis=2).mean()),'near_black_fraction':float((y<=1).mean()),'laplacian_variance_indicator':float(lap[1:-1,1:-1].var()) if min(im.size)>2 else None,'palette':[{'rgb':list(c),'fraction':n/(im.width*im.height)} for n,c in sorted(palette or [],reverse=True)],'limitations':['8-bit RGB conversion; source transfer function/colorimetry not inferred from appearance.','Display-value Rec.709-weighted luma approximation, not calibrated linear-light scopes.','Clipping/edge indicators are candidates; white backgrounds, grain and intended softness require interpretation.','No automatic CGI, identity, historical or artistic quality verdict.']}
 if out_dir:
  out=Path(out_dir);out.mkdir(parents=True,exist_ok=True);im_small=im.copy();im_small.thumbnail((480,270));a=np.asarray(im_small).astype(float);l=.2126*a[:,:,0]+.7152*a[:,:,1]+.0722*a[:,:,2]
  for mode in ['waveform','rgb-parade','vectorscope']:
   canvas=Image.new('RGB',(768,330),'#171f27');draw=Draw.Draw(canvas);draw.text((15,10),mode+' / encoded RGB approximation',fill='#dfd7c7')
   if mode=='vectorscope':
    draw.ellipse((240,50,520,330),outline='#64717c');cb=(a[:,:,2]-l)/1.8556;cr=(a[:,:,0]-l)/1.5748
    for xx,yy in zip(cb.ravel()[::3],cr.ravel()[::3]):draw.point((384+xx,190-yy),fill='#7bb8b3')
   else:
    channels=[l] if mode=='waveform' else [a[:,:,i] for i in range(3)]
    for i,ch in enumerate(channels):
     left=12+i*250;span=744 if len(channels)==1 else 242;color='#d8c494' if len(channels)==1 else ['#d57b7b','#8ecb96','#8daee8'][i]
     for x in range(ch.shape[1]):
      for value in ch[:,x][::2]:draw.point((left+x*span/ch.shape[1],315-value),fill=color)
   dest=fresh_path(out/(mode+'.png'));canvas.save(dest)
  result['scope_images']=[str(out/(m+'.png')) for m in ['waveform','rgb-parade','vectorscope']]
 return result
def overlay(source,out,spec):
 np,Image,Ops,Draw,Font=modules();im,meta=read_image(source);draw=Draw.Draw(im);w,h=im.size;color=spec.get('color','#edc075');guides=spec.get('guides',['thirds']);allowed={'thirds','golden-grid','golden-spiral','symmetry','center','diagonal','triangle','perspective','headroom','leadroom','safe'}
 if not set(guides)<=allowed:raise ValueError('Unknown composition guide')
 def line(xy):draw.line(xy,fill=color,width=max(1,w//600))
 for g in guides:
  if g in {'thirds','golden-grid'}:
   for t in ([1/3,2/3] if g=='thirds' else [.381966,.618034]):line((w*t,0,w*t,h));line((0,h*t,w,h*t))
  elif g in {'symmetry','center'}:line((w/2,0,w/2,h));line((0,h/2,w,h/2))
  elif g=='diagonal':line((0,0,w,h));line((0,h,w,0))
  elif g=='triangle':line((w*.2,h*.8,w*.5,h*.2,w*.8,h*.8,w*.2,h*.8))
  elif g=='perspective':
   vp=spec.get('vanishing_point',[.5,.4]);x,y=vp[0]*w,vp[1]*h
   for corner in [(0,0),(w,0),(0,h),(w,h)]:line((*corner,x,y))
  elif g=='headroom':line((0,h*.1,w,h*.1))
  elif g=='leadroom':line((w*.65,0,w*.65,h));draw.text((w*.66,h*.5),'lead room guide',fill=color)
  elif g=='safe':
   for margin in [.05,.10]:draw.rectangle((w*margin,h*margin,w*(1-margin),h*(1-margin)),outline=color,width=2)
  elif g=='golden-spiral':
   # Logarithmic golden spiral: radius grows by phi every quarter turn; guide is normalized to fit.
   phi=(1+math.sqrt(5))/2;pts=[]
   for i in range(361):
    t=i*math.pi/90;r=.42*min(w,h)*phi**((t-4*math.pi)/(math.pi/2));pts.append((w*.5+r*math.cos(t),h*.5+r*math.sin(t)))
   line(pts)
 for box in spec.get('regions',[]):
  x0,y0,x1,y1=box['rect'];
  if not(0<=x0<x1<=1 and 0<=y0<y1<=1):raise ValueError('Normalized region invalid')
  draw.rectangle((x0*w,y0*h,x1*w,y1*h),outline=color,width=3);draw.text((x0*w+3,y0*h+3),box.get('label','region'),fill=color)
 if spec.get('crop_ratio'):
  ratio=float(spec['crop_ratio']);
  if not math.isfinite(ratio) or ratio<=0:raise ValueError('Invalid crop ratio')
  cw=min(w,h*ratio);ch=cw/ratio;draw.rectangle(((w-cw)/2,(h-ch)/2,(w+cw)/2,(h+ch)/2),outline='#f6f2e9',width=4)
 dest=fresh_path(out,source);im.save(dest);return {'kind':'TECHNICAL_PREVIS','source_sha256':meta['sha256'],'derivative':str(dest),'guides':guides,'quality_judged':False}
def contact_sheet(paths,out,columns=3):
 np,Image,Ops,Draw,Font=modules()
 if type(columns) is not int or not 1<=columns<=8 or not paths:raise ValueError('Invalid contact sheet layout')
 ims=[read_image(p)[0] for p in paths];rows=math.ceil(len(ims)/columns);canvas=Image.new('RGB',(columns*400,rows*270),'#151d24');draw=Draw.Draw(canvas)
 for i,(p,im) in enumerate(zip(paths,ims)):
  thumb=im.copy();thumb.thumbnail((388,232));x=(i%columns)*400;y=(i//columns)*270;canvas.paste(thumb,(x+(400-thumb.width)//2,y+8));draw.text((x+8,y+244),Path(p).name[:48],fill='#dedbd3')
 dest=fresh_path(out);canvas.save(dest);return {'derivative':str(dest),'sources':[str(p) for p in paths],'count':len(paths)}
def compare(a,b):
 np,Image,Ops,Draw,Font=modules();ia,ma=read_image(a);ib,mb=read_image(b)
 if ia.size!=ib.size:return {'same_dimensions':False,'pixel_comparison':None,'reason':'Do not silently align/resize different versions'}
 aa=np.asarray(ia).astype(float);bb=np.asarray(ib).astype(float)
 return {'same_dimensions':True,'mean_absolute_encoded_rgb_difference':float(np.abs(aa-bb).mean()),'identical_pixels':bool(np.array_equal(aa,bb)),'source_hashes':[ma['sha256'],mb['sha256']],'limitation':'Pixel difference does not identify cause or artistic improvement.'}
