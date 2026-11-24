"""Real local integration, with explicitly synthetic approvals and original schematic media."""
import json,subprocess,sys,uuid,hashlib,shutil,textwrap
from pathlib import Path
R=Path(__file__).resolve().parents[2];W=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else R.parent/'cpe-case-work';sys.path.insert(0,str(R/'scripts'))
from harness_runtime import file_hash,verify_events,now,policies
from image_tools import contact_sheet
from PIL import Image,ImageDraw,ImageFont
CASE=W/('integrated-case-'+uuid.uuid4().hex[:8]);CASE.mkdir(parents=True);workspace=CASE/'state';calls=[]
def write(name,v):p=CASE/name;p.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8');return p
def cli(command,**kwargs):
 args=[sys.executable,str(R/'scripts/cpe.py'),command,'--workspace',str(workspace)]
 for k,v in kwargs.items():
  if isinstance(v,list):
   for x in v:args+=['--'+k.replace('_','-'),str(x)]
  elif v is True:args+=['--'+k.replace('_','-')]
  elif v is not None:args+=['--'+k.replace('_','-'),str(v)]
 p=subprocess.run(args,text=True,capture_output=True,encoding='utf-8');
 if p.returncode and not (command=='blender' and p.returncode==2):raise RuntimeError(p.stderr)
 receipt=json.loads(p.stdout);result=json.loads(Path(receipt['result']).read_text(encoding='utf-8'));calls.append({'command':command,'receipt':receipt,'event_chain':verify_events(receipt['events'])});return result,receipt
host=write('host-evidence.json',{
 'google_sheets':{'status':'UNKNOWN','evidence_ref':'Historical package evidence; rediscover host capability. audits/native-validation-summary.json — historical native read/write/readback summary only; originals private'},
 'google_drive':{'status':'UNKNOWN','evidence_ref':'Historical package evidence; rediscover host capability. Native spreadsheet import and folder creation in stage1; no general media upload claim'},
 'higgsfield_read_only':{'status':'UNKNOWN','evidence_ref':'Historical package evidence; rediscover host capability. libraries/model-capabilities.snapshot.json and read-only workflow lookup'},
 'native_image_generation':{'status':'UNKNOWN','evidence_ref':'Historical package evidence; rediscover host capability. Historical case did not generate images; separate native-image-lab.json records later authorized studies'},
 'multimodal_analysis':{'status':'UNKNOWN','evidence_ref':'Historical package evidence; rediscover host capability. Tool exposed; final case image inspection follows, not inferred from documentation'},
 'local_files':{'status':'UNKNOWN','evidence_ref':'Historical package evidence; rediscover host capability. Own workspace files and tests actually read/written'},
 'interactive_ui':{'status':'UNKNOWN','evidence_ref':'Historical package evidence; rediscover host capability. Google Sheet HTTPS inspected; local HTML file protocol blocked; DOM tests only'}
})
blender=__import__('os').environ.get('CPE_BLENDER') or shutil.which('blender')
doctor,dr=cli('doctor',input=host,blender=blender)
ctx,cr=cli('task',snapshot=R/'templates/shared-state.test-fixture.json',project='TEST-CPE31',episode='TEST-CPE31-EP1',gate='G8',facet=['design','composition'],include_test=True)
opt,opr=cli('experiment',input=R/'templates/optical-experiment.json')
previs,pvr=cli('previs',input=R/'templates/previs-room.json')
blend,blr=cli('blender',input=R/'templates/previs-room.json',blender=blender)
# Original, deliberately schematic storyboard; no stock stills or native generation.
sys.path.insert(0,str(R/'examples/series-worked'))
from storyboard_media import draw_storyboard
frames=CASE/'storyboard'
durations=draw_storyboard(frames)
contact_sheet(sorted(frames.glob('*.png')),CASE/'storyboard-contact.png',3)
source=Path(previs['floorplan']);overlay,ovr=cli('overlay',source=source,input=R/'templates/overlay.json');image,imr=cli('image',source=source)
manifest=CASE/'animatic.ffconcat';manifest.write_text('ffconcat version 1.0\n'+''.join("file '"+(frames/f'P{i:02d}.png').resolve().as_posix()+"'\nduration "+str(d)+"\n" for i,d in enumerate(durations,1))+"file '"+(frames/'P06.png').resolve().as_posix()+"'\n",encoding='utf-8')
ff=shutil.which('ffmpeg');assert ff
def ffmpeg(args):
 p=subprocess.run([ff,'-nostdin','-hide_banner','-v','error',*args],text=True,capture_output=True,encoding='utf-8');
 if p.returncode:raise RuntimeError(p.stderr)
animatic=CASE/'narrative-previs.mp4';ffmpeg(['-safe','0','-f','concat','-i',str(manifest),'-f','lavfi','-i','anullsrc=r=48000:cl=mono','-r','24','-c:v','libx264','-pix_fmt','yuv420p','-c:a','aac','-t',str(sum(durations)),str(animatic)])
media,mer=cli('inspect',source=animatic,max_seconds=60,sample_fps=.5)
assert abs(float(media['metadata']['format']['duration'])-sum(durations))<.15,'Animatic duration differs from planned total'
# Independent technical fixture: intentional black, white, black, white, with silent audio.
qc=CASE/'qc-fixture.mp4';ffmpeg(['-f','lavfi','-i','color=black:s=320x180:r=24:d=1','-f','lavfi','-i','color=white:s=320x180:r=24:d=1','-f','lavfi','-i','anullsrc=r=48000:cl=mono','-filter_complex','[0:v][1:v][0:v][1:v]concat=n=4:v=1:a=0[v]','-map','[v]','-map','2:a','-c:v','libx264','-pix_fmt','yuv420p','-c:a','aac','-t','4',str(qc)])
qc_result,qcr=cli('inspect',source=qc,max_seconds=4,sample_fps=4)
assert len(qc_result['candidate_events']['black_intervals'])>=1,'Expected known black interval'
assert len(qc_result['candidate_events']['cut_seconds'])>=1,'Expected known cut'
assert qc_result['candidate_events']['silence_messages'],'Expected intentional silence'
assert Path(qc_result['frame_paths'][-1]).exists()
model,cmr=cli('compile',input=R/'examples/prompt-specs/seedance_2_5.json')
imp=write('import-spec.json',{'id':'DEMO-REFERENCE-ANIMATIC','revision':1,'kind':'NARRATIVE_PREVIS','origin':'Original local didactic animatic, not an external final production','rights_confirmed':True});imported,ir=cli('import',source=animatic,input=imp);assert imported['status']=='REVIEW_REQUIRED'
cp,cpr=cli('checkpoint',snapshot=R/'templates/shared-state.test-fixture.json');recovery,rcr=cli('recover',input=cp['checkpoint'],snapshot=R/'templates/shared-state.test-fixture.json');assert recovery['status']=='MATCHES_CURRENT_READ_COPY'
review,rv=cli('judge',review=R/'judgment-engine/revision-critic-one.json');assert review['approved'] is False
used=[{'technique':'TECH-LOCATION-SHEET','application':'Room stays 6×4 with W1/E1/N1 in deterministic plan','evidence_ref':previs['floorplan'],'limit':'2D only; no verified 3D render'},{'technique':'TECH-PROP-SHEET','application':'Cantil and hand states appear in P02–P06 captions','evidence_ref':str(CASE/'storyboard-contact.png'),'limit':'Schematic annotations; no performance/physical hand image'},{'technique':'TECH-WIDE','application':'Same position/sensor, 35 and50 mm field calculation compared','evidence_ref':opr['result'],'limit':'No lens-character simulation or generated image benchmark'}]
summary={'status':'LOCAL_INTEGRATION_EXECUTED','case_dir':str(CASE.resolve()),'executions':calls,'knowledge_application':used,'optical_experiment':opt,'blender':blend,'narrative_media_duration_seconds':media['metadata']['format']['duration'],'qc_fixture_detected':qc_result['candidate_events'],'manual_production_export':cmr['result'],'imported_preview':imported,'checkpoint':cp,'recovery':recovery,'judgment_contract':review,'approval_origin':'No human artistic approval; stage1 rehearsal separately labels simulated approvals','native_generation_executed':False,'external_paid_operations':0,'limits':['Schematic local previs and test media, not a finished film.','Final external production and human approval remain manual.','Narrative emotional effect and acting are not established by technical detection.','CLI checkpoint is local/unsynchronized; native receipt tests are separate actual connector evidence.']}
(CASE/'case-report.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8');(W/'integrated-case-location.json').write_text(json.dumps({'path':str(CASE.resolve())}),encoding='utf-8');print(json.dumps({'case':str(CASE.resolve()),'executions':len(calls),'blender_status':blend['status'],'duration':summary['narrative_media_duration_seconds'],'known_qc_events_detected':True},ensure_ascii=False))
