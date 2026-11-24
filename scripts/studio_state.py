#!/usr/bin/env python3
"""Offline state manager. No network, dependencies or media generation."""
import argparse, json, pathlib, datetime, copy
GATES=json.loads((pathlib.Path(__file__).resolve().parents[1]/'orchestration/gates.json').read_text())
BY={g['id']:g for g in GATES}; DONE={'APPROVED','LOCKED','SKIPPED'}
def new(project,episode):
 return {'version':3,'project':project,'episode':episode,'credits_allowed':0,'mode':'guided','gates':{g['id']:{'status':'PENDING','checks':[False]*len(g['checks']),'evidence':'','revision':1} for g in GATES},'history':[]}
def validate(s):
 assert s['version']==3 and s['credits_allowed']==0,'Invalid scope/version'
 assert s['mode'] in ('guided','manual','hybrid'),'Invalid mode'
 assert set(s['gates'])==set(BY),'Missing/unknown gate'
 for id,st in s['gates'].items():
  g=BY[id]; status=st['status']; assert status in DONE|{'PENDING','IN_PROGRESS','REVIEW_REQUIRED','CHANGES_REQUESTED'},f'{id}: invalid status'
  assert len(st['checks'])==len(g['checks']) and all(type(x) is bool for x in st['checks']),f'{id}: invalid checklist'
  assert isinstance(st['revision'],int) and st['revision']>=1,f'{id}: invalid revision'
  if status in DONE:
   assert all(s['gates'][d]['status'] in DONE for d in g['depends']),f'{id}: dependency not approved'
   assert st['evidence'].strip(),f'{id}: missing evidence'
   if status=='SKIPPED': assert g['skippable'],f'{id}: mandatory gate'
   else: assert all(st['checks']),f'{id}: checklist incomplete'
 return True
def change(s,id,action,evidence='',checks=None):
 validate(s); s=copy.deepcopy(s); st=s['gates'][id]; g=BY[id]; previous=copy.deepcopy(st)
 if action=='review':
  assert st['status'] not in DONE,'Use revise first'; st['status']='REVIEW_REQUIRED'; st['checks']=checks if checks is not None else st['checks'];st['evidence']=evidence
 elif action=='approve':
  assert st['status']=='REVIEW_REQUIRED','Review first';st['status']='APPROVED'
 elif action=='lock':
  assert st['status']=='APPROVED','Approve first';st['status']='LOCKED'
 elif action=='skip':
  assert st['status'] not in DONE,'Revise first';st['status']='SKIPPED';st['evidence']=evidence
 elif action=='revise':
  assert evidence.strip(),'Revision requires reason'; affected={id}
  for x in GATES:
   if any(d in affected for d in x['depends']): affected.add(x['id'])
  for x in affected:
   t=s['gates'][x];s['history'].append({'gate':x,'action':'invalidate','previous':copy.deepcopy(t),'reason':evidence});t.update(status='CHANGES_REQUESTED',checks=[False]*len(BY[x]['checks']),evidence='',revision=t['revision']+1)
 else: raise ValueError(action)
 s['history'].append({'gate':id,'action':action,'previous':previous,'reason':evidence,'at':datetime.datetime.now(datetime.timezone.utc).isoformat()});validate(s);return s
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('file',type=pathlib.Path);p.add_argument('action',choices=['init','validate','status','review','approve','lock','skip','revise']);p.add_argument('--project',default='Projeto');p.add_argument('--episode',default='1');p.add_argument('--gate',choices=BY);p.add_argument('--evidence',default='');p.add_argument('--checked',action='store_true',help='Explicitly attest all checks reviewed, with evidence');a=p.parse_args()
 if a.action=='init':
  if a.file.exists(): p.error('File already exists')
  s=new(a.project,a.episode)
 else: s=json.loads(a.file.read_text(encoding='utf8'))
 validate(s)
 if a.action=='validate': print('OK');return
 if a.action=='status':
  for g in GATES: print(g['id'],g['name'],s['gates'][g['id']]['status'])
  return
 if a.action!='init':
  if not a.gate: p.error('--gate required')
  s=change(s,a.gate,a.action,a.evidence,[True]*len(BY[a.gate]['checks']) if a.checked else None)
 a.file.parent.mkdir(parents=True,exist_ok=True);tmp=a.file.with_suffix(a.file.suffix+'.tmp');tmp.write_text(json.dumps(s,ensure_ascii=False,indent=2),encoding='utf8');tmp.replace(a.file);print('OK')
if __name__=='__main__': main()
