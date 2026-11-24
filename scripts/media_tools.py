"""Local FFprobe/FFmpeg inspection, bounded derivatives and optional offline transcription."""
from pathlib import Path
import subprocess,shutil,json,hashlib,re,math
from fractions import Fraction
def tool(name):
 p=shutil.which(name)
 if not p:raise RuntimeError(name+' unavailable; manual inspection required. Nothing installed.')
 return p
def run(args,timeout=120):
 p=subprocess.run(args,capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=timeout,shell=False)
 if p.returncode:raise RuntimeError('Local tool failed: '+p.stderr[-2000:])
 return p
def local_file(path):
 p=Path(path).resolve()
 if not p.is_file():raise ValueError('An accessible authorized local file is required')
 return p
def probe(path):
 p=local_file(path);r=run([tool('ffprobe'),'-v','error','-protocol_whitelist','file,pipe','-show_format','-show_streams','-of','json',str(p)]);v=json.loads(r.stdout)
 for s in v.get('streams',[]):
  for k in ['r_frame_rate','avg_frame_rate']:
   if s.get(k) and s[k]!='0/0':s[k+'_numeric']=float(Fraction(s[k]))
 with p.open('rb') as source:
  signature=hashlib.file_digest(source,'sha256').hexdigest() if hasattr(hashlib,'file_digest') else _stream_digest(source)
 v.update(source=str(p),source_sha256=signature,result_kind='METADATA_NOT_ARTISTIC_VERDICT',limits=['Stream offsets/duration do not prove lip sync.','Reported color tags are metadata, not independently verified color science.'])
 return v

def _stream_digest(source):
 digest=hashlib.sha256()
 for block in iter(lambda:source.read(1024*1024),b''):
  digest.update(block)
 return digest.hexdigest()

def candidate_events(logs,duration):
 """Publish candidates on the half-open analysis window [0, duration)."""
 number=r'[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?'
 def clip(value):
  return max(0.0,min(duration,value))
 cuts=sorted({float(v) for v in re.findall(r'pts_time:\s*('+number+')',logs.get('cuts','')) if 0<float(v)<duration})
 black=[]
 for start,end in re.findall(r'black_start:('+number+r')\s+black_end:('+number+r')',logs.get('black_freeze','')):
  a,b=clip(float(start)),clip(float(end))
  if a<b:black.append({'start':a,'end':b,'duration':b-a})

 def intervals(pattern,log):
  start=None
  results=[]
  for event,token in re.findall(pattern,log):
   time=float(token)
   if event=='start':
    start=time
   elif start is not None:
    a,b=clip(start),clip(time)
    if a<b:results.append({'start':a,'end':b,'duration':b-a,'ends_at_window':b==duration})
    start=None
  if start is not None and start<duration:
   a=clip(start)
   results.append({'start':a,'end':duration,'duration':duration-a,'ends_at_window':True})
  return results

 freezes=intervals(r'lavfi\.freezedetect\.freeze_(start|end):\s*('+number+')',logs.get('black_freeze',''))
 silences=intervals(r'silence_(start|end):\s*('+number+')',logs.get('silence',''))
 def messages(items,stem):
  return [f'{stem}_{key}: {x[key]:g}' for x in items for key in ('start','end','duration')]
 boundaries=[0,*cuts,duration]
 return {'cut_seconds':cuts,'black_intervals':black,'freeze_intervals':freezes,'silence_intervals':silences,
         'freeze_messages':messages(freezes,'lavfi.freezedetect.freeze'),'silence_messages':messages(silences,'silence'),
         'candidate_shot_durations_seconds':[b-a for a,b in zip(boundaries,boundaries[1:])]}
def inspect(path,out_dir,max_seconds=60,sample_fps=1):
 p=local_file(path);out=Path(out_dir).resolve()
 if out.exists() and any(out.iterdir()):raise ValueError('Use an empty new analysis directory')
 if not(0<max_seconds<=600 and 0<sample_fps<=4 and max_seconds*sample_fps<=600):raise ValueError('Bound analysis duration/sample count')
 out.mkdir(parents=True,exist_ok=True);meta=probe(p);streams=meta.get('streams',[]);video=next((s for s in streams if s['codec_type']=='video'),None);audio=next((s for s in streams if s['codec_type']=='audio'),None);logs={};frames=[]
 duration=min(float(meta.get('format',{}).get('duration',max_seconds)),max_seconds)
 if not math.isfinite(duration) or duration<=0:raise ValueError('Positive finite analysis window required')
 base=[tool('ffmpeg'),'-nostdin','-hide_banner','-v','info','-protocol_whitelist','file,pipe','-t',str(duration),'-i',str(p)]
 trim=f'trim=end={duration},'
 if video:
  r=run(base+['-vf',trim+'blackdetect=d=0.2:pix_th=0.03,freezedetect=n=-50dB:d=0.5','-an','-f','null','-']);logs['black_freeze']=r.stderr
  r=run(base+['-vf',trim+"select='gt(scene,0.35)',showinfo",'-an','-f','null','-']);logs['cuts']=r.stderr
  run(base+['-vf',trim+f'fps={sample_fps},scale=640:-2','-an',str(out/'frame_%04d.png')]);frames=sorted(out.glob('frame_*.png'))
 if audio:logs['silence']=run(base+['-vn','-af',f'atrim=end={duration},silencedetect=n=-35dB:d=0.25','-f','null','-']).stderr
 for name,text in logs.items():(out/(name+'.log')).write_text(text,encoding='utf-8')
 candidates=candidate_events(logs,duration)
 motion=[]
 if frames:
  from image_tools import modules,contact_sheet,read_image
  np,Image,Ops,Draw,Font=modules();prev=None
  for i,f in enumerate(frames):
   im,_=read_image(f);small=np.asarray(im.resize((96,54))).astype(float);value=None if prev is None else float(np.abs(small-prev).mean());motion.append({'nominal_sample_seconds':i/sample_fps,'mean_absolute_rgb_change':value,'possible_repeated_sample':value==0 if value is not None else None,'mean_encoded_rgb':float(small.mean())});prev=small
  # Representative start/end samples, plus a bounded overview; all frames remain available.
  count=min(14,len(frames));indices=[round(i*(len(frames)-1)/(count-1)) for i in range(count)] if count>1 else [0];picks=[frames[i] for i in sorted(set(indices))];contact_sheet(picks,out/'contact-sheet.png')
 result={'metadata':meta,'analyzed_seconds':duration,'source_duration_seconds':meta.get('format',{}).get('duration'),'sample_fps':sample_fps,'frame_paths':[str(f) for f in frames],'candidate_events':candidates,'motion_samples':motion,'audio_video_start_delta_seconds':float(audio.get('start_time',0))-float(video.get('start_time',0)) if audio and video else None,'limitations':['Threshold candidates may be fades, intentional still shots, silence or motion rather than faults.','Sampling can miss frames, fast cuts, brief flashes and local motion; nominal times are not exact source frame timecodes.','No automatic identity, geometry, narrative, acting or artistic verdict.','Narrative and sound continuity require inspecting ordered frames plus playback/script; contact sheet alone is insufficient.'],'artistic_status':'NOT_EVALUATED'}
 (out/'analysis.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8');return result
def subtitles(path):
 text=local_file(path).read_text(encoding='utf-8-sig');entries=[]
 pattern=r'(\d\d):(\d\d):(\d\d)[,.](\d{3})\s*-->\s*(\d\d):(\d\d):(\d\d)[,.](\d{3})'
 def seconds(t):return int(t[0])*3600+int(t[1])*60+int(t[2])+int(t[3])/1000
 for block in re.split(r'\n\s*\n',text.strip()):
  m=re.search(pattern,block)
  if not m:raise ValueError('Malformed subtitle timing')
  a,b=seconds(m.groups()[:4]),seconds(m.groups()[4:]);body=block[m.end():].strip()
  if not(body and b>a):raise ValueError('Subtitle text/positive interval required')
  entries.append({'start':a,'end':b,'text':body})
 return {'origin':'SUPPLIED_SUBTITLES_NOT_ASR','entries':entries,'gaps_seconds':[entries[i]['start']-entries[i-1]['end'] for i in range(1,len(entries))],'limitations':['Overlapping cues may be intentional; subtitles do not independently prove spoken words or lip sync.']}
def transcribe(path,model_path):
 path=local_file(path);model_path=Path(model_path).resolve()
 if not model_path.is_dir():raise ValueError('Authorized existing local model directory required; no downloads')
 try:from faster_whisper import WhisperModel
 except ImportError:raise RuntimeError('Faster Whisper unavailable; use user-supplied SRT/text. No installation performed.')
 model=WhisperModel(str(model_path),device='cpu',compute_type='int8',local_files_only=True);segments,info=model.transcribe(str(path));return {'origin':'LOCAL_ASR_UNVERIFIED','language':info.language,'entries':[{'start':x.start,'end':x.end,'text':x.text} for x in segments],'limitations':['ASR text requires listening and human correction; names/dialects/noise may be wrong.']}
