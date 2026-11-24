"""Integrity of recorded desk decisions and the exact material authorized in a new proposal."""
import json
from pathlib import Path
import re
import unicodedata
from shared_state import fingerprint, index, require
from shot_workflow import TOPIC as LINK, ref, ROOT, digest_file

def verified_media(snapshot, pin, project, episode):
    current=index(snapshot)['Artifact Registry'].get(pin.get('id'))
    require(current and current['project_id']==project and current['episode_id']==episode
            and pin==ref('Artifact Registry',current),'A versão do material mudou.')
    require(current['kind'] not in {'REFERENCE','PRODUCTION_EXPORT'} and current['status'] not in {'ARCHIVED','REJECTED','CHANGES_REQUESTED'},
            'A alternativa exige um take disponível para revisão.')
    rights=''.join(c for c in unicodedata.normalize('NFKD',current['rights'].casefold().strip()) if not unicodedata.combining(c))
    require(rights and current['origin'].strip() and rights not in {'nao','no','n/a','?','false'} and not any(s in rights for s in
            ('nao autoriz','sem autoriz','nao confirm','pendente','desconhecid','unknown','not authorized','not permitted',
             'not cleared','pending','proibid','denied','sem direitos','sem licenc','aguarda')),
            'Os direitos e a origem do take precisam estar confirmados.')
    uri=current['uri'].strip();normal=uri.replace(chr(92),'/')
    require(normal and not normal.startswith('//') and '://' not in normal and not normal.startswith('file:'),
            'A edição da mesa precisa de mídia local autorizada.')
    path=Path(uri);base=ROOT.resolve()
    if not path.is_absolute():
        path=(base/path).resolve()
        require(path.is_relative_to(base),'Referência relativa fora da instalação.')
    require(path.is_file() and digest_file(path)==current['sha256'],'O arquivo da alternativa mudou ou está indisponível.')
    return current,path

def pins_with_origin(ctx, edit, snapshot):
    if not edit:return ctx
    origin=edit['source']
    current=index(snapshot)['Artifact Registry'].get(origin['id'])
    require(current and origin==ref('Artifact Registry',current),'A origem da alternativa mudou.')
    unique={(p['table'],p['id']):p for p in [*ctx,origin]}
    return [unique[k] for k in sorted(unique)]

def check_ledger(snapshot, proposal, result):
    ix=index(snapshot)
    rows=snapshot['tables']['Decisions']
    selected={}
    results=set()
    for row in rows:
        if row['topic']==LINK:
            link=json.loads(row['choice'])
            if link['relation']=='selected_take':
                selected.setdefault((row['last_op_id'],row['user_message_ref'],row['updated_by']),[]).append(link)
    for row in rows:
        if row['topic'] not in {proposal,result}:continue
        data=json.loads(row['choice'])
        pid,eid=row['project_id'],row['episode_id']
        require(isinstance(data,dict) and row['status']=='RECORDED' and row['user_message_ref'].strip(),'Decisão de mesa sem origem.')
        if row['topic']==proposal:
            require(all(isinstance(data.get(k),str) and data[k].strip() for k in ('title','request','author')),
                    'Proposta incompleta.')
            require(isinstance(data.get('shot_id'),str) and isinstance(data.get('pins'),list),'Vínculos ausentes.')
            refs={}
            for pin in data['pins']:
                require(isinstance(pin,dict) and set(pin)=={'table','id','revision','sha256'}
                        and isinstance(pin['table'],str) and isinstance(pin['id'],str),'Vínculo inválido.')
                target=ix.get(pin['table'],{}).get(pin['id'])
                require(target and target['project_id']==pid and target['is_test']==row['is_test'] and
                        type(pin['revision']) is int and 1<=pin['revision']<=target['revision'] and
                        isinstance(pin['sha256'],str) and re.fullmatch('[0-9a-f]{64}',pin['sha256']),
                        'Origem ou escopo de versão inválidos.')
                require(pin['revision']!=target['revision'] or pin==ref(pin['table'],target),
                        'A origem foi alterada sem uma nova revisão.')
                key=(pin['table'],pin['id']);require(key not in refs,'Vínculo duplicado.')
                refs[key]=pin
            require(('Projects',pid) in refs and ('Episodes',eid) in refs,'Proposta fora da base da mesa.')
            if data['shot_id']:
                shot=ix['Shot List'].get(data['shot_id'])
                require(shot and shot['episode_id']==eid and ('Shot List',shot['id']) in refs,'Plano fora do escopo da proposta.')
            ticket=data.get('ticket','')
            require(isinstance(ticket,str) and (not ticket and not data.get('input_sha256') or
                    ticket and re.fullmatch(r'PED-[A-Za-z0-9-]+',ticket) and isinstance(data.get('input_sha256'),str)
                    and re.fullmatch('[0-9a-f]{64}',data['input_sha256'])),'Protocolo da proposta inválido.')
            edit=data.get('edit')
            if edit is not None:
                require(isinstance(edit,dict) and set(edit)=={'source','offset_ms'} and isinstance(edit['source'],dict)
                        and edit['source'].get('table')=='Artifact Registry' and data.get('media')
                        and edit['source']!=data['media'] and type(edit['offset_ms']) is int and edit['offset_ms']!=0,
                        'Origem ou deslocamento da variação inválido.')
            for attached in (data.get('target'),data.get('media'), (edit or {}).get('source')):
                if attached:
                    require(isinstance(attached,dict) and attached in data['pins'],'O material deve estar entre as versões propostas.')
                    require(ix[attached['table']][attached['id']]['episode_id']==eid,'Material de outro episódio.')
            target=data.get('target')
            if target:
                require(target['table'] in {'Shot List','Screenplays','Characters','Locations','Props','Cinematography','Artifact Registry'}
                        and data['shot_id']==(target['id'] if target['table']=='Shot List' else ''),
                        'A proposta precisa identificar o seu único plano ou material.')
            if data.get('media'):
                require(data['shot_id'] and data['media']['table']=='Artifact Registry','Alternativa sem take do plano.')
        else:
            parent=ix['Decisions'].get(data.get('proposal_id'))
            require(parent and parent['topic']==proposal and (parent['project_id'],parent['episode_id'],parent['is_test'])==(pid,eid,row['is_test'])
                    and parent['id'] not in results,'Proposta ausente, de outro episódio ou já decidida.')
            require(data.get('choice') in {'accept','reject'} and isinstance(data.get('reason'),str)
                    and data['reason'].strip() and data.get('proposal_sha256')==fingerprint(parent),'Escolha sem justificativa ou origem alterada.')
            proposed=json.loads(parent['choice'])
            if data['choice']=='accept' and proposed.get('media'):
                original=next((p for p in proposed['pins'] if p['table']=='Shot List' and p['id']==proposed['shot_id']),None)
                claims=selected.get((row['last_op_id'],row['user_message_ref'],row['updated_by']),[])
                require(any(l['from']==original and l['to']==proposed['media'] for l in claims),
                        'Aceitar a alternativa exige selecionar esse take para o plano na mesma operação.')
            results.add(parent['id'])

def verify_new(before,after,changes,message):
    from desk_queue import PROPOSAL,RESULT,context_pin,candidates,material_for,attach_intake
    changes=[c for c in changes if c['table']=='Decisions' and c['after']['topic'] in {PROPOSAL,RESULT}]
    if not changes:return
    if 'intake_values' in before:before=attach_intake(before,before['intake_values'])
    ix=index(before)
    for change in changes:
        row=change['after']
        require(row['user_message_ref']==message,'A decisão da mesa precisa citar a autorização recebida.')
        data=json.loads(row['choice'])
        if row['topic']==PROPOSAL:
            reference=after
        else:
            parent=ix['Decisions'].get(data['proposal_id'])
            require(parent,'É preciso apresentar e registrar a proposta antes de decidir.')
            choice=data['choice']
            data=json.loads(parent['choice']);reference=before
        pid,eid=row['project_id'],row['episode_id']
        if row['topic']==PROPOSAL and not data.get('ticket'):
            require(data['author']==row['updated_by'],'A proposta direta deve identificar o autor da mensagem recebida.')
        if data.get('ticket'):
            requests=[entry for entry in before.get('desk_intake',[]) if entry['Pedido']==data['ticket']
                      and entry['sha256']==data.get('input_sha256') and candidates(before,pid,eid,entry)]
            require(len(requests)==1,'Pedido da fila alterado ou ausente. Releia a linha original.')
            entry=requests[0]
            require(data['request']==entry['Proposta'] and data['author']==(entry['Colaborador'] or 'Colaborador'),
                    'O pedido ou o colaborador diverge da linha recebida.')
            target=material_for(before,pid,eid,entry['Plano ou material'])
            if row['topic']==PROPOSAL:
                require(data.get('target')==target or ('target' not in data and target and target in data['pins']
                        and (target['table']!='Shot List' or data['shot_id']==target['id'])),
                        'O material diverge da linha recebida.')
            elif target:
                old=data.get('target') or next((p for p in data['pins'] if p['id']==target['id'] and p['table']==target['table']),None)
                require(old and (old['id'],old['table'])==(target['id'],target['table']),
                        'A linha deixou de apontar para o material da proposta.')
        if row['topic']==RESULT and choice=='reject':continue
        expected=context_pin(reference,pid,eid,data['shot_id'],data.get('media'),data.get('target'))
        expected=pins_with_origin(expected,data.get('edit'),reference)
        require(data['pins']==expected,'Conflito: reconfira os materiais e as dependências apresentados.')
        if data.get('media'):
            media,path=verified_media(reference,data['media'],pid,eid)
            links=[json.loads(d['choice']) for d in reference['tables']['Decisions'] if d['topic']==LINK and d['status']=='RECORDED']
            shot=ref('Shot List',index(reference)['Shot List'][data['shot_id']])
            require(any(l['relation']=='take' and l['from']==shot and l['to']==data['media'] for l in links),
                    'A versão do take precisa estar vinculada à versão do plano.')
        if data.get('edit'):
            edit=data['edit'];origin,_=verified_media(reference,edit['source'],pid,eid)
            require(any(l['relation']=='take' and l['from']==shot and l['to']==edit['source'] for l in links),
                    'A origem da variação precisa estar vinculada ao mesmo plano.')
            require(media['rights']==origin['rights'],'Os direitos da alternativa devem preservar os termos da origem.')
            if row['topic']==PROPOSAL:
                evidence=path.with_name('origem.json')
                require(evidence.is_file() and not evidence.is_symlink()
                        and json.loads(evidence.read_text(encoding='utf-8'))=={'provenance':edit,'sha256':media['sha256']},
                        'A alternativa precisa do comprovante local da edição proposta.')

