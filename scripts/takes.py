"""Compare two registered local media revisions and prepare a director's vote for Sheets."""
import datetime
import hashlib
import json
import math
import secrets
import uuid
from pathlib import Path

from shared_state import canonical, fingerprint, prepare, require, validate

FORMATS = {
    '.mp4': 'video/mp4', '.webm': 'video/webm', '.mov': 'video/quicktime',
    '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.png': 'image/png', '.webp': 'image/webp',
    '.wav': 'audio/wav', '.mp3': 'audio/mpeg', '.ogg': 'audio/ogg', '.m4a': 'audio/mp4',
}
ROOT = Path(__file__).resolve().parents[1]

def local_media_path(value):
    location=str(value).strip().replace(chr(92),'/')
    require(location and not location.startswith('//') and '://' not in location and not location.lower().startswith('file:'),
            'Use uma cópia local do take cadastrado.')
    candidate = Path(value)
    if candidate.is_absolute() or candidate.is_file():
        return candidate
    return ROOT / candidate

def media_hash(path):
    with path.open('rb') as stream:
        h = hashlib.sha256()
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(chunk)
        return h.hexdigest()

def manifest_hash(manifest):
    return fingerprint({k: v for k, v in manifest.items() if k != 'pair_sha256'})

def scope_rows(snapshot, project, episode):
    validate(snapshot)
    episode_row = next((r for r in snapshot['tables']['Episodes']
                        if r['id'] == episode and r['project_id'] == project), None)
    require(episode_row is not None, 'Episódio e projeto não correspondem.')
    return episode_row, {r['id']: r for r in snapshot['tables']['Artifact Registry']
                         if r['episode_id'] == episode and r['project_id'] == project}

def descriptor(row, path):
    mime = FORMATS.get(path.suffix.lower())
    require(path.is_file() and mime, 'Arquivo de imagem, áudio ou vídeo compatível necessário.')
    require(media_hash(path) == row['sha256'], 'O arquivo diverge do hash cadastrado.')
    duration_ms, has_audio = 0, False
    if mime.startswith('image/'):
        from PIL import Image
        with Image.open(path) as image:
            image.verify()
    else:
        from media_tools import probe
        metadata = probe(path)
        streams = metadata.get('streams', [])
        require(any(s.get('codec_type') == mime.split('/')[0] for s in streams), 'Faixa esperada ausente.')
        duration = float(metadata['format']['duration'])
        require(math.isfinite(duration) and duration > 0, 'Duração da mídia indisponível.')
        duration_ms = math.floor(duration * 1000)
        has_audio = any(s.get('codec_type') == 'audio' for s in streams)
    return {'id': row['id'], 'revision': row['revision'], 'version': row['version'],
            'sha256': row['sha256'], 'mime': mime, 'duration_ms': duration_ms, 'has_audio': has_audio}

def take_pair(snapshot, spec):
    project, episode = spec['project_id'], spec['episode_id']
    episode_row, rows = scope_rows(snapshot, project, episode)
    require(not episode_row['is_test'] or spec.get('include_test') is True, 'Âmbito de teste requer include_test.')
    takes = spec.get('takes')
    require(isinstance(takes, list) and len(takes) == 2 and len({t['id'] for t in takes}) == 2,
            'Escolha dois registros de take distintos.')
    question = spec.get('question', '').strip()
    require(bool(question), 'Informe a decisão que os takes devem esclarecer.')
    bound = []
    for take in takes:
        row = rows.get(take['id'])
        require(row and row['revision'] == take.get('revision'), 'Take fora do episódio ou revisão desatualizada.')
        bound.append(descriptor(row, local_media_path(take.get('path') or row['uri'])))
    require(bound[0]['sha256'] != bound[1]['sha256'], 'As duas mídias têm conteúdo idêntico.')
    secrets.SystemRandom().shuffle(bound)
    manifest = {'kind': 'CPE_TAKE_PAIR_1', 'pair_id': 'PAIR-' + uuid.uuid4().hex,
                'spreadsheet_id': snapshot['spreadsheet_id'], 'project_id': project, 'episode_id': episode,
                'is_test': episode_row['is_test'], 'question': question,
                'takes': dict(zip(('A', 'B'), bound))}
    return {**manifest, 'pair_sha256': manifest_hash(manifest)}

def vote_plan(snapshot, spec):
    # manifest is the agent-retained original; vote is the separately received director message.
    manifest, vote, auth = spec['manifest'], spec['vote'], spec['authorization']
    require(manifest.get('kind') == 'CPE_TAKE_PAIR_1' and vote.get('kind') == 'CPE_TAKE_VOTE_1',
            'Formato de par ou voto incompatível.')
    require(manifest['pair_sha256'] == manifest_hash(manifest) == vote.get('pair_sha256')
            and vote.get('pair_id') == manifest['pair_id'], 'O voto não corresponde ao par apresentado.')
    require(snapshot['spreadsheet_id'] == manifest['spreadsheet_id'], 'Planilha diferente da origem do par.')
    episode_row, rows = scope_rows(snapshot, manifest['project_id'], manifest['episode_id'])
    require(episode_row['is_test'] is manifest['is_test'], 'Escopo do par inválido.')
    require(not vote.get('demonstration') or manifest['is_test'], 'Um voto demonstrativo só pode ser usado em teste.')
    alternatives = manifest['takes']
    require(set(alternatives) == {'A','B'} and alternatives['A']['id'] != alternatives['B']['id'],
            'Par incompleto ou repetido.')
    for take in alternatives.values():
        current = rows.get(take['id'])
        require(current and all(take[k] == current[k] for k in ('revision','version','sha256')),
                'A versão da mídia mudou. Apresente novo par antes de salvar.')
        source = local_media_path(spec.get('paths',{}).get(take['id']) or current['uri'])
        require(source.is_file() and media_hash(source) == take['sha256'],
                'Mídia ausente ou substituída desde a apresentação do par. Confira os arquivos.')
    require(vote.get('authorized') is True and vote.get('choice') in {'A','B','TIE','BOTH_FAIL'},
            'Voto explícito necessário.')
    require(isinstance(vote.get('reason'), str) and vote['reason'].strip(), 'Motivo necessário.')
    duration = min((t['duration_ms'] for t in alternatives.values() if t['duration_ms']), default=0)
    start, mark, end = (vote.get(k) for k in ('start_ms', 'mark_ms', 'end_ms'))
    require(all(type(n) is int for n in (start, mark, end)) and 0 <= start <= mark <= end <= duration,
            'Trecho ou marca fora da duração comum dos takes.')
    scope = vote.get('preference_scope', 'deliverable')
    require(scope in {'deliverable','scene','episode','project'}, 'Escopo da preferência inválido.')
    source_shot = manifest.get('shot')
    if source_shot:
        shot = next((r for r in snapshot['tables']['Shot List'] if r['id']==source_shot['id']), None)
        require(shot and shot['episode_id']==manifest['episode_id'] and fingerprint(shot)==source_shot['sha256'],
                'A versão do plano mudou desde a apresentação.')
    if scope=='scene':
        require(source_shot and source_shot.get('scene_beat') and source_shot['scene_beat']==shot['scene_beat'],
                'Vincule a comparação a um plano da cena antes de registrar essa preferência.')
    require(auth.get('authorized') is True and auth.get('actor') and auth.get('user_message_ref'),
            'Vincule o voto à mensagem efetivamente recebida.')
    key = fingerprint([manifest['pair_id'], auth['user_message_ref']])[:28]
    pair_id, feedback_id = 'CMP-'+key, 'HF-'+key
    project, episode = manifest['project_id'], manifest['episode_id']
    common = {'project_id': project, 'episode_id': episode, 'is_test': manifest['is_test'], 'status':'DRAFT'}
    record = {'kind': 'TAKE_PREFERENCE', 'pair_sha256': manifest['pair_sha256'], 'takes': alternatives,
              'choice': vote['choice'], 'start_ms': start, 'end_ms': end, 'mark_ms': mark,
              'question': manifest['question'], 'preference_scope': scope, 'reason': vote['reason'].strip()}
    if source_shot:record['shot']=source_shot
    result = alternatives[vote['choice']]['id'] if vote['choice'] in alternatives else vote['choice']
    example_id = 'EX-'+key
    example = {**common, 'title': manifest['question'], 'kind':'TAKE_COMPARISON',
               'department':'editing', 'source_ref':manifest['pair_id'], 'expected':manifest['question'],
               'observed':canonical(alternatives), 'limitations':'Escolha relativa aos dois takes apresentados.'}
    pair = {**common, 'target_id':example_id, 'target_revision':1, 'department':'editing',
            'session_ref':manifest['pair_id'], 'reviewer_ids':auth['actor'],
            'order_results_json':canonical(record), 'outcome':result,'human_decision_ref':auth['user_message_ref'],
            'limitations':'Preferência contextual em uma apresentação. Uso do take requer aprovação própria.'}
    decision = {'A':'PREFER_A','B':'PREFER_B'}.get(vote['choice'],vote['choice'])
    feedback = {**common, 'evaluation_id':'','target_table':'Pairwise Comparisons','target_id':pair_id,
                'target_revision':1,'human_decision':decision,'user_message_ref':auth['user_message_ref'],
                'reason':vote['reason'].strip(),'evidence':canonical(record),'preference_scope':scope,
                'context':manifest['question']}
    changes = [{'table':t,'id':i,'expected_revision':None,'values':values} for t,i,values in
               [('Examples',example_id,example),('Pairwise Comparisons',pair_id,pair),('Human Feedback',feedback_id,feedback)]]
    intent = {**auth, 'op_id':'TAKE-VOTE-'+key,'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'changes':changes}
    plan=prepare(snapshot, intent)
    if spec.get('paths'):
        plan['local_take_files']={t['id']:str(local_media_path(spec['paths'].get(t['id']) or rows[t['id']]['uri']).resolve())
                                  for t in alternatives.values()}
    return plan

def verify_vote_sources(plan,snapshot):
    for change in plan['changes']:
        if change['table']!='Human Feedback':continue
        row=change['after']
        try:record=json.loads(row['evidence'])
        except (TypeError,ValueError):continue
        if not isinstance(record,dict) or record.get('kind')!='TAKE_PREFERENCE':continue
        _,assets=scope_rows(snapshot,row['project_id'],row['episode_id'])
        for source in record['takes'].values():
            asset=assets.get(source['id'])
            require(asset and all(source[k]==asset[k] for k in ('version','revision','sha256')),
                    'A versão da mídia mudou antes da gravação.')
            file=local_media_path(plan.get('local_take_files',{}).get(asset['id']) or asset['uri'])
            require(file.is_file() and media_hash(file)==asset['sha256'],
                    'A mídia foi removida ou substituída após a preparação do voto.')
