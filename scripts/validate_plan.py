#!/usr/bin/env python3
"""Structural/timing checks only; not a literary or historical validation."""
import argparse, json, math, sys
from pathlib import Path

def number(x):
    return type(x) in (int, float) and math.isfinite(x)
def valid_text(x):
    return isinstance(x, str) and bool(x.strip())
def validate(p, allow_empty=False):
    errors=[]
    if not isinstance(p,dict): return ['root must be object']
    if type(p.get('episode')) is not int or p['episode']<1: errors.append('invalid episode')
    for k in ('version','language'):
        if not valid_text(p.get(k)): errors.append('missing '+k)
    if p.get('status') not in ('draft','review','approved','blocked'): errors.append('invalid status')
    target=p.get('target_seconds'); wps=p.get('speech_wps')
    if not number(target) or target<=0: errors.append('invalid target_seconds'); target=0
    if not number(wps) or wps<=0: errors.append('invalid speech_wps'); wps=1
    sources=p.get('sources'); beats=p.get('beats')
    if not isinstance(sources,list): errors.append('sources must be array'); sources=[]
    if not isinstance(beats,list): return errors+['beats must be array']
    ids=set(); seen=set(); cursor=0.0
    for s in sources:
        if not isinstance(s,dict) or not valid_text(s.get('id')) or not valid_text(s.get('locator')) or s.get('kind') not in ('fact','inference','fiction','unknown'):
            errors.append('invalid source record'); continue
        if s['id'] in ids: errors.append('duplicate source '+s['id'])
        ids.add(s['id'])
    if not beats and not allow_empty: errors.append('no beats')
    for i,b in enumerate(beats):
        prefix=f'beat {i+1}: '
        if not isinstance(b,dict): errors.append(prefix+'not an object'); continue
        for k in ('id','action','change','cause'):
            if not valid_text(b.get(k)): errors.append(prefix+'missing '+k)
        bid=b.get('id')
        if valid_text(bid):
            if bid in seen: errors.append(prefix+'duplicate id')
            seen.add(bid)
        refs=b.get('source_ids')
        if not isinstance(refs,list) or any(not isinstance(r,str) or r not in ids for r in refs): errors.append(prefix+'unknown/invalid source_ids')
        fields=('start','end','action_seconds','pause_seconds','overlap_seconds','spoken_words')
        if any(not number(b.get(k)) or b[k]<0 for k in fields) or type(b.get('spoken_words')) is not int:
            errors.append(prefix+'invalid time or word count'); continue
        a,z=b['start'],b['end']; speech=b['spoken_words']/wps; act=b['action_seconds']; overlap=b['overlap_seconds']
        if abs(a-cursor)>0.01: errors.append(prefix+'timeline gap or overlap')
        if z<=a: errors.append(prefix+'end must exceed start')
        if overlap>min(speech,act)+0.01: errors.append(prefix+'impossible overlap')
        if z-a+0.01<speech+act+b['pause_seconds']-overlap: errors.append(prefix+'estimated minimum exceeds beat duration')
        cursor=z
    if cursor>target+0.01: errors.append('episode exceeds target duration')
    return errors

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('file'); ap.add_argument('--allow-empty',action='store_true'); a=ap.parse_args()
    try: errors=validate(json.loads(Path(a.file).read_text(encoding='utf-8')),a.allow_empty)
    except (OSError,ValueError) as e: errors=[str(e)]
    print(json.dumps({'valid':not errors,'errors':errors},ensure_ascii=False,indent=2)); return int(bool(errors))
if __name__=='__main__': sys.exit(main())
