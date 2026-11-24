"""Retain compared versions and authorized plan drafts in the director's workspace."""
import base64
from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
from tempfile import NamedTemporaryFile

from shared_state import canonical, fingerprint, index, require, validate
from takes import local_media_path, manifest_hash, media_hash, take_pair, vote_plan
from history_integrity import verify_journal
from shot_workflow import ref, TOPIC as SHOT_LINK

def utc():
    return datetime.now(timezone.utc).isoformat()

def read(path):
    return json.loads(path.read_text(encoding='utf-8'))

def publish_once(path, write):
    """Install a fully written file if absent. Concurrent winners are re-read by callers."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with NamedTemporaryFile('w', delete=False, dir=path.parent, encoding='utf-8') as stream:
        tmp = Path(stream.name)
        try:
            write(stream)
            stream.flush()
            os.fsync(stream.fileno())
        except BaseException:
            stream.close()
            tmp.unlink(missing_ok=True)
            raise
    try:
        try:
            if os.name=='nt':
                os.rename(tmp,path)  # Windows rename is atomic and refuses an existing destination.
            else:
                os.link(tmp,path)
        except FileExistsError:
            pass
    finally:
        tmp.unlink(missing_ok=True)

def publish_media(path, write):
    """Rebuild the exact verified derivative and repair an interrupted/damaged copy."""
    path.parent.mkdir(parents=True,exist_ok=True)
    with NamedTemporaryFile('w',delete=False,dir=path.parent,encoding='utf-8') as stream:
        tmp=Path(stream.name)
        try:
            write(stream)
            stream.flush()
            os.fsync(stream.fileno())
        except BaseException:
            stream.close()
            tmp.unlink(missing_ok=True)
            raise
    try:
        if not path.exists() or media_hash(path)!=media_hash(tmp):
            os.replace(tmp,path)
    finally:
        tmp.unlink(missing_ok=True)

def state_dir(snapshot,pid,eid,workspace):
    return Path(workspace)/'desk-pairs'/fingerprint([snapshot['spreadsheet_id'],pid,eid])

def shot_from(snapshot,pid,eid,sid):
    shot=next((r for r in snapshot['tables']['Shot List'] if r['id']==sid and
               r['project_id']==pid and r['episode_id']==eid and r.get('status')!='ARCHIVED'),None)
    require(shot is not None,'Plano ausente, arquivado ou de outro episódio.')
    return shot

def shot_binding(shot):
    return {k:shot[k] for k in ('id','revision','scene_beat')} | {'sha256':fingerprint(shot)}

def require_shot_association(snapshot,shot,asset):
    linked=[]
    for row in snapshot['tables']['Decisions']:
        if row['topic']!=SHOT_LINK or row['status']!='RECORDED' or row['episode_id']!=shot['episode_id']:continue
        edge=json.loads(row['choice'])
        if edge['relation'] in {'take','selected_take'} and edge['to']['id']==asset['id']:linked.append(edge)
    if linked:
        require(any(e['from']==ref('Shot List',shot) and e['to']==ref('Artifact Registry',asset) for e in linked),
                'O take pertence a outro plano ou versão. Confira a associação apresentada.')

def pairs_in(snapshot,pid,eid,workspace):
    root=state_dir(snapshot,pid,eid,workspace)
    records = []
    for path in sorted(root.glob('pair-*.json')):
        entry=read(path)
        manifest=entry['manifest']
        require(manifest['pair_sha256']==manifest_hash(manifest) and
                (manifest['spreadsheet_id'],manifest['project_id'],manifest['episode_id'])==
                (snapshot['spreadsheet_id'],pid,eid),'O par local diverge da produção.')
        records.append(entry)
    return sorted(records,key=lambda r:(r['at'],r['manifest']['pair_id']))

def retain_pair(snapshot,spec,workspace):
    pid,eid=spec['project_id'],spec['episode_id']
    shot=shot_from(snapshot,pid,eid,spec['shot_id'])
    registry=index(snapshot)['Artifact Registry']
    for item in spec['takes']:
        row=registry.get(item['id'])
        require(row,'Take não encontrado no registro.')
        require_shot_association(snapshot,shot,row)
        local_only(item.get('path') or row['uri'])
    manifest=take_pair(snapshot,spec)
    bound=shot_binding(shot)
    manifest['shot']=bound
    manifest['pair_sha256']=manifest_hash(manifest)
    parts=sorted((t['id'],t['revision'],t['sha256']) for t in manifest['takes'].values())
    paths={r['id']:str(local_media_path(r.get('path') or registry[r['id']]['uri']).resolve()) for r in spec['takes']}
    key=fingerprint([bound,spec.get('presentation_ref',''),manifest['question'],parts,paths])
    path=state_dir(snapshot,pid,eid,workspace)/('pair-'+key+'.json')
    entry={'at':utc(),'manifest':manifest,'shot_id':shot['id'],'paths':paths}
    publish_once(path,lambda f:f.write(canonical(entry)))
    saved=read(path)
    require(saved['manifest']['pair_sha256']==manifest_hash(saved['manifest']), 'Manifesto local alterado.')
    return {'kind':'LOCAL_PAIR_RETAINED','shot_id':shot['id'],'manifest':saved['manifest'],'remote_write':False}

def local_only(value):
    text=str(value).strip().replace(chr(92),'/')
    require(text and not text.startswith('//') and '://' not in text and not text.lower().startswith('file:'),
            'Use um arquivo local acessível na máquina da mesa.')

def checked_path(snapshot,entry,label):
    take=entry['manifest']['takes'][label]
    row=next((r for r in snapshot['tables']['Artifact Registry'] if r['id']==take['id']),None)
    require(row and all(row[k]==take[k] for k in ('revision','sha256','version')) and
            (row['project_id'],row['episode_id'])==(entry['manifest']['project_id'],entry['manifest']['episode_id']),
            'A versão do take '+label+' mudou. Apresente outro par.')
    local_only(entry['paths'][take['id']])
    path=Path(entry['paths'][take['id']])
    require(path.is_file(),'Arquivo do take '+label+' indisponível.')
    return path

def project_media(path,take,media_dir):
    if media_dir and path.stat().st_size>8*1024*1024:
        # Each sidecar is requested only when opening its pair, including on file://.
        target=Path(media_dir)/(take['sha256']+'.js')
        def write(stream):
            checksum=sha256()
            with path.open('rb') as source:
                stream.write("window.CPE_MEDIA_CHUNKS("+json.dumps(take['sha256'])+",[")
                first=True
                while chunk:=source.read(384*1024):
                    checksum.update(chunk)
                    if not first:stream.write(',')
                    stream.write(json.dumps(base64.b64encode(chunk).decode('ascii')))
                    first=False
                stream.write("]);")
            require(checksum.hexdigest()==take['sha256'],'Arquivo de mídia substituído desde a apresentação.')
        publish_media(target,write)
        return 'media/'+target.name
    raw=path.read_bytes()
    require(sha256(raw).hexdigest()==take['sha256'],'Arquivo de mídia substituído desde a apresentação.')
    return 'data:'+take['mime']+';base64,'+base64.b64encode(raw).decode('ascii')

def presentable_pairs(snapshot,project_id,episode_id,workspace,media_dir=None):
    rows=[]
    for entry in pairs_in(snapshot,project_id,episode_id,workspace):
        manifest=entry['manifest']
        item={'shot_id':entry['shot_id'],'manifest':manifest,'media':{}}
        try:
            shot=shot_from(snapshot,project_id,episode_id,entry['shot_id'])
            require(shot_binding(shot)==manifest['shot'],'O plano mudou. Apresente um par ligado à versão vigente.')
            for label,take in manifest['takes'].items():
                current=index(snapshot)['Artifact Registry'].get(take['id'])
                require(current,'O take apresentado foi removido.')
                require_shot_association(snapshot,shot,current)
                item['media'][label]=project_media(checked_path(snapshot,entry,label),take,media_dir)
        except (ValueError,OSError) as reason:
            item.update(media={},unavailable=str(reason))
        rows.append(item)
    return rows

def select_pair(snapshot,spec,workspace):
    pairs=pairs_in(snapshot,spec['project_id'],spec['episode_id'],workspace)
    if spec.get('pair_id'):
        pairs=[r for r in pairs if r['manifest']['pair_id']==spec['pair_id']]
    if spec.get('shot_id'):
        pairs=[r for r in pairs if r['shot_id']==spec['shot_id']]
    if spec.get('question'):
        pairs=[r for r in pairs if r['manifest']['question']==spec['question']]
    if spec.get('pair_hint'):
        hint=spec['pair_hint'].lower()
        require(len(hint)==8 and all(c in '0123456789abcdef' for c in hint),'Referência curta de par inválida.')
        pairs=[r for r in pairs if r['manifest']['pair_id'].endswith(hint)]
    require(pairs,'Nenhum par apresentado corresponde a esta decisão.')
    if len(pairs)>1:
        return {'kind':'PAIR_CLARIFICATION','choices':[{'pair_id':r['manifest']['pair_id'],'shot_id':r['shot_id'],
                'pair_sha256':r['manifest']['pair_sha256'],
                'question':r['manifest']['question'],'presented_at':r['at']} for r in pairs], 'remote_write':False}
    return pairs[0]

def vote_from_message(snapshot,spec,workspace):
    auth=spec['authorization']
    require(auth.get('authorized') is True and bool(auth.get('actor')) and bool(auth.get('user_message_ref')),
            'A decisão precisa vir de uma mensagem autorizada.')
    entry=select_pair(snapshot,spec,workspace)
    if entry.get('kind')=='PAIR_CLARIFICATION':return entry
    manifest=entry['manifest']
    require(spec.get('pair_id')==manifest['pair_id'] and spec.get('pair_sha256')==manifest['pair_sha256'],
            'Confirme o ID e a versão do par que o diretor viu. Apresente novamente se o par mudou.')
    require(not manifest['is_test'] or spec.get('include_test') is True,'Exija o escopo explícito de ensaio.')
    root=state_dir(snapshot,spec['project_id'],spec['episode_id'],workspace)
    vote={k:spec[k] for k in ('choice','mark_ms','reason','preference_scope')}
    vote.update(start_ms=spec.get('start_ms',vote['mark_ms']),end_ms=spec.get('end_ms',vote['mark_ms']),
                authorized=True,kind='CPE_TAKE_VOTE_1',pair_id=manifest['pair_id'],pair_sha256=manifest['pair_sha256'])
    require(isinstance(vote['reason'],str) and vote['reason'].strip(),'Indique o motivo do voto.')
    vote['reason']=vote['reason'].strip()
    # Keep one immutable request per actor/presentation. A changed decision uses an explicit new presentation.
    request_id=fingerprint([manifest['pair_id'],auth['actor']])
    path=root/('vote-'+request_id+'.json')
    request={'vote':vote,'authorization':auth}
    if path.exists():
        saved=read(path)
        require(saved['vote']==vote,'Já há outra decisão neste par. Reconcilie a anterior e apresente uma nova comparação.')
        auth=saved['authorization']
    key=fingerprint([manifest['pair_id'],auth['user_message_ref']])[:28]
    op='TAKE-VOTE-'+key
    data_rows={c['id'] for table in ('Examples','Pairwise Comparisons','Human Feedback') for c in snapshot['tables'][table]}
    events=[r for r in snapshot['tables']['Revision History'] if r['op_id']==op]
    existing=data_rows&{'EX-'+key,'CMP-'+key,'HF-'+key}
    if events or existing:
        # A repeated request is an inspection, never permission to write again.
        state='RECONCILIATION_REQUIRED'
        if events and any(r['event']=='CONFIRMED' for r in events):
            ix=index(snapshot)
            for cached in root.glob('plan-'+key+'-*.json'):
                retained=read(cached)
                try:
                    verify_journal(retained,snapshot,require_prepared=True,require_confirmed=True)
                except ValueError:
                    continue
                if all(ix[c['table']].get(c['id'])==c['after'] for c in retained['changes']):
                    state='ALREADY_CONFIRMED'
                    break
        return {'kind':state,'op_id':op,'remote_write':False,'history_events':[r['event'] for r in events]}
    shot=shot_from(snapshot,spec['project_id'],spec['episode_id'],entry['shot_id'])
    require(shot_binding(shot)==manifest['shot'],'A versão do plano mudou. Apresente novamente os takes.')
    for take in manifest['takes'].values():
        current=index(snapshot)['Artifact Registry'].get(take['id'])
        require(current,'O take apresentado foi removido.')
        require_shot_association(snapshot,shot,current)
    plan=vote_plan(snapshot,{'manifest':manifest,'vote':vote,'authorization':auth,'paths':entry['paths']})
    publish_once(path,lambda f:f.write(canonical(request)))
    saved=read(path)
    if saved['authorization']!=auth or saved['vote']!=vote:
        return vote_from_message(snapshot,spec,workspace)
    # The original plan is needed for timestamp/digest checks after an uncertain write.
    generation=fingerprint([plan['guards'],plan['history_baseline']])
    cached=root/('plan-'+key+'-'+generation+'.json')
    publish_once(cached,lambda f:f.write(canonical(plan)))
    return read(cached)

def dispatch(action,snapshot,spec,workspace):
    validate(snapshot)
    require(action in ('desk-pair','desk-vote'),'Comando desconhecido de comparação.')
    if action=='desk-pair':return retain_pair(snapshot,spec,workspace)
    return vote_from_message(snapshot,spec,workspace)

