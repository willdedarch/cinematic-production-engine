#!/usr/bin/env python3
"""Compile a MANUAL production worksheet; never invoke a model or paid service."""
import argparse, json, math, hashlib, re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
CAT=json.loads((ROOT/'libraries/model-capabilities.snapshot.json').read_text(encoding='utf-8'))
LIMITS={'seedance_2_5':{'images':30,'videos':10,'audios':10},'seedream_v5_pro':{'images':10},'gpt_image_2_6':{'images':16},'nano_banana_2_1':{'images':14,'videos':1},'flux_3_image':{'images':10},'minimax_h3':{'images':9,'videos':3,'audios':3}}
ORDER={
 'seedance_2_5':['initial_state','action','performance','camera','sound','protected'],
 'seedream_v5_pro':['subject','space','composition','light','materials','protected'],
 'gpt_image_2_6':['purpose','subject','space','composition','light','materials','protected'],
 'nano_banana_2_1':['purpose','subject','space','composition','light','protected'],
 'flux_3_image':['subject','space','light','materials','composition','protected'],
 'minimax_h3':['initial_state','action','performance','camera','sound','protected'],
 'wan2_7':['initial_state','action','camera','performance','sound','protected'],
 'kling3_0_turbo':['initial_state','action','camera','performance','protected']}
class CompileError(ValueError):pass
def need(ok,msg):
 if not ok:raise CompileError(msg)


def protect_intent(compiled, binding):
 from creative_intent import prompt_lines
 from shared_state import fingerprint

 lines = prompt_lines(binding)
 return {**compiled,'prompt':compiled['prompt']+'\n\n'+lines,
         'creative_intent_sha256':fingerprint(binding),'intent_decision':binding['decision']}


def manual_strategy(model_id, parameters):
 if model_id=='seedance_2_5':
  return {
   't2v':'Descrever primeira imagem, ação observável e consequência. Este modo é textual.',
   'omni_reference':'Vincular cada anexo ao papel registrado. Conferir o primeiro e o último quadro quando enviados.',
   'video_edit':'Identificar origem e intervalo da alteração. Conferir duração e proporção a partir do material de retorno.',
   'video_extension':'Inspecionar a junção com a fonte e comparar continuidade da ação, escala e eixo.',
  }[parameters.get('mode','t2v')]
 return {
  'kling3_0_turbo':'Usar o quadro inicial quando houver. Conferir o destino do gesto pela mídia devolvida, e o som na montagem.',
  'minimax_h3':'Conferir início, fim e dependências dos anexos. Rever o gesto intermediário e a relação entre áudio e ação.',
  'wan2_7':'Identificar a ação pela mudança de estado. Se houver áudio anexado, confirmar as dependências na interface e rever a sincronia.',
  'seedream_v5_pro':'Separar a criação da edição localizada. Conferir dimensão, escala dos objetos e área preservada no retorno.',
  'gpt_image_2_6':'Escolher o formato antes de anexar referências. Conferir transparência, formato e quadros quando pertinentes.',
  'nano_banana_2_1':'Separar referências de imagem, vídeo e máscara. Revisar identidade, pontos alterados e elementos protegidos.',
  'flux_3_image':'Entregar referências na ordem registrada. Conferir composição e preservação de posição e escala.',
 }[model_id]


def compile_prompt(spec):
 mid=spec['model_id'];need(mid in CAT['models'],'Model not verified in catalog; refresh through read-only connector')
 model=CAT['models'][mid];params=spec.get('parameters',{});fields={p['name']:p for p in model['parameters']}
 need(isinstance(params,dict),'Parameters must be object')
 for key,val in params.items():
  need(key in fields,'Unsupported native parameter: '+key)
  p=fields[key]
  if val is None:need(p.get('nullable',False),'Parameter is not nullable');continue
  typ=p['type'];need((typ=='bool' and type(val) is bool) or (typ=='number' and type(val) in (int,float) and math.isfinite(val)) or (typ=='string' and isinstance(val,str)),'Invalid parameter type: '+key)
  if 'options' in p:need(val in p['options'],'Unsupported value: '+key)
  if 'min' in p:need(val>=p['min'],'Below minimum: '+key)
  if 'max' in p:need(val<=p['max'],'Above maximum: '+key)
  if typ=='number' and ('Whole number' in p.get('description','') or key in {'duration','batch_size','width','height','seed','frame_count','frame_duration_ms'}):need(val==int(val),'Whole number required: '+key)
 ratio=spec.get('aspect_ratio','');need(not ratio or ratio in model['aspect_ratios'],'Unsupported aspect ratio')
 refs=spec.get('references',[]);need(isinstance(refs,list),'References must be list')
 roles=set(role for media in model['medias'] for role in media.get('roles',[]));counts={};warnings=[]
 ids=set()
 for ref in refs:
  need(isinstance(ref,dict) and ref.get('id') and ref.get('uri'),'Reference identity/URI missing')
  need(ref['id'] not in ids,'Duplicate reference id');ids.add(ref['id'])
  need(ref.get('role') in roles,'Unsupported reference role: '+str(ref.get('role')))
  need(ref.get('rights_confirmed') is True,'Reference rights/authorization must be confirmed')
  counts[ref['role']]=counts.get(ref['role'],0)+1
 for role in ('start_image','end_image','mask'):need(counts.get(role,0)<=1,'Single reference role: '+role)
 lim=LIMITS.get(mid,{})
 images=counts.get('image_references',0)+(counts.get('start_image',0)+counts.get('end_image',0) if mid=='seedance_2_5' else 0)
 for label,count in [('images',images),('videos',counts.get('video_references',0)),('audios',counts.get('audio_references',0))]:
  if label in lim:need(count<=lim[label],'Reference limit: '+label)
 if mid=='seedance_2_5':
  mode=params.get('mode','t2v')
  need(not refs or mode!='t2v','t2v has no references; select an appropriate mode')
  need(not (counts.get('start_image') or counts.get('end_image')) or mode=='omni_reference','Start/end require omni_reference')
  need(('extension_mode' in params)==(mode=='video_extension'),'extension_mode only and required for video_extension')
  if mode=='video_extension':need(params.get('extension_mode') in {'forward','backward'},'extension_mode must be non-null forward/backward')
  if mode in {'video_edit','video_extension'}:need(counts.get('video_references',0)==1,'Editing/extension worksheet requires exactly one source video')
  if mode=='video_edit' and ('duration' in params or ratio):warnings.append('video_edit ignores duration/aspect_ratio; do not promise these controls')
  if mode=='video_extension' and ratio:warnings.append('video_extension follows source aspect ratio')
  if params.get('draft_job_id'):warnings.append('Draft finalization has provider constraints and billing; manual only, excluded from execution')
 if mid=='minimax_h3':
  need(not counts.get('end_image') or counts.get('start_image'),'End image requires start')
  need(not counts.get('audio_references') or (counts.get('start_image') or counts.get('image_references') or counts.get('video_references')),'Audio requires image/video')
 if mid=='gpt_image_2_6':
  output_format=params.get('output_format','png')
  need(not refs or output_format!='svg','SVG does not support references')
  for key in ('frame_count','frame_duration_ms'):
   need(output_format=='gif' or params.get(key) is None,key+' requires GIF output')
  size=params.get('size')
  if size is not None and size!='auto':
   match=re.fullmatch(r'([1-9][0-9]*)x([1-9][0-9]*)',size)
   need(bool(match),'Size must be WIDTHxHEIGHT or auto')
   if output_format=='gif':
    need(all(int(v)%16==0 for v in match.groups()),'GIF dimensions must be multiples of 16')
 if mid=='wan2_7' and refs:warnings.append('Audio count and start/end dependencies beyond returned catalog are unverified; check current UI before manual execution')
 intent=spec.get('intent',{});need(isinstance(intent,dict),'Intent must be object')
 order=ORDER[mid];unknown=set(intent)-set(order)
 need(not unknown,'Intent fields unsupported by this adapter: '+','.join(sorted(unknown)))
 need(all(isinstance(v,str) for v in intent.values()),'Intent values must be text')
 intent={key:value.strip() for key,value in intent.items()}
 need(bool(intent.get('subject') or intent.get('initial_state')),'Subject or initial state required')
 need(model['output_type']!='video' or bool(intent.get('action')),'Video action required')
 prompt='\n'.join(k.replace('_',' ').capitalize()+': '+intent[k].strip() for k in order if intent.get(k,'').strip())
 authored=''
 if spec.get('cinematic_plan') is not None:
  from cinematic_plan import compile_plan,PlanError
  try:
   authored,plan_warnings=compile_plan(spec['cinematic_plan'],model,params,refs)
  except PlanError as error:raise CompileError(str(error)) from error
  prompt+='\n\n'+authored
  warnings+=plan_warnings
 need(bool(prompt),'Empty prompt')
 if len(prompt.split())>220:warnings.append('Long prompt: inspect competing instructions; 220 words is advisory, not a model limit')
 if refs:warnings.append('Attach each reference in the supported UI role; local labels are not native @bindings')
 warnings+=['Natural-language camera/light/acting intent is a request, not a verified native parameter or result.', 'Refresh capabilities at production time; catalog snapshot is not a generation benchmark.']
 return {'kind':'MANUAL_PRODUCTION_EXPORT_NOT_EXECUTED','model_id':mid,'model_name':model['name'],'output_type':model['output_type'],'prompt':prompt,'native_parameters':params,'aspect_ratio':ratio,'reference_manifest':refs,'protected':intent.get('protected',''),'warnings':warnings,'catalog_checked_at':CAT['checked_at'],'manual_strategy':manual_strategy(mid,params),'generation_tested':False,'credits_consumed':0,'source_spec_sha256':hashlib.sha256(json.dumps(spec,sort_keys=True,ensure_ascii=False).encode()).hexdigest(),**({'authored_directions':authored} if authored else {})}
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('spec',type=Path);p.add_argument('--out',type=Path);a=p.parse_args();value=compile_prompt(json.loads(a.spec.read_text(encoding='utf-8')));text=json.dumps(value,ensure_ascii=False,indent=2)+'\n'
 if a.out:
  need(not a.out.exists(),'Refusing to overwrite export');a.out.write_text(text,encoding='utf-8')
 else:print(text)
if __name__=='__main__':main()
