#!/usr/bin/env python3
"""Return and verify the reading route; does not itself make artistic decisions."""
import argparse,json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
ROUTER=json.loads((ROOT/'orchestration/knowledge-router.json').read_text(encoding='utf-8'))
def route(command,conditions=()):
 key=ROUTER['commands'].get(command.upper(),command.upper())
 if key not in ROUTER['gates']:raise ValueError('Resolve current eligible gate from fresh state first')
 r=ROUTER['gates'][key];paths=list(ROUTER['always'])+r['read']+[r['example']]
 for c in conditions:paths+=ROUTER['conditions'].get(c,[])
 result=[]
 for name in dict.fromkeys(paths):
  file=(ROOT/name).resolve()
  if not file.is_relative_to(ROOT) or not file.is_file():raise ValueError('Missing/outside route: '+name)
  result.append({'file':name,'sha256':hashlib.sha256(file.read_bytes()).hexdigest(),'text':file.read_text(encoding='utf-8')})
 return {'gate':key,'panel':r['panel'],'loaded':result}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('command');p.add_argument('--condition',action='append',default=[]);a=p.parse_args();print(json.dumps(route(a.command,a.condition),ensure_ascii=False,indent=2))
