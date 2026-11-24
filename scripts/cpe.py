#!/usr/bin/env python3
"""CPE local CLI. No server, external generation or automatic Google writes."""
import argparse,json,sys,traceback
from pathlib import Path
from harness_runtime import *
from optics import optics,dof,exposure
def read(path):
 require(path is not None,'Input file required');return json.loads(Path(path).read_text(encoding='utf-8'))
def execute(a,run):
 c=a.command.lower();spec=read(a.input) if a.input else {};s=read(a.snapshot) if a.snapshot else None
 if c=='study-feedback':
  from study_feedback import record_feedback
  return record_feedback(spec,run.workspace)
 if c in {'desk-read-plan','desk-read-copy'}:
  from desk_connector import dispatch
  return dispatch(c,spec)
 if c.startswith('desk-'):
  require(s is not None,'Consulte a planilha antes de abrir a mesa')
  from desk_queue import attach_intake
  if 'intake_values' in s:s=attach_intake(s,s['intake_values'])
  if a.include_test:spec['include_test']=True
  if c=='desk-publish':
   if a.project:spec.setdefault('project',a.project)
   if a.episode:spec.setdefault('episode',a.episode)
   from desk_publish import dispatch
  elif c in {'desk-pair','desk-vote'}:
   from desk_pairs import dispatch
  else:
   from desk_queue import dispatch
  return dispatch(c,s,spec,run.workspace)
 if c in {'status','resume','next','briefing-view','bible','scene-check','canon-plan'}:
  require(s is not None,'Latest shared-state read copy required')
  validate(s)
  project = spec.get('project_id') if c=='canon-plan' else a.project
  episode = spec.get('episode_id') if c=='canon-plan' else a.episode
  target = next((e for e in s['tables']['Episodes'] if e['id']==episode),None)
  require(target and (not project or project==target['project_id']),'Episode does not belong to the selected project')
  require(not target['is_test'] or a.include_test or spec.get('include_test') is True,'Explicit test scope required')
  if not a.project:a.project=target['project_id']
 if c=='doctor':return doctor(spec,a.blender)
 if c in {'optics','dof','exposure'}:
  cost_guard(c);return optics(spec) if c=='optics' else dof(spec) if c=='dof' else exposure(spec['fps'],spec['shutter_angle_deg'])
 if c=='task':
  require(s is not None,'Agent must provide latest native read copy')
  return context(s,a.project,a.episode,a.gate or a.task.upper(),a.facet,a.model,a.include_test,
                 spec.get('intention',''),spec.get('target_ids',[]),
                 department=spec.get('department',''),purpose=spec.get('purpose',''),problem=spec.get('problem',''),
                 secondary_genres=spec.get('secondary_genres',[]),scene_complexity=spec.get('scene_complexity',''),
                 deliverable=spec.get('deliverable',''))
 if c in {'status','resume','next'}:
  require(s is not None,'Latest shared-state read copy required');validate(s);wf=[w for w in s['tables']['Workflow'] if w['episode_id']==a.episode];require(wf,'Episode not found');done={'APPROVED','LOCKED','SKIPPED'};eligible=[w for w in wf if w['status'] not in done and all(next(x for x in wf if x['gate_id']==d)['status'] in done for d in w['depends_on'].split(',') if d)]
  return {'kind':'STATE_READ_COPY','source_read_at':s['read_at'],'remote_read_performed_by_cli':False,'episode_handoff':__import__('series_bible').handoff(s,wf[0]['project_id'],a.episode,before_episode=True),'workflow':wf,'eligible':[w['gate_id'] for w in eligible],'next':'Ask agent to present eligible stage; never approve automatically'}
 if c=='validate':return {'state_valid':validate(s or spec),'saved':False}
 if c=='briefing-view':
  from episode_view import build
  return build(s,a.project,a.episode,run.dir)
 if c=='panel-copy':return panel_snapshot(s or spec)
 if c=='panel-base':return validate_panel_base(spec,s,read(a.plan) if a.plan else None)
 if c=='prepare':cost_guard('prepare_state');return validate_artistic_approval(s,spec,read(a.review) if a.review else None)
 if c in {'init','new-episode'}:
  cost_guard('init_plan')
  brief=dict(spec['brief'])
  if a.include_test:brief['include_test']=True
  if c=='new-episode':brief['new_episode']=True
  return initialize(s,brief,spec['authorization'])
 if c in {'bible','scene-check','canon-plan'}:
  from series_bible import handoff,check_assumptions,canon_plan
  if c=='canon-plan':return canon_plan(s,spec)
  bible=handoff(s,a.project,a.episode,through_sequence=spec.get('through_sequence'))
  if c=='scene-check':return {'episode_id':a.episode,'checks':check_assumptions(bible,spec['assertions'])}
  return bible
 if c in {'take-pair','take-vote','feedback-metrics'}:
  from takes import take_pair,vote_plan
  from judgment import native_metrics
  if c=='take-pair':return take_pair(s,spec)
  if c=='take-vote':return vote_plan(s,spec)
  return {**native_metrics(s),'message_origin':'UNVERIFIED_BY_LOCAL_CLI'}
 if c in {'shot-card','storyboard','shot-impact','shot-handoff','shot-compare','shot-import','shot-link','shot-repair'}:
  require(s is not None,'Latest shared-state read copy required')
  from shot_workflow import dispatch
  return dispatch(c,s,spec,run.dir)
 if c=='prewrite':
  from shared_state import check_guards
  plan=read(a.plan) if a.plan else spec
  return {'ready_to_write':check_guards(plan,s,require_prepared=True),'saved':False}
 if c=='confirm':
  from shared_state import verify_readback
  plan=read(a.plan) if a.plan else spec
  value=verify_readback(plan,s,True);cp=checkpoint(s,run.workspace,plan);return {'receipt_verified_from_files':value,'remote_io_performed_by_cli':False,**cp}
 if c in {'image','overlay','contact','compare'}:
  from image_tools import analyze,overlay,contact_sheet,compare
  action={'image':'image_analysis','overlay':'overlay','contact':'contact_sheet','compare':'pixel_compare'}[c];cost_guard(action)
  if c=='image':return analyze(a.source,run.dir/'scopes')
  if c=='overlay':return overlay(a.source,run.dir/'overlay.png',spec)
  if c=='contact':return contact_sheet(a.paths,run.dir/'contact-sheet.png')
  return compare(a.source,a.second)
 if c=='inspect':
  from media_tools import inspect
  cost_guard('media_inspection');return inspect(a.source,run.dir/'media',a.max_seconds,a.sample_fps)
 if c=='transcript':
  from media_tools import subtitles,transcribe
  cost_guard('transcript_local' if a.model_path else 'transcript_supplied');return transcribe(a.source,a.model_path) if a.model_path else subtitles(a.source)
 if c in {'previs','blender'}:
  from previs import plan,blender
  cost_guard('previs_blender' if c=='blender' else 'previs_2d');return blender(spec,run.dir/'blender',a.blender) if c=='blender' else plan(spec,run.dir/'previs')
 if c=='experiment':
  from lab_execution import run_laboratory
  return run_laboratory(experiment(spec),run.dir,a.source)
 if c=='judge':
  cost_guard('judgment_validation' if a.review else 'judgment_packet')
  if a.review:return validate_review(read(a.review))
  packet=review_packet(spec)
  if s:
   from judgment import take_preferences
   validate(s)
   matches=[(name,row) for name in PRODUCTION_ASSETS for row in s['tables'].get(name,[]) if row['id']==packet['target']['id']]
   require(len(matches)==1 and matches[0][1]['revision']==packet['target']['revision'],'Packet target must match current state copy')
   table,row=matches[0]
   require(not row['is_test'] or a.include_test,'Explicit test scope required')
   require(table!='Artifact Registry' or packet['target']['sha256']==row['sha256'],'Review file differs from the registered take')
   require(not a.project or a.project==row['project_id'],'Review target belongs to another project')
   episode=a.episode or row['episode_id']
   require(not a.episode or not row['episode_id'] or a.episode==row['episode_id'],'Review target belongs to another episode')
   if episode:require(any(e['id']==episode and e['project_id']==row['project_id'] for e in s['tables']['Episodes']),'Unknown review episode')
   packet['target']['record_sha256']=fingerprint(row);packet['target']['is_test']=row['is_test'];packet['source_read_at']=s['read_at']
   packet['take_preferences']=[] if spec.get('holdout') else take_preferences(s,row['project_id'],episode,[row['id']],a.include_test)
  return packet
 if c=='revise':
  from judgment import revision_decision
  cost_guard('revision_validation');return revision_decision(spec)
 if c=='compile':
  from prompt_compiler import compile_prompt
  cost_guard('compile_manual');return {**compile_prompt(spec),'material_class':'PRODUCTION_EXPORT','approval_status':'DRAFT_UNLESS_SEPARATELY_APPROVED','external_execution':'USER_MANUAL'}
 if c=='import':cost_guard('import_asset');return import_asset(a.source,spec['kind'],spec['id'],spec['revision'],spec['origin'],spec['rights_confirmed'])
 if c=='checkpoint':cost_guard('checkpoint');return checkpoint(s or spec,run.workspace,read(a.plan) if a.plan else None)
 if c=='recover':cost_guard('recovery');return recover(spec,s)
 raise StateError('Unknown command; use natural language with agent or --help')
def main(argv=None):
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('command');p.add_argument('--workspace',type=Path,required=True);p.add_argument('--input',type=Path);p.add_argument('--source',type=Path);p.add_argument('--second',type=Path);p.add_argument('--paths',nargs='+',type=Path);p.add_argument('--snapshot',type=Path);p.add_argument('--review',type=Path);p.add_argument('--plan',type=Path);p.add_argument('--project');p.add_argument('--episode');p.add_argument('--gate');p.add_argument('--task',default='STATUS');p.add_argument('--facet',action='append',default=[]);p.add_argument('--model',default='');p.add_argument('--include-test',action='store_true');p.add_argument('--blender');p.add_argument('--model-path',type=Path);p.add_argument('--max-seconds',type=float,default=60);p.add_argument('--sample-fps',type=float,default=1);a=p.parse_args(argv)
 run=Run(a.workspace,{'project_id':a.project,'episode_id':a.episode,'department':a.facet,'command':a.command});cmd=a.command.lower();pair={'experiment':('before_experiment','after_experiment'),'judge':('before_judgment','after_judgment'),'revise':('before_revision','after_revision'),'prepare':('before_transition','after_transition'),'compile':('before_export','after_export'),'shot-handoff':('before_export','after_export'),'import':('before_import','after_import'),'shot-import':('before_import','after_import'),'recover':('before_stage','on_recovery'),'checkpoint':('before_checkpoint','after_checkpoint')}.get(cmd,('before_stage','after_stage'))
 run.event(pair[0],'REQUESTED',inputs={'input':str(a.input) if a.input else None,'source':str(a.source) if a.source else None})
 creating=cmd in {'overlay','contact','previs','blender','compile','shot-handoff','import','shot-import','experiment'}
 if creating:run.event('before_create','REQUESTED',operation=cmd,scope_note='Local derivative or evidence artifact; not final generative production')
 try:
  approving=cmd=='prepare' and any(c.get('values',{}).get('status') in {'APPROVED','LOCKED'} for c in read(a.input).get('changes',[]))
  if approving:run.event('before_approval','REQUESTED',scope_note='Local validation of received-authorization claim; connector persistence still pending')
  result=execute(a,run);path=run.save('result.json',result)
  failed_render=cmd=='blender' and result.get('status')!='RENDERED_REOPENED_REQUIRES_VISUAL_REVIEW'
  if failed_render:status='FAILED'
  elif result.get('kind')=='WRITE_PLAN_NOT_SAVED':status='PLANNED'
  elif cmd in {'judge','prepare','validate','revise','confirm'}:status='VALIDATED'
  elif result.get('kind') in {'EXPERIMENT_PLAN_NOT_EXECUTED','REVIEW_PACKET_NOT_JUDGED','LAB_RESOURCE_REQUIRED','GUIDED_REVIEW_READY'}:status='PLANNED'
  else:status='EXECUTED'
  run.event(pair[1],status,output_ref=path,sha256=file_hash(path),operation_outcome=result.get('status',result.get('kind',status)),receipt_written=True)
  if creating:run.event('after_create',status,output_ref=path,receipt_written=True,scope_note='Status describes the requested artifact. A receipt is available for every outcome.')
  if failed_render:run.event('on_failure','FAILED',output_ref=path,operation='blender',reason=result['status'])
  if approving:run.event('after_approval','VALIDATED',output_ref=path,persisted_by_cli=False)
  print(json.dumps({'run_id':run.id,'result':path,'events':str(run.dir/'events.jsonl'),'summary':{k:v for k,v in result.items() if k in {'kind','status','recommendation','approved','state_valid','remote_read_performed_by_cli','artistic_decision'}}},ensure_ascii=False,indent=2));return 2 if failed_render else 0
 except Exception as e:
  run.event('on_failure','FAILED',error_type=type(e).__name__,message=str(e));print(json.dumps({'run_id':run.id,'error':str(e),'events':str(run.dir/'events.jsonl'),'saved_to_google':False},ensure_ascii=False),file=sys.stderr);return 1
if __name__=='__main__':raise SystemExit(main())
