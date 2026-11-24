#!/usr/bin/env python3
"""Evidence contracts, blind packets and correction bounds. No automatic artistic scoring."""
import argparse,copy,hashlib,json,uuid,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class JudgmentError(ValueError):pass
def need(ok,msg):
 if not ok:raise JudgmentError(msg)
def digest(v):return hashlib.sha256(json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def nonempty(v):return isinstance(v,str) and bool(v.strip())
ROLES={
 'story':['Story Critic','Audience Critic'], 'screenplay':['Story Critic','Film Critic'], 'dialogue':['Story Critic','Performance Critic'],
 'emotion':['Story Critic','Audience Critic'],'suspense':['Audience Critic','Story Critic'],'retention':['Audience Critic'],
 'direction':['Film Critic','Continuity Auditor'],'performance':['Performance Critic','Story Critic'],'casting':['Performance Critic','Production Design Critic'],
 'character-sheets':['Production Design Critic','Continuity Auditor'],'performance-sheets':['Performance Critic'],'wardrobe':['Production Design Critic','Continuity Auditor'],
 'locations':['Production Design Critic','Cinematography Critic'],'geometry':['Continuity Auditor','Technical Auditor'],'props':['Production Design Critic','Continuity Auditor'],
 'photography':['Cinematography Critic','Film Critic'],'optics':['Cinematography Critic','Technical Auditor'],'composition':['Cinematography Critic','Film Critic'],
 'lighting':['Cinematography Critic','Production Design Critic'],'color-texture':['Cinematography Critic','Production Design Critic'],'atmosphere':['Cinematography Critic','Film Critic'],
 'living-world':['Production Design Critic','Film Critic'],'storyboards':['Film Critic','Continuity Auditor'],'shot-design':['Film Critic','Technical Auditor'],
 'prompts':['Technical Auditor','Film Critic'],'continuity':['Continuity Auditor'],'editing':['Film Critic','Audience Critic'],'sound':['Film Critic','Audience Critic']}
def roles(department):
 need(department in ROLES,'Unknown department');return ['Creative Agent']+ROLES[department]+['Chief Reviewer']
def rubric(department):
 data=json.loads((ROOT/'judgment-engine/rubrics.json').read_text(encoding='utf-8'))
 rr=[x for x in data['rubrics'] if x['department']==department];need(len(rr)==1,'Rubric missing/duplicate');return rr[0]
def review_packet(spec):
 dep=spec['department'];r=rubric(dep);target=spec['target'];path=Path(target['path']);need(path.is_file(),'Material not accessible')
 raw=path.read_bytes();need(len(raw)<=20_000_000,'Use scoped media inspection for large artifacts')
 try:text=raw.decode('utf-8')
 except UnicodeDecodeError:text=None
 examples=json.loads((ROOT/'judgment-engine/calibration-examples.json').read_text(encoding='utf-8'))['examples']
 from knowledge_select import canonical_genres, classify_intention, matching_genre_cases
 genre = str(spec['context'].get('genre','')).strip().casefold()
 genre_keys = canonical_genres([genre])
 mode = classify_intention(genre_keys,spec['context'].get('intention',''),spec['context'].get('creative_profile',''))
 action_first = mode=='action_led_war'
 relevant_cases = [case for case in matching_genre_cases(genre,action_first=action_first)
                   if dep in case['departments']]
 genre_labels = [e for e in examples if e['department']==dep and
                 (e.get('genre','').casefold()==genre or
                  (genre in {'drama','realist drama'} and e.get('genre')=='drama realista'))]
 if action_first:
  genre_labels=[]
 return {'kind':'REVIEW_PACKET_NOT_JUDGED','target':{'id':target['id'],'revision':target['revision'],'uri':str(path),'sha256':hashlib.sha256(raw).hexdigest()},'department':dep,'context':spec['context'],'roles':roles(dep),'rubric':r,'rubric_sha256':digest(r),'calibration':[] if spec.get('holdout') else genre_labels, 'genre_cases':[] if spec.get('holdout') else relevant_cases, 'calibration_origin':'Exemplos didáticos da biblioteca, filtrados por gênero e departamento. A avaliação depende da mídia e da decisão do diretor.','material_text':text,'media_status':'TEXT_ACCESSIBLE' if text is not None else 'REQUIRES_AUTHORIZED_MULTIMODAL_INSPECTION','observed_quality':None}
def validate_review(r):
 for k in ['id','project_id','episode_id','department','reviewer','creator_id','mode','target','context','technical','artistic','adversarial','limitations']:
  need(k in r,'Missing review field: '+k)
 need(r['department'] in ROLES,'Unknown rubric department')
 rr=rubric(r['department']);need(r.get('rubric_sha256')==digest(rr),'Review must bind the actual current rubric; re-packet if changed')
 need(all(nonempty(r[k]) for k in ['id','project_id','episode_id','reviewer','creator_id']),'Review identity missing')
 need(r['mode'] in {'independent_agent','separate_pass','human'},'Unknown review mode')
 if r['mode']=='independent_agent':need(r['reviewer']!=r['creator_id'],'Creator is not an independent reviewer')
 target=r['target'];need(nonempty(target.get('id')) and type(target.get('revision')) is int and target['revision']>=1 and re.fullmatch('[0-9a-f]{64}',target.get('sha256','')),'Target version/hash missing')
 ctx=r['context'];need(all(nonempty(ctx.get(k)) for k in ['intention','genre','format']),'Artistic context required');goal=ctx.get('target_level',3);need(type(goal) is int and 1<=goal<=5,'Invalid context target')
 tech=r['technical'];need(tech.get('status') in {'PASS','FAIL','UNKNOWN'},'Invalid technical status');checks=tech.get('checks',[]);need(isinstance(checks,list) and bool(checks),'Technical checks required')
 for c in checks:
  need(c.get('status') in {'PASS','FAIL','UNKNOWN','NOT_APPLICABLE'} and nonempty(c.get('criterion')) and nonempty(c.get('observation')),'Malformed technical check')
  if c['status'] in {'PASS','FAIL'}:need(nonempty(c.get('evidence_ref')),'Observed technical check needs evidence')
 if tech['status']=='PASS':need(all(c['status'] in {'PASS','NOT_APPLICABLE'} for c in checks) and any(c['status']=='PASS' for c in checks),'Technical pass has failed/unknown/no observed checks')
 if tech['status']=='FAIL':need(any(c['status']=='FAIL' for c in checks),'Technical failure lacks failing check')
 art=r['artistic'];need(art.get('status') in {'RECOMMEND_APPROVAL','CHANGES_REQUESTED','UNKNOWN'},'Invalid artistic status');level=art.get('level')
 if art['status']=='UNKNOWN':need(level is None,'Unknown art cannot have a level')
 else:
  need(type(level) is int and 1<=level<=5,'Artistic level must be 1..5')
  need(nonempty(art.get('rationale')),'Artistic rationale required')
  obs=art.get('observations',[]);need(bool(obs),'Artistic evidence absent')
  need({c.get('criterion') for c in obs}==set(rr['criteria']),'Address each actual rubric criterion; use UNKNOWN when essential evidence is absent')
  for c in obs:need(all(nonempty(c.get(k)) for k in ['criterion','observation','evidence_ref','interpretation']),'Artistic observation must link criterion/evidence/interpretation')
  need(isinstance(art.get('strengths'),list) and isinstance(art.get('problems'),list),'Strengths/problems lists required')
  if level>=4:need(nonempty(art.get('integration')),'Excellent/exceptional requires explanation of integrated choices, not technical compliance alone')
 adv=r['adversarial'];need(nonempty(adv.get('challenge')) and nonempty(adv.get('successful_choice')),'Adversarial review must test a choice and recognize observed strengths; may report no defects')
 need(isinstance(r['limitations'],list) and bool(r['limitations']),'Review limitations required')
 if tech['status']=='FAIL':recommendation='CHANGES_REQUESTED'
 elif tech['status']=='UNKNOWN' or art['status']=='UNKNOWN':recommendation='INCOMPLETE_EVIDENCE'
 elif art['status']=='CHANGES_REQUESTED' or level<goal:recommendation='CHANGES_REQUESTED'
 else:recommendation='READY_FOR_HUMAN_DECISION'
 return {'valid':True,'technical':tech['status'],'artistic_level':level,'recommendation':recommendation,'approved':False,'independence':'declared_mode_not_cryptographically_proven','review_sha256':digest(r)}
def blind_packets(variants,context):
 need(len(variants)==2,'Exactly two alternatives per pair')
 need(all(nonempty(x.get('material_id')) and nonempty(x.get('text')) for x in variants),'Material identity/text missing')
 need(variants[0]['material_id']!=variants[1]['material_id'],'Distinct materials required')
 session=str(uuid.uuid4());packets=[];mapping={}
 for i,order in enumerate([(0,1),(1,0)]):
  packet={'packet_id':session+'-'+str(i+1),'context':context,'alternatives':[{'label':label,'text':variants[j]['text']} for label,j in zip(['A','B'],order)],'allowed_choices':['A','B','TIE','BOTH_FAIL'],'warnings':['Inspect text for authorship clues; metadata removal does not guarantee blinding.']}
  packets.append(packet);mapping[packet['packet_id']]={label:variants[j]['material_id'] for label,j in zip(['A','B'],order)}
 return {'public_packets':packets,'private_mapping':mapping,'session_id':session,'source_hashes':{x['material_id']:digest(x['text']) for x in variants}}
def consolidate(session,reviews):
 need(bool(reviews),'No reviews');by={};allowed={'A','B','TIE','BOTH_FAIL'}
 for r in reviews:
  need(r.get('packet_id') in session['private_mapping'],'Wrong packet');need(r.get('choice') in allowed,'Invalid choice')
  need(nonempty(r.get('reviewer')) and nonempty(r.get('rationale')) and bool(r.get('evidence')),'Pairwise rationale/evidence/reviewer missing')
  key=(r['reviewer'],r['packet_id']);need(key not in by,'Duplicate reviewer/packet');by[key]=r
 judges={r['reviewer'] for r in reviews};votes={};disagreements=[]
 for judge in sorted(judges):
  rr=[r for r in reviews if r['reviewer']==judge];need({r['packet_id'] for r in rr}==set(session['private_mapping']),'Both orders required per reviewer')
  winners=[]
  for r in rr:winners.append(session['private_mapping'][r['packet_id']].get(r['choice'],r['choice']))
  if winners[0]==winners[1]:votes[judge]=winners[0]
  else:disagreements.append({'reviewer':judge,'outcomes':winners,'reason':'Order/context sensitivity possible; cannot infer cause from this pair alone'})
 order_changes = list(disagreements)
 reviewer_dissent = []
 if len(set(votes.values())) > 1:
  for judge,winner in votes.items():
   reviewer_dissent.append({'reviewer':judge, 'preferred':winner,
       'reasons':[{'rationale':r['rationale'],'evidence':r['evidence']} for r in reviews if r['reviewer']==judge]})
  disagreements.append({'kind':'between_reviewers','positions':reviewer_dissent})
 values=set(votes.values());stable=len(values)==1 and not disagreements
 return {'outcome':next(iter(values)) if stable else 'UNRESOLVED','per_reviewer':votes,'disagreements':disagreements,'order_changes':order_changes,'reviewer_dissent':reviewer_dissent,'human_decision_required':True,'approved':False,'position_bias_rate':None,'position_bias_limit':'Same-context repeats are descriptive, not isolated fresh-context position-bias measurement.'}
def diagnosis(d):
 for k in ['symptom','evidence','probable_cause','alternatives','missing_evidence','confidence','repair','risks','protected','verification']:need(k in d,'Missing diagnosis '+k)
 need(d['confidence'] in {'LOW','MEDIUM','HIGH'},'Confidence qualitative only')
 for k in ['symptom','probable_cause','repair']:need(nonempty(d[k]),'Diagnosis text missing: '+k)
 for k in ['evidence','alternatives','verification','risks','missing_evidence','protected']:
  need(isinstance(d[k],list) and all(nonempty(v) for v in d[k]),'Diagnosis list contains absent/malformed items: '+k)
 for k in ['evidence','alternatives','verification']:need(bool(d[k]),'Diagnosis requires observed evidence, differential and test: '+k)
 return {'valid':True,'causation_proven':False}
def revision_decision(state):
 n=state.get('round',0);limit=state.get('max_rounds',2);need(type(n) is int and type(limit) is int and 0<=n and 1<=limit<=5,'Invalid revision bounds')
 need(not set(state.get('changed_elements',[]))&set(state.get('protected_elements',[])),'Correction modifies protected element; create authorized successor revision')
 return {'next':'PRESENT_UNRESOLVED_TO_USER' if n>=limit else 'LOCALIZED_REVISION','auto_approve':False,'remaining':max(0,limit-n)}
def metrics(records):
 """Human agreement only on actual labeled records, plus explicit denominators."""
 eligible=[r for r in records if r.get('human_origin')=='REAL_USER' and nonempty(r.get('user_message_ref')) and nonempty(r.get('evidence_ref')) and r.get('agent_decision') in {'APPROVE','REJECT'} and r.get('human_decision') in {'APPROVE','REJECT'}]
 need(all(nonempty(r.get('id')) for r in eligible),'Real feedback requires stable IDs')
 need(len({r['id'] for r in eligible})==len(eligible),'Duplicate human feedback IDs; reconcile before metrics')
 n=len(eligible);false_a=sum(r['agent_decision']=='APPROVE' and r['human_decision']=='REJECT' for r in eligible);false_r=sum(r['agent_decision']=='REJECT' and r['human_decision']=='APPROVE' for r in eligible)
 negatives=sum(r['human_decision']=='REJECT' for r in eligible);positives=n-negatives
 return {'real_human_n':n,'human_agreement':sum(r['agent_decision']==r['human_decision'] for r in eligible)/n if n else None,'false_approval_rate':false_a/negatives if negatives else None,'false_rejection_rate':false_r/positives if positives else None,'denominators':{'human_reject':negatives,'human_approve':positives},'not_measured':['audience retention','viral performance','population-level artistic quality','fresh-context position bias']}
def native_metrics(snapshot, confirmed_messages=()):
 """Only compare human messages verified by the calling agent with an evaluation of that revision."""
 from shared_state import validate
 validate(snapshot)
 need(isinstance(confirmed_messages,(list,tuple,set)) and all(nonempty(v) for v in confirmed_messages),
      'Supply actual message references resolved by the host')
 confirmed = set(confirmed_messages)
 decisions = {'READY_FOR_HUMAN_DECISION':'APPROVE','CHANGES_REQUESTED':'REJECT',
              'RECOMMEND_APPROVAL':'APPROVE','APPROVE':'APPROVE','REJECT':'REJECT'}
 evaluations = {r['id']:r for r in snapshot['tables']['Evaluation Results']}
 excluded, normalized = [], []
 for feedback in snapshot['tables']['Human Feedback']:
  reason = None
  evaluation = evaluations.get(feedback['evaluation_id'])
  if feedback['is_test']: reason = 'test_record'
  elif feedback['status'] in {'REJECTED','ARCHIVED'}: reason = 'inactive_feedback'
  elif feedback['user_message_ref'] not in confirmed: reason = 'unconfirmed_message_origin'
  elif feedback['human_decision'] not in {'APPROVE','REJECT'}: reason = 'relative_or_nonbinary_decision'
  elif not evaluation: reason = 'linked_evaluation_missing'
  elif evaluation['is_test'] or evaluation['status'] in {'REJECTED','ARCHIVED'}: reason = 'inactive_evaluation'
  elif any(feedback[k] != evaluation[k] for k in ('project_id','episode_id','target_table','target_id','target_revision')):
   reason = 'evaluation_scope_or_version_mismatch'
  elif evaluation['decision'] not in decisions: reason = 'evaluation_not_binary'
  if reason:
   excluded.append({'id':feedback['id'],'reason':reason})
  else:
   normalized.append({**feedback, 'human_origin':'REAL_USER','evidence_ref':feedback['evidence'],
                      'agent_decision':decisions[evaluation['decision']]})
 return {**metrics(normalized),'excluded':excluded,'included_ids':[r['id'] for r in normalized]}

def take_preferences(snapshot, project_id, episode_id, target_ids=(), include_test=False, confirmed_messages=()):
 """Retrieve versioned preferences within the scope the director actually granted."""
 pairs = {r['id']:r for r in snapshot['tables']['Pairwise Comparisons']}
 targets = {r['id']:r for r in snapshot['tables']['Artifact Registry'] if r['id'] in target_ids
            and r['project_id']==project_id and r['episode_id']==episode_id}
 found = []
 for row in snapshot['tables']['Human Feedback']:
  if row['target_table']!='Pairwise Comparisons' or row['project_id']!=project_id:continue
  if (row['is_test'] and not include_test) or row['status'] in {'ARCHIVED','REJECTED'}:continue
  pair=pairs.get(row['target_id'])
  if not pair or pair['status'] in {'ARCHIVED','REJECTED'}:continue
  if (pair['project_id'],pair['episode_id'],pair['revision'],pair['is_test'],pair['human_decision_ref'])!=(
      row['project_id'],row['episode_id'],row['target_revision'],row['is_test'],row['user_message_ref']):continue
  try: evidence=json.loads(row['evidence']);pair_evidence=json.loads(pair['order_results_json'])
  except (TypeError,ValueError):continue
  if not isinstance(evidence,dict) or evidence.get('kind')!='TAKE_PREFERENCE' or evidence!=pair_evidence:continue
  takes=evidence.get('takes')
  if not isinstance(takes,dict) or set(takes)!={'A','B'} or not all(isinstance(t,dict) and t.get('id') for t in takes.values()):continue
  scope=row['preference_scope']
  if scope not in {'deliverable','scene','episode','project'} or scope!=evidence.get('preference_scope'):continue
  if scope!='project' and row['episode_id']!=episode_id:continue
  if scope=='scene':
   shot=evidence.get('shot')
   if not isinstance(shot,dict) or not shot.get('scene_beat'):continue
   if not any(s['id'] in target_ids and s['project_id']==project_id and s['episode_id']==episode_id
              and s['scene_beat']==shot['scene_beat'] for s in snapshot['tables']['Shot List']):continue
  if scope=='deliverable' and not any(t['id'] in targets and
      all(targets[t['id']].get(k)==t.get(k) for k in ('revision','version','sha256')) for t in takes.values()):continue
  origin='TEST' if row['is_test'] else ('HOST_VERIFIED' if row['user_message_ref'] in confirmed_messages else 'SHEET_MESSAGE_REFERENCE')
  found.append({'id':row['id'],'origin_message':row['user_message_ref'],'scope':scope,
                'origin_status':origin,
                'project_id':project_id,'episode_id':row['episode_id'],'pair_id':pair['session_ref'],
                'target_revision':row['target_revision'],'evidence':evidence,'is_test':row['is_test']})
 return sorted(found,key=lambda r:r['id'])

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('command',choices=['validate','pair','consolidate','diagnose','revise','metrics','roles','packet']);p.add_argument('input');p.add_argument('--reviews',type=Path);a=p.parse_args()
 if a.command=='roles':result=roles(a.input)
 else:
  v=json.loads(Path(a.input).read_text(encoding='utf-8'))
  result={'validate':lambda:validate_review(v),'pair':lambda:blind_packets(v['variants'],v['context']),'consolidate':lambda:consolidate(v,json.loads(a.reviews.read_text(encoding='utf-8'))),'diagnose':lambda:diagnosis(v),'revise':lambda:revision_decision(v),'metrics':lambda:metrics(v),'packet':lambda:review_packet(v)}[a.command]()
 print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
