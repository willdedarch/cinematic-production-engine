"""Decision inbox and alternate cuts. Only authenticated connector readbacks can close a receipt."""
import json
import re
import unicodedata
from collections import Counter
from datetime import datetime,timezone
from pathlib import Path
from journal_codec import decode_event
from history_integrity import check_event_series,event_identity
from shared_state import canonical,fingerprint,index,prepare,require,timestamp,validate
from shot_workflow import card,ref,link_change,digest_file,ROOT,impact
from series_bible import source_link

PROPOSAL='CPE_DESK_PROPOSAL_V1'
RESULT='CPE_DESK_RESULT_V1'
HEADERS=['Pedido','Série','Episódio','Plano ou material','Proposta','Colaborador']
def now():return datetime.now(timezone.utc).isoformat()
def clean(value):
    folded=unicodedata.normalize('NFKD',str(value).casefold())
    return ' '.join(''.join(c for c in folded if not unicodedata.combining(c)).split())
def read_body(row):return json.loads(row['choice'])
def attach_intake(snapshot, values):
    require(values and values[0][:6]==HEADERS,'Fila de direção: cabeçalhos divergentes')
    rows=[];issues=[]
    tickets=Counter(raw[0] for raw in values[1:] if raw and isinstance(raw[0],str) and raw[0])
    for n,raw in enumerate(values[1:],2):
        v=(list(raw)+['']*6)[:6]
        if not str(v[4] or '').strip():continue
        entry=dict(zip(HEADERS,(str(x).strip() if x is not None else '' for x in v)),row=n,sha256=fingerprint(v),source_values=v)
        if not isinstance(v[0],str) or not re.fullmatch(r'PED-[A-Za-z0-9-]+',v[0]) or tickets[v[0]]!=1:
            issues.append(entry)
        else:
            rows.append(entry)
    return {**snapshot,'desk_intake':rows,'desk_intake_issues':issues}

def confirmed_changes(events,read_at):
    require({e['event'] for e in events}=={'PREPARED','CONFIRMED'},'Histórico incompleto')
    prepared=decode_event([e for e in events if e['event']=='PREPARED'])
    confirmed=decode_event([e for e in events if e['event']=='CONFIRMED'])
    require(prepared==confirmed and all(event_identity(e)==event_identity(events[0]) for e in events),'Journal mismatch')
    check_event_series(confirmed,events,read_at)
    return confirmed

def receipt(snapshot,row,history=None,table='Decisions'):
    if history is None:
        history={}
        for event in snapshot['tables']['Revision History']:history.setdefault(event['op_id'],[]).append(event)
    events=history.get(row['last_op_id'],[])
    try:
        after=confirmed_changes(events,snapshot['read_at'])
        require(all(e['actor']==row['updated_by'] and e['authorization_ref']==row['user_message_ref'] for e in events),'Incorrect authorization')
        require(any(c['table']==table and c['id']==row['id'] and c['after']==row for c in after),'Different record')
        current=index(snapshot)
        for change in after:
            latest=current[change['table']].get(change['id'])
            expected=change['after']
            while latest and latest['revision']>expected['revision']:
                later=confirmed_changes(history.get(latest['last_op_id'],[]),snapshot['read_at'])
                prior=next((c['before'] for c in later if c['table']==change['table'] and c['id']==change['id'] and c['after']==latest),None)
                require(prior and prior['revision']==latest['revision']-1,'Histórico da revisão sucessora incompleto')
                latest=prior
            require(latest==expected,'Parte da operação não consta da leitura')
    except (ValueError,KeyError,TypeError):return ''
    return row['last_op_id']

def candidates(snapshot,pid,eid,q):
    projects=[p['id'] for p in snapshot['tables']['Projects'] if clean(q['Série']) in {clean(p['id']),clean(p['name'])}]
    if projects!=[pid]:return False
    label=clean(q['Episódio'])
    number=re.fullmatch(r'(?:ep(?:isodio)?\s*)?0*(\d+)',label)
    episodes=[ep['id'] for ep in snapshot['tables']['Episodes'] if ep['project_id']==pid
              and (label in {clean(ep['id']),clean(ep['title'])} or number and int(number[1])==ep['episode_number'])]
    return episodes==[eid]
def shot_for(snapshot,pid,eid,lookup):
    if not lookup:return None
    hits=[]
    for r in snapshot['tables']['Shot List']:
        if (r['project_id'],r['episode_id'])!=(pid,eid) or r['status']=='ARCHIVED':continue
        names={clean(r['id']),clean(r['scene_beat']),clean(r['purpose']),f"sh{int(r['order']):02d}"}
        if clean(lookup) in names:hits.append(r)
    require(len(hits)==1,'Esclareça o plano: faltante ou ambíguo')
    return hits[0]

def material_for(snapshot,pid,eid,name):
    if not name:return None
    hits=[]
    for table in ('Shot List','Screenplays','Characters','Props','Locations','Cinematography','Artifact Registry'):
        for r in snapshot['tables'][table]:
            if r['project_id']!=pid or r['episode_id']!=eid or r.get('status')=='ARCHIVED':continue
            labels=[r.get(k,'') for k in ('id','name','title','purpose','scene_beat','asset_name','character_name','location_name','prop_name')]
            if table=='Shot List':labels.append(f"sh{int(r['order']):02d}")
            if table=='Artifact Registry':labels.append(Path(r['uri']).name)
            if any(clean(name)==clean(t) for t in labels if t):hits.append(ref(table,r))
    require(len(hits)==1,'O nome corresponde a nenhum ou vários materiais. Esclareça a entrega.')
    return hits[0]

def context_pin(snapshot,pid,eid,shot_id,media=None,target=None):
    ix=index(snapshot);e=ix['Episodes'].get(eid);require(e and e['project_id']==pid,'Episódio fora da série')
    pins=[ref('Projects',ix['Projects'][pid]),ref('Episodes',e)]
    if target:
        current=ix.get(target['table'],{}).get(target['id'])
        require(current and current['project_id']==pid and current['episode_id']==eid and target==ref(target['table'],current),'A entrega escolhida mudou')
        pins.append(target)
    if shot_id:
        shot=ix['Shot List'].get(shot_id)
        require(shot and shot['episode_id']==eid,'Plano fora do episódio')
        shot_card=card(snapshot,shot_id);pins.append(shot_card['shot'])
        prior=sorted((x for x in snapshot['tables']['Shot List'] if x['episode_id']==eid and x['scene_beat']==shot['scene_beat'] and x['order']<shot['order'] and x['status']!='ARCHIVED'),key=lambda x:(x['order'],x['id']))
        if prior:pins.append(ref('Shot List',prior[-1]))
        for link in shot_card['links']:
            if media and link['relation']=='take' and link['to']['id']!=media['id']:continue
            for side in ('from','to'):
                endpoint=link[side]
                pins.append(ref(endpoint['table'],ix[endpoint['table']][endpoint['id']]))
            if link.get('decision'):pins.append(ref('Decisions',ix['Decisions'][link['decision']['id']]))
    if media:
        current=ix['Artifact Registry'].get(media['id'])
        require(current and current['episode_id']==eid and ref('Artifact Registry',current)==media,'Mídia mudou de versão')
        pins.append(media)
    unique={(p['table'],p['id']):p for p in pins}
    return [unique[k] for k in sorted(unique)]

def projection(s,pid,eid):
    sources={r['id']:r for r in s['tables']['Decisions'] if r['project_id']==pid and r['episode_id']==eid and r['topic']==PROPOSAL}
    results={read_body(r)['proposal_id']:r for r in s['tables']['Decisions'] if r['project_id']==pid and r['episode_id']==eid and r['topic']==RESULT}
    raw={r['Pedido']:r for r in s.get('desk_intake',[]) if candidates(s,pid,eid,r)}
    history={}
    for e in s['tables']['Revision History']:history.setdefault(e['op_id'],[]).append(e)
    queue=[];alternatives=[]
    for key,p in sources.items():
        data=read_body(p);r=results.get(key);ack=receipt(s,r,history) if r else ''
        status='PROPOSTA' if not r else ('EM REVISÃO' if not ack else 'CONFIRMADA' if read_body(r)['choice']=='accept' else 'RECUSADA')
        ticket=data.get('ticket','');entry=raw.get(ticket)
        if entry and entry['sha256']==data.get('input_sha256'):raw.pop(ticket)
        elif entry and not r:status='CONFLITO'
        item={'id':key,'title':data['title'],'summary':data['request'],'request':data['request'],'shot_id':data['shot_id'],'actor':data['author'],'base':data['pins'],'source':source_link(s,p),'status':status,'receipt':ack,'ticket':ticket,'input_sha256':data.get('input_sha256'),'reason':read_body(r)['reason'] if r else '', 'alternative_id':key if data.get('media') else '', 'media':data.get('media')}
        queue.append(item)
        if item['alternative_id']:alternatives.append({**item,'status':{'CONFIRMADA':'ESCOLHIDA'}.get(status,status)})
    for ticket,entry in raw.items():
        try:shot=shot_for(s,pid,eid,entry['Plano ou material'])
        except ValueError:shot=None
        queue.append({'id':ticket,'ticket':ticket,'title':entry['Plano ou material'] or 'Proposta da equipe','summary':entry['Proposta'],'request':entry['Proposta'],'actor':entry['Colaborador'],'shot_id':shot['id'] if shot else '','status':'PROPOSTA','receipt':'','source':{'table':'Fila de direção','row':entry['row']},'input_sha256':entry['sha256']})
    for entry in s.get('desk_intake_issues',[]):
        if candidates(s,pid,eid,entry):
            queue.append({'id':'FILA-LINHA-'+str(entry['row']),'title':entry['Plano ou material'] or 'Pedido da equipe','summary':'Confira o protocolo desta linha na planilha antes de decidir.','request':entry['Proposta'],'status':'CONFLITO','receipt':'','shot_id':'','actor':entry['Colaborador'],'source':{'table':'Fila de direção','row':entry['row']}})
    return {'queue':queue,'alternatives':alternatives}

def ledger(snapshot):
    from desk_guard import check_ledger
    check_ledger(snapshot,PROPOSAL,RESULT)

def as_change(key,ep,topic,body,a):
    return {'table':'Decisions','id':key,'expected_revision':None,'values':{'project_id':ep['project_id'],'episode_id':ep['id'],'gate_id':'G10','is_test':ep['is_test'],'topic':topic,'choice':canonical(body),'rationale':body.get('reason') or body['request'],'user_message_ref':a['user_message_ref'],'status':'RECORDED'}}

def dispatch(action,s,spec,workspace=None):
    from desk_guard import pins_with_origin,verified_media
    validate(s)
    pid,eid=spec['project_id'],spec['episode_id'];ix=index(s);ep=ix['Episodes'].get(eid)
    require(ep and ep['project_id']==pid and (not ep['is_test'] or spec.get('include_test') is True),'Escopo do episódio inválido')
    if action=='desk-inbox':return projection(s,pid,eid)
    if action=='desk-receipts':
        output=[]
        for item in projection(s,pid,eid)['queue']:
            ticket=item.get('ticket');ack=item.get('receipt')
            if not (ticket and ack):continue
            entry=next((r for r in s.get('desk_intake',[]) if r['Pedido']==ticket and r['sha256']==item['input_sha256']),None)
            if entry:
                fields=entry.get('source_values',[entry[k] for k in HEADERS])
                output.append({'row':entry['row'],'expected_A_to_F':fields,'values_I_to_P':[ack,*fields[1:],item['status'],item['reason']]})
        return {'kind':'QUEUE_RECEIPTS_FOR_CONNECTOR','sheet_name':'Fila de direção','patches':output,'remote_write':False}
    if action=='desk-context':return {'pins':context_pin(s,pid,eid,spec.get('shot_id'),spec.get('media')),'read_at':s['read_at']}
    auth=spec.get('authorization',{})
    require(auth.get('authorized') is True and auth.get('actor') and auth.get('user_message_ref'),'Vincule à mensagem recebida')
    at=now();ch=[]
    if action in {'desk-propose','desk-edit'}:
        ticket=spec.get('ticket','');entry=None
        if ticket:
            matches=[r for r in s.get('desk_intake',[]) if r['Pedido']==ticket and candidates(s,pid,eid,r)]
            require(len(matches)==1 and spec.get('input_sha256')==matches[0]['sha256'],'Proposta da equipe mudou ou requer nova leitura')
            entry=matches[0]
        request=entry['Proposta'] if entry else spec['request']
        author=(entry['Colaborador'] or 'Colaborador') if entry else auth['actor']
        target=material_for(s,pid,eid,entry['Plano ou material'] if entry else spec.get('shot_id') or spec.get('material',''))
        shot=ix['Shot List'][target['id']] if target and target['table']=='Shot List' else None
        shot_id=shot['id'] if shot else ''
        key='MESA-P-'+fingerprint([s['spreadsheet_id'],eid, ticket or auth['user_message_ref'],entry['sha256'] if entry else spec.get('request_key',request)])[:24]
        op='MESA-OP-'+key
        existing=ix['Decisions'].get(key)
        if existing:
            data=read_body(existing)
            require(data['request']==request and data['shot_id']==shot_id,'Operação já utilizada para outra proposta')
            requested_edit={'source':spec.get('source'),'offset_ms':spec.get('offset_ms')} if action=='desk-edit' else None
            target_matches=(data.get('target')==target or ('target' not in data and target and target in data['pins']
                            and (target['table']!='Shot List' or data['shot_id']==target['id'])))
            require(data.get('edit')==requested_edit and (requested_edit or data.get('media')==spec.get('media'))
                    and target_matches and (not spec.get('title') or spec['title']==data['title']),
                    'Esta proposta já usa outra versão, variação ou material.')
            return {'kind':'EXISTING_PROPOSAL','id':key,'receipt':receipt(s,existing),'replay':False}
        if any(h['op_id']==op for h in s['tables']['Revision History']):return {'kind':'RECONCILE_PENDING','op_id':op,'replay':False}
        a={**auth,'op_id':op,'at':at};media=spec.get('media')
        if action=='desk-edit':
            from desk_variant import materialize
            require(shot,'Selecione o plano da variação')
            source=spec['source']; original=ix['Artifact Registry'].get(source['id'])
            require(original and original['episode_id']==eid and ref('Artifact Registry',original)==source and original['rights'].strip(),'Confira a versão e os direitos da origem')
            original,path=verified_media(s,source,pid,eid)
            require(any(link['relation']=='take' and link['from']['id']==shot_id and link['to']==source and not link['stale'] for link in card(s,shot_id)['links']),'Origem não pertence ao plano')
            provenance={'source':source,'offset_ms':spec['offset_ms']}
            file=materialize(workspace,key,path,provenance)
            asset_id='ART-'+key
            ch.append({'table':'Artifact Registry','id':asset_id,'expected_revision':None,'values':{'project_id':pid,'episode_id':eid,'is_test':ep['is_test'],'gate_id':'G12','kind':'NARRATIVE_PREVIS','department':'editing','version':1,'uri':str(file.resolve()),'sha256':digest_file(file),'origin':'Variação local a partir de '+original['id']+' · áudio '+str(spec['offset_ms'])+' ms','rights':original['rights'],'status':'REVIEW_REQUIRED'}})
            candidate=prepare(s,{**a,'changes':ch})['candidate']
            media=ref('Artifact Registry',index(candidate)['Artifact Registry'][asset_id])
            ch.append(link_change(candidate,{'relation':'take','decision_id':'LINK-'+key,'reason':request,'authorization':a},ref('Shot List',shot),media))
            base=prepare(s,{**a,'changes':ch})['candidate']
        else:base=s
        if media:
            require(shot and any(l['relation']=='take' and l['to']==media and l['from']['id']==shot_id and not l['stale'] for l in card(base,shot_id)['links']),'Escolha uma versão já vinculada ao plano')
        pins=context_pin(base,pid,eid,shot_id,media,target)
        body={'title':spec.get('title') or (entry['Plano ou material'] if entry else '') or request[:72],'request':request,'author':author,'shot_id':shot_id,'pins':pins,'media':media,'ticket':ticket,'input_sha256':entry['sha256'] if entry else ''}
        body['target']=target
        if action=='desk-edit':
            body['edit']=provenance
            body['pins']=pins_with_origin(pins,provenance,base)
        ch.append(as_change(key,ep,PROPOSAL,body,a))
    elif action=='desk-resolve':
        p=ix['Decisions'].get(spec['proposal_id']);require(p and p['project_id']==pid and p['episode_id']==eid and p['topic']==PROPOSAL,'Proposta fora do episódio')
        data=read_body(p); choice=spec['choice'];reason=spec['reason']
        require(choice in {'accept','reject'} and reason.strip(),'Escolha e motivo necessários')
        require(spec.get('proposal_sha256')==fingerprint(p),'Proposta alterada: apresente a versão atual')
        key='MESA-R-'+fingerprint(p['id'])[:24];op='MESA-OP-'+key;a={**auth,'op_id':op,'at':at}
        existing=ix['Decisions'].get(key)
        if existing:
            prev=read_body(existing);require(prev['choice']==choice and prev['reason']==reason,'Esta proposta já recebeu outra decisão')
            return {'kind':'EXISTING_DECISION','id':key,'receipt':receipt(s,existing),'replay':False}
        if any(h['op_id']==op for h in s['tables']['Revision History']):return {'kind':'RECONCILE_PENDING','op_id':op,'replay':False}
        if data['ticket']:
            require(any(x['Pedido']==data['ticket'] and x['sha256']==data['input_sha256'] for x in s.get('desk_intake',[])),'Pedido da fila alterado. Reapresente-o.')
        if choice=='accept':
            checked=context_pin(s,pid,eid,data['shot_id'],data['media'],data.get('target'))
            require(pins_with_origin(checked,data.get('edit'),s)==data['pins'],'Conflito: o plano, o take ou uma dependência mudou')
            if data['media']:
                verified_media(s,data['media'],pid,eid)
                shot=ix['Shot List'][data['shot_id']]
                ch.append(link_change(s,{'relation':'selected_take','decision_id':'LINK-'+key,'reason':reason,'authorization':a},ref('Shot List',shot),data['media']))
        body={'proposal_id':p['id'],'proposal_sha256':fingerprint(p),'choice':choice,'reason':reason}
        ch.append(as_change(key,ep,RESULT,body,a))
    else:raise ValueError('Comando de mesa desconhecido')
    plan=prepare(s,{**a,'changes':ch})
    plan['desk_item_id']=key
    return plan

