"""Build the offline director's desk from an agent-supplied shared-state read."""
import base64
import contextlib
import hashlib
import json
import mimetypes
import os
from pathlib import Path
import re
import secrets
import tempfile
import unicodedata
import shutil
from collections import defaultdict

from knowledge_select import select as select_knowledge
from series_bible import handoff
from shared_state import fingerprint, index, require, timestamp, validate
from shot_workflow import card, impact

ROOT = Path(__file__).resolve().parents[1]
from local_binding import load_binding
BINDING = load_binding()
PANEL_DIR = ROOT / 'panels'
PUBLICATION_MARKER = '// CPE_DESK_PUBLICATION '
OWNER_FILE = '.cpe-desk-owner.json'
MEDIA_FIELDS = {
    'Characters': ('name', 'identity', 'costume', 'performance'),
    'Props': ('name', 'material_scale', 'state', 'owner_character_id'),
    'Locations': ('name', 'anchors', 'state', 'light_weather'),
    'Screenplays': ('title', 'text_or_ref'),
    'Cinematography': ('intent', 'focal_mm', 'composition', 'light', 'motion'),
    'Prompts': ('target_id', 'model', 'prompt_text'),
    'Artifact Registry': ('kind', 'department', 'origin', 'sha256'),
    'Continuity': ('scene_beat', 'entity_id', 'before_state', 'event', 'after_state'),
    'Experiments': ('lab', 'objective', 'hypothesis', 'observed'),
    'Shot List': ('scene_beat','order','purpose','action'),
    'Reference Library': ('title','author','rights','context','limitations'),
    'Examples': ('title','kind','department','expected','limitations'),
    'Techniques': ('name','department','when_to_use','tradeoff'),
    'Model Compatibility': ('model_id','output_type','checked_at','generation_tested','limitations'),
    'Production Lessons': ('department','context','observation','correction','scope'),
    'Director Profiles': ('title','intention','principle','application','limitations'),
    'Genre Profiles': ('name','question','tools','pacing','limitations'),
    'Prompt Library': ('name','model_id','generation_tested','observed'),
    'Evaluation Results': ('target_id','target_revision','department','artistic_result','decision','limitations'),
    'Pairwise Comparisons': ('target_id','target_revision','department','outcome','limitations'),
    'Human Feedback': ('target_id','target_revision','human_decision','reason','preference_scope'),
    'Failure Diagnostics': ('target_id','target_revision','symptom','probable_cause','confidence','repair'),
    'Revision Results': ('previous_id','previous_revision','current_id','current_revision','problem','resolved','persistent'),
    'Tool Capabilities': ('name','availability','scope','alternative','checked_at'),
    'Execution Evidence': ('operation','department','execution_state','result','limitations'),
    'Checkpoints': ('source_read_at','sync_status','last_confirmed_op'),
}


def key(text):
    normal = unicodedata.normalize('NFKD', str(text).strip().casefold())
    return ' '.join(''.join(c for c in normal if not unicodedata.combining(c)).split())


def match_one(rows, label, query):
    require(rows, f'{label} não encontrado para {query!r}.')
    require(len(rows) == 1, f'{label} ambíguo para {query!r}; identifique a série ou o título do episódio.')
    return rows[0]


def resolve_scope(snapshot, spec):
    validate(snapshot)
    permit_test = spec.get('include_test') is True
    projects = [p for p in snapshot['tables']['Projects'] if permit_test or not p['is_test']]
    project_query = spec.get('project_id') or spec.get('project')
    if project_query:
        exact = [p for p in projects if p['id'] == project_query]
        projects = exact or [p for p in projects if key(p['name']) == key(project_query)]
    project_ids = {p['id'] for p in projects}
    episodes = [e for e in snapshot['tables']['Episodes'] if e['project_id'] in project_ids]
    ep_query = spec.get('episode_id') or spec.get('episode')
    if ep_query is not None:
        exact = [e for e in episodes if e['id'] == ep_query]
        number = re.fullmatch(r'(?:ep(?:isodio)?\s*[-#]?\s*)?(\d+)', key(ep_query))
        episodes = exact or [e for e in episodes if key(e['title']) == key(ep_query)
                             or (number and e['episode_number'] == int(number[1]))]
    episode = match_one(episodes, 'Episódio', ep_query)
    project = next(p for p in projects if p['id'] == episode['project_id'])
    require(project['is_test'] or snapshot['spreadsheet_id'] == BINDING['spreadsheet_id'],
            'Planilha de produção diferente da conta vinculada.')
    return project, episode


def minimal_source(source):
    if not isinstance(source, dict):
        return None
    return {k:source[k] for k in ('id','revision','reason','sheet_url','record_sha256') if k in source}


def local_thumbnail(links, registry):
    reasons = []
    for link in links:
        if link['relation'] not in {'reference','storyboard'}:
            continue
        asset = registry.get(link['from']['id'])
        if not asset:
            continue
        if link['stale'] or not asset['rights'].strip():
            reasons.append(asset['id']+' · conferir versão ou direitos.')
            continue
        uri = asset['uri']
        if '://' in uri or uri.startswith(('\\\\','//')):
            reasons.append(asset['id']+' · referência externa.')
            continue
        path = ROOT / Path(uri)
        mime = mimetypes.guess_type(path.name)[0]
        if mime not in {'image/png','image/jpeg','image/webp'}:
            reasons.append(asset['id']+' · sem imagem de referência compatível.')
            continue
        try:
            if path.stat().st_size > 2_000_000:
                reasons.append(asset['id']+' · gerar miniatura local.')
                continue
            with path.open('rb') as stream:
                blob = stream.read(2_000_001)
            if len(blob)>2_000_000:
                reasons.append(asset['id']+' · gerar miniatura local.')
                continue
        except (OSError,ValueError):
            reasons.append(asset['id']+' · arquivo indisponível.')
            continue
        if hashlib.sha256(blob).hexdigest() != asset['sha256']:
            reasons.append(asset['id']+' · arquivo alterado.')
            continue
        return 'data:'+mime+';base64,'+base64.b64encode(blob).decode('ascii'), ''
    return '', ' '.join(reasons) or 'Miniatura pendente.'


def bible_projection(snapshot, project_id, episode_id):
    bible = handoff(snapshot,project_id,episode_id)
    def fact(item):
        result = {k:item[k] for k in ('kind','subject','key','value','beat','sequence','episode_id',
                                     'episode_number','previous_decision_id') if k in item}
        result['source'] = minimal_source(item['source'])
        return result
    return {'facts':{k:[fact(f) for f in group] for k,group in bible['facts'].items()},
            'timeline':[fact(f) for f in bible['timeline']],
            'proposals':[fact(f) for f in bible['proposals']]}


def shot_label(shot_id):
    suffix = re.search(r'(?:^|[-_])(SH\d+)$',shot_id,re.I)
    return suffix[1].upper() if suffix else shot_id


def positions(shots, timeline, episode_id):
    """Only place a fact when its authored beat identifies a shot or its scene by name."""
    facts = [f for f in timeline if f['episode_id'] == episode_id]
    locations = {}
    labels = [key(shot_label(shot['id'])) for shot in shots]
    for shot in shots:
        identifiers={key(shot['id'])}
        label=key(shot_label(shot['id']))
        if labels.count(label)==1:
            identifiers.add(label)
        matches = sorted((f for f in facts if key(f['beat']) in identifiers),
                         key=lambda f:f['sequence'])
        scene_matches = sorted((f for f in facts if key(f['beat']) == key(shot['scene_beat'])),
                               key=lambda f:f['sequence'])
        source = matches or scene_matches
        if source:
            start = source[0]['sequence'] - 1
            precision = 'shot' if matches else 'scene'
            # Same-scene positions may be selected manually but never silently assigned to a line.
            positions_ = sorted({(f['sequence'],f['beat']) for f in source})
            locations[shot['id']] = {'precision':precision,'previous_sequence':start,
                                     'positions':[{'sequence':s,'beat':b} for s,b in positions_]}
        else:
            locations[shot['id']] = {'precision':'episode','previous_sequence':0,'positions':[]}
    return locations


def materials_for(snapshot, project_id, episode_id):
    ix=index(snapshot)
    project_row,episode=ix['Projects'][project_id],ix['Episodes'][episode_id]
    gate=next((r['gate_id'] for r in snapshot['tables']['Workflow'] if r['episode_id']==episode_id
               and r['status'] not in {'APPROVED','SKIPPED','LOCKED'}),'G10')
    knowledge,_=select_knowledge(snapshot,project_row,episode,gate,(),None,episode['title'])
    shared={table:{r['id'] for r in rows if r['project_id']=='LIB-CPE31' and not r['is_test']}
            for table,rows in knowledge.items()}
    result={}
    for table, fields in MEDIA_FIELDS.items():
        result[table] = []
        for row in snapshot['tables'][table]:
            local=row['project_id']==project_id and row['episode_id'] in {'',episode_id}
            library=row['project_id']=='LIB-CPE31' and row['id'] in shared.get(table,())
            if not (local or library) or row['status'] in {'ARCHIVED','REJECTED'}:
                continue
            entry={k:row[k] for k in ('id','revision','version','status',*fields) if k in row}
            entry['label']=next((row[k] for k in ('name','title','objective','model_id','operation','symptom','context','origin')
                                 if row.get(k)),row['id'])
            if library:
                entry['library']=True
            result[table].append(entry)
    return result


def shot_preferences(snapshot, project_id, episode):
    """Retain the exact presentation at its original shot, even if a new version is current."""
    from desk_queue import receipt
    ix=index(snapshot)
    by_shot=defaultdict(list)
    events=defaultdict(list)
    for event in snapshot['tables']['Revision History']:
        events[event['op_id']].append(event)
    scope=(project_id,episode['id'],episode['is_test'])
    for row in snapshot['tables']['Human Feedback']:
        if (row['project_id'],row['episode_id'],row['is_test'])!=scope or row['target_table']!='Pairwise Comparisons':
            continue
        pair=ix['Pairwise Comparisons'].get(row['target_id'])
        if not pair or (pair['project_id'],pair['episode_id'],pair['is_test'])!=scope:
            continue
        if any(r['status'] in {'ARCHIVED','REJECTED'} for r in (row,pair)):
            continue
        if pair['revision']!=row['target_revision'] or pair['human_decision_ref']!=row['user_message_ref']:
            continue
        try:
            evidence=json.loads(row['evidence'])
            if not isinstance(evidence,dict) or evidence.get('kind')!='TAKE_PREFERENCE' or evidence!=json.loads(pair['order_results_json']):
                continue
            shot_ref=evidence['shot']
            shot=ix['Shot List'][shot_ref['id']]
            if (shot['project_id'],shot['episode_id'],shot['is_test'])!=scope:
                continue
            choice=evidence['choice']
            if {'A':'PREFER_A','B':'PREFER_B','TIE':'TIE','BOTH_FAIL':'BOTH_FAIL'}.get(choice)!=row['human_decision']:
                continue
            if evidence['reason']!=row['reason'] or evidence['preference_scope']!=row['preference_scope']:
                continue
            takes={label:{k:evidence['takes'][label][k] for k in ('id','revision','version','sha256')} for label in ('A','B')}
            if pair['outcome']!=(takes[choice]['id'] if choice in takes else choice):
                continue
            current=shot_ref['revision']==shot['revision'] and shot_ref['sha256']==fingerprint(shot)
            for take in takes.values():
                asset=ix['Artifact Registry'].get(take['id'])
                current=current and bool(asset) and (asset['project_id'],asset['episode_id'],asset['is_test'])==scope and all(asset[k]==v for k,v in take.items())
            timing={k:evidence[k] for k in ('start_ms','mark_ms','end_ms')}
            if not all(type(v) is int for v in timing.values()) or not 0<=timing['start_ms']<=timing['mark_ms']<=timing['end_ms']:
                continue
        except (ValueError,KeyError,TypeError):
            continue
        source={'id':row['id'],'revision':row['revision'],'table':'Human Feedback'}
        if snapshot['spreadsheet_id']==BINDING['spreadsheet_id']:
            source['sheet_url']=BINDING['spreadsheet_url'].split('#')[0]+'#gid='+str(BINDING['sheet_ids']['Human Feedback'])
            position=snapshot.get('source_rows',{}).get('Human Feedback',{}).get(row['id'])
            if type(position) is int and position>=2:
                source['sheet_url']+='&range=A'+str(position)
        operation=receipt(snapshot,row,events,table='Human Feedback')
        by_shot[shot['id']].append({**timing,'choice':choice,'takes':takes,'pair_id':pair['session_ref'],
                                    'shot_revision':shot_ref['revision'],'reason':row['reason'],'scope':row['preference_scope'],
                                    'current':current,'confirmed':bool(operation),'operation':operation,'is_test':row['is_test'],
                                    'source':source,'at':row['updated_at']})
    for items in by_shot.values():
        items.sort(key=lambda item:(timestamp(item['at']),item['source']['id']),reverse=True)
    return by_shot


def project(snapshot, spec, workspace, media_dir=None):
    project_row, episode = resolve_scope(snapshot,spec)
    pid,eid = project_row['id'],episode['id']
    registry = index(snapshot)['Artifact Registry']
    shot_rows = sorted((r for r in snapshot['tables']['Shot List'] if r['episode_id']==eid and r['status']!='ARCHIVED'),
                       key=lambda r:(r['order'],r['id']))
    bible = bible_projection(snapshot,pid,eid)
    temporal = positions(shot_rows, bible['timeline']+bible['proposals'],eid)
    preferences = shot_preferences(snapshot,pid,episode)
    shots, previous = [], {}
    for row in shot_rows:
        c = card(snapshot,row['id'])
        image, presentation = local_thumbnail(c['links'],registry)
        links=[]
        for link in c['links']:
            links.append({**link,'decision':minimal_source(link['decision'])})
        affected=impact(snapshot,row['id'],'')['affected']
        shots.append({'id':row['id'],'label':shot_label(row['id']),'revision':row['revision'],'version':row['version'],
                      'status':row['status'],'record_sha256':c['shot']['sha256'],'scene':c['beat'],
                      'order':c['order'],'duration_s':c['duration_s'],'action':c['action'],'intention':c['intention'],
                      'camera':c['camera'],'sound':c['sound'],'states':c['states'],'links':links,
                      'last_decision':minimal_source(c['last_decision']),'selected_take':c['selected_take'],
                      'preferences':preferences.get(row['id'],[]),
                      'thumbnail':image,'presentation':presentation,'continuity_review':c['continuity_review'],
                      'previous_shot':previous.get(c['beat']), 'temporal':temporal[row['id']],
                      'impact':[{**i['current'],'relationship':i['relationship']} for i in affected if i['current']]})
        previous[c['beat']]=row['id']
    from desk_queue import projection
    from desk_pairs import presentable_pairs
    work = projection(snapshot,pid,eid)
    pairs = presentable_pairs(snapshot,pid,eid,workspace,media_dir)
    workflow=[{k:w[k] for k in ('gate_id','name','status','revision','depends_on','skippable')}
              for w in snapshot['tables']['Workflow'] if w['episode_id']==eid]
    urls={}
    if snapshot['spreadsheet_id']==BINDING['spreadsheet_id']:
        base=BINDING['spreadsheet_url'].split('#')[0]+'#gid='
        urls={'dashboard_url':base+str(BINDING['sheet_ids']['Dashboard']),
              'queue_url':base+str(BINDING['sheet_ids']['Fila de direção'])}
    return {**urls,'version':1,'spreadsheet_id':snapshot['spreadsheet_id'],'read_at':snapshot['read_at'],
            'series':{'id':pid,'name':project_row['name'],'is_test':project_row['is_test']},
            'episode':{'id':eid,'title':episode['title'],'number':episode['episode_number'],'is_test':episode['is_test']},
            'workflow':workflow,'shots':shots,'bible':bible,'materials':materials_for(snapshot,pid,eid),
            'queue':work['queue'],'alternatives':work['alternatives'],'pairs':pairs}


def compact(value):
    return json.dumps(value, ensure_ascii=True, separators=(',',':'))


@contextlib.contextmanager
def publication_lock(path):
    """The OS releases the file lock on normal exit and process termination."""
    with path.open('a+b') as f:
        if f.tell()==0:
            f.write(b'0')
            f.flush()
        f.seek(0)
        if os.name=='nt':
            import msvcrt
            try:
                msvcrt.locking(f.fileno(),msvcrt.LK_NBLCK,1)
            except OSError as exc:
                raise RuntimeError('Outra atualização está em curso; releia antes de tentar novamente.') from exc
        else:
            import fcntl
            fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB)
        try:
            yield
        finally:
            f.seek(0)
            if os.name=='nt':
                msvcrt.locking(f.fileno(),msvcrt.LK_UNLCK,1)
            else:
                fcntl.flock(f,fcntl.LOCK_UN)


def atomic_bytes(path,data):
    require(not path.is_symlink(),'Destino de publicação é um vínculo simbólico.')
    fd, name = tempfile.mkstemp(dir=path.parent)
    try:
        with os.fdopen(fd,'wb') as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        os.replace(name,path)
    finally:
        Path(name).unlink(missing_ok=True)


def addressed_asset(base, source):
    blob=source.read_bytes()
    name=hashlib.sha256(blob).hexdigest()+source.suffix
    destination=base/name
    if destination.exists():
        require(not destination.is_symlink() and destination.read_bytes()==blob, 'Arquivo local de interface alterado.')
    else:
        atomic_bytes(destination,blob)
    return 'assets/'+name


def shell_parts(template, asset_dir):
    html=template.read_text(encoding='utf-8')
    pattern=r'\b(src|href)="([^"]+)"'
    def replace_asset(match):
        attr, url = match.groups()
        if url=='desk-data.js':
            return 'data-desk-view="current"'  # Already loaded by the stable entry.
        if url.startswith(('#','https://','data:')) or url.split('?',1)[0] in {'takes.html','studio.html'}:
            return match[0]
        if url=='../examples/series-worked/episode-guide.html':
            example = ROOT/'examples/series-worked/episode-guide.html'
            return attr+'="'+addressed_asset(asset_dir,example)+'"'
        require('/' not in url and '\\' not in url and url not in ('.','..'),'Recurso local desconhecido na interface: '+url)
        source=PANEL_DIR/url
        require(source.is_file(),'Recurso ausente na instalação: '+url)
        return attr+'="'+addressed_asset(asset_dir,source)+'"'
    rewritten=re.sub(pattern,replace_asset,html)
    head=re.search(r'<head\b[^>]*>(.*?)</head>',rewritten,flags=re.S|re.I)
    body=re.search(r'<body\b([^>]*)>(.*?)</body>',rewritten,flags=re.S|re.I)
    require(head and body,'Estrutura HTML da interface inválida.')
    require(not body[1].strip(),'Atributos de body requerem migração explícita do lançador.')
    return {'head':head[1],'body':body[2]}


def launcher(page):
    """Native classic script insertion preserves script order and a stable file URL for drafts."""
    return (f'<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">'
            f'<script src="desk-data.js"></script><script>if(window.CPE_DESK_PAGES)document.write(CPE_DESK_PAGES.{page}.head)</script>'
            f'</head><body><script>if(window.CPE_DESK_PAGES)document.write(CPE_DESK_PAGES.{page}.body);'
            'else document.write("Mesa indisponível. Peça ao agente para atualizar a leitura.")</script></body></html>').encode('utf-8')


def build_commit(stage, data, header):
    assets=stage/'assets'
    require(not assets.is_symlink(),'Diretório de interface inválido.')
    assets.mkdir(exist_ok=True)
    pages={name:shell_parts(PANEL_DIR/(name+'.html'),assets) for name in ('studio','takes')}
    return (PUBLICATION_MARKER+compact(header)+'\nwindow.CPE_DESK_DATA='+compact(data)+';\n'
            +'window.CPE_DESK_PAGES='+compact(pages)+';\n').encode('utf-8')


def commit(stage,snapshot,spec,workspace,header,initial):
    if initial:
        atomic_bytes(stage/OWNER_FILE,compact(header['owner']).encode('utf-8'))
        for name in ('studio','takes'):
            atomic_bytes(stage/(name+'.html'),launcher(name))
    else:
        owner=stage/OWNER_FILE
        require(owner.is_file() and not owner.is_symlink() and json.loads(owner.read_text(encoding='utf-8'))==header['owner'],
                'A pasta pertence a outro projeto ou não foi criada pelo Studio.')
        for name in ('studio','takes'):
            page=stage/(name+'.html')
            require(page.is_file() and not page.is_symlink() and page.read_bytes()==launcher(name),
                    'O lançador da mesa foi modificado; preservar e verificar antes de atualizar.')
        with (stage/'desk-data.js').open(encoding='utf-8') as old:
            line=old.readline()
        require(line.startswith(PUBLICATION_MARKER),'A última publicação precisa de recuperação.')
        before=json.loads(line[len(PUBLICATION_MARKER):])
        require(before['owner']==header['owner'],'Outro proprietário da mesa.')
        require(timestamp(header['read_at'])>=timestamp(before['read_at']),'Leitura anterior à mesa aberta; consultar a planilha novamente.')
        require(timestamp(header['read_at'])!=timestamp(before['read_at']) or before['digest']==header['digest'],
                'Duas leituras diferentes têm o mesmo instante; reler o estado.')
    media_dir = stage/'media'
    require(not media_dir.is_symlink(),'Diretório de mídia inválido.')
    data = project(snapshot,spec,workspace,media_dir)
    payload=build_commit(stage,data,header)
    atomic_bytes(stage/'desk-data.js',payload)
    return data


def dispatch(action,snapshot,spec,workspace):
    require(action=='desk-publish','Comando de publicação desconhecido.')
    workspace=Path(workspace).resolve()
    require(not workspace.is_relative_to(ROOT),'Escolha uma pasta de trabalho fora da instalação.')
    series,_ = resolve_scope(snapshot,spec)
    owner={'source':snapshot['spreadsheet_id'],'project':series['id'],'is_test':series['is_test']}
    # Names are editable. IDs are the stable identity and never become raw filesystem paths.
    token=fingerprint(owner)[:24]
    base=Path(spec['publish_root']) if spec.get('publish_root') else workspace/'mesas'
    require(base.is_absolute() and not str(base).replace(chr(92),'/').startswith('//'),
            'Use um caminho absoluto local para as mesas.')
    require(not base.is_symlink(),'A raiz de mesas deve ser uma pasta local da produção.')
    base=base.resolve()
    require(not base.is_relative_to(ROOT) and not base.is_relative_to(workspace/'desk-pairs'),
            'Mantenha o destino das mesas fora da instalação e da área privada de pares.')
    base.mkdir(parents=True,exist_ok=True)
    destination=base/('serie-'+token)
    curated={'Reference Library','Examples','Techniques','Model Compatibility','Production Lessons'}
    relevant={n:sorted((r for r in rows if r['project_id']==owner['project']
                        or (n in curated and r['project_id']=='LIB-CPE31' and not r['is_test'])),key=lambda r:r['id'])
              for n,rows in snapshot['tables'].items()}
    relevant['desk_intake']=sorted((q for q in snapshot.get('desk_intake',[])
                                    if key(q.get('Série','')) in {key(series['id']),key(series['name'])}),
                                   key=lambda q:q['Pedido'])
    relevant['desk_intake_issues']=[q for q in snapshot.get('desk_intake_issues',[])
                                   if key(q.get('Série','')) in {key(series['id']),key(series['name'])}]
    header={'owner':owner,'read_at':snapshot['read_at'],'digest':fingerprint(relevant)}
    lock_path=base/(token+'.lock')
    require(not lock_path.is_symlink(),'Vínculo inválido no controle da publicação.')
    with publication_lock(lock_path):
        require(not destination.is_symlink(),'Destino da mesa inválido.')
        if destination.exists():
            data=commit(destination,snapshot,spec,workspace,header,False)
        else:
            stage=Path(tempfile.mkdtemp(prefix='preparo-',dir=base))
            try:
                data=commit(stage,snapshot,spec,workspace,header,True)
                stage.rename(destination)
            finally:
                if stage.exists() and stage.resolve().parent==base.resolve() and stage.name.startswith('preparo-'):
                    shutil.rmtree(stage)
    return {'kind':'PUBLISHED_LOCAL_DESK','project_id':owner['project'],'episode_id':data['episode']['id'],
            'studio':str(destination/'studio.html'),'comparator':str(destination/'takes.html'),'data':str(destination/'desk-data.js'),
            'source_read_at':header['read_at'],'source_test':owner['is_test'],'shots':len(data['shots']),
            'pairs':len(data['pairs']),'user_file_transfers':0,'remote_read_performed_by_cli':False}

