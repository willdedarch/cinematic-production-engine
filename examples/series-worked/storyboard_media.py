"""Render six shot-state diagrams and an original 10-second SH06 animatic from the shot cards."""
import argparse, json, shutil, subprocess, textwrap
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
shots=json.loads(Path(__file__).with_name('last-water-shots.json').read_text(encoding='utf-8'))
durations=[s['duration'] for s in shots]
assert [s['key'] for s in shots]==[f'SH{i:02d}' for i in range(1,7)] and sum(durations)==60
for previous,current in zip(shots,shots[1:]):
 assert (previous['exit'],previous['cap_out'])==(current['entry'],current['cap_in']), 'Verifique a troca de plano '+current['key']
try:font=ImageFont.truetype('arial.ttf',18)
except OSError:font=ImageFont.load_default()

def render_frame(shot, destination=None, title="Estado na saída do plano", caption=None, doorway_gaze=False, bottle_xy=None):
 caption=caption or shot['caption']
 im=Image.new('RGB',(640,360),'#18212b');d=ImageDraw.Draw(im)
 d.text((25,12),f"{shot['key']}   |   {shot['duration']} s   |   {title}",font=font,fill='#efe6d2')
 d.rectangle((25,43,615,244),outline='#b69d72',width=2)
 d.rectangle((25,107,33,158),fill='#cc985d');d.text((38,108),'W1',font=font,fill='#d4bb8e')
 d.rectangle((598,70,615,103),fill='#a6b6b1');d.text((562,70),'E1',font=font,fill='#d4bb8e')
 d.rectangle((275,49,367,60),fill='#807354');d.text((303,64),'N1',font=font,fill='#d4bb8e')
 d.pieslice((344,65,372,85),180,360,fill='#799080');d.line((341,76,374,76),fill='#799080',width=2)
 d.text((376,59),'capacete',font=font,fill='#b6c5b7')
 hands={}
 for name,x,skin,coat in [('Davi',208,'#9fb8b5','#6f7a62'),('Lia',432,'#c5aebc','#6f7787')]:
  d.ellipse((x-12,109,x+12,133),fill=skin);d.rectangle((x-18,136,x+18,185),fill=coat)
  d.text((x-20,205),name,font=font,fill=skin)
  for side,offset in [('direita',-42),('esquerda',42)]:
   point=(x+offset,160);hands[name+'.'+side]=point
   d.line((x,142,*point),fill=skin,width=4);d.ellipse((point[0]-4,156,point[0]+4,164),fill=skin)
   d.text((point[0]-6,181),'D' if side=='direita' else 'E',font=font,fill=skin)
 cx,cy=bottle_xy or hands[shot['exit']]
 d.rounded_rectangle((cx-9,cy,cx+9,cy+18),radius=4,fill='#e7b96b')
 if shot['cap_out']=='roscada_no_cantil':
  d.rectangle((cx-6,cy-5,cx+6,cy-1),fill='#8cd6e3')
 else:
  tx,ty=hands[shot['cap_out']];d.rectangle((tx-8,ty,tx+8,ty+4),fill='#8cd6e3')
 d.text((25,248),'Cantil',font=font,fill='#e7b96b');d.text((85,248),'Tampa',font=font,fill='#8cd6e3')
 d.text((180,248),'D / E = mãos do personagem',font=font,fill='#ced3d1')
 for j,line in enumerate(textwrap.wrap(caption,62)):d.text((25,283+j*23),line,font=font,fill='#e0dfdb')

 if doorway_gaze:
  for x in (208,432):
   d.ellipse((x-9,117,x-5,121),fill='#18212b')
 if destination:im.save(destination)
 return im

def draw_storyboard(frames):
 frames.mkdir(parents=True,exist_ok=True)
 for i,shot in enumerate(shots,1):
  render_frame(shot,frames/f'P{i:02d}.png',doorway_gaze=i==6)
 return durations

def shot06_animatic(destination):
 shot=shots[-1];assert shot['entry']=='Lia.esquerda' and shot['exit']=='Lia.direita'
 assert shot['cap_in']==shot['cap_out']=='Davi.esquerda' and shot['duration']==10
 fps=24
 audio="sine=frequency=285:sample_rate=48000:duration=0.9,afade=t=in:d=0.09,afade=t=out:st=0.5:d=0.4,volume=0.4,adelay=7200,apad"
 args=[shutil.which('ffmpeg') or 'ffmpeg','-hide_banner','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24',
       '-s','640x360','-r',str(fps),'-i','-','-f','lavfi','-i',audio,'-c:v','libx264','-pix_fmt','yuv420p',
       '-c:a','aac','-movflags','+faststart','-t',str(shot['duration']),str(destination)]
 keys=[(0,(474,160)),(2.25,(474,160)),(3.25,(390,160)),(4,(390,160)),(4.8,(428,127)),
       (5.4,(428,127)),(6,(390,160)),(10,(390,160))]
 with subprocess.Popen(args,stdin=subprocess.PIPE) as process:
  for frame in range(shot['duration']*fps):
   t=frame/fps
   for (start,a),(stop,b) in zip(keys,keys[1:]):
    if start<=t<stop:break
   fraction=(t-start)/(stop-start)
   xy=tuple(round(u+(v-u)*fraction) for u,v in zip(a,b))
   if t<2.25:title='Entrada';caption='Lia começa com o cantil na esquerda, como na saída de SH05. Davi fica com a tampa.'
   elif t<4:title='Troca em quadro';caption='Lia passa o cantil da esquerda para a direita.'
   elif t<7.2:title='Gole';caption='Lia ergue o cantil com a direita, bebe e baixa a mão. Davi permanece ao lado.'
   else:title='Buzina';caption='Uma buzina distante. Os dois olham para W1. O cantil permanece na direita de Lia.'
   image=render_frame(shot,title=title,caption=caption,doorway_gaze=t>=7.2,bottle_xy=xy)
   process.stdin.write(image.tobytes())
  process.stdin.close()
  if process.wait():raise RuntimeError('Falha ao codificar o ensaio de SH06.')

if __name__=='__main__':
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('output',type=Path)
 args=parser.parse_args()
 draw_storyboard(args.output/'frames')
 shot06_animatic(args.output/'SH06-previs.mp4')
