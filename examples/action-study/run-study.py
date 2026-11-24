"""Rehearse the shipped fictional study through the official CPE CLI using local test state."""
import argparse
from datetime import datetime, timezone
import itertools
import json
from pathlib import Path
import shutil
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CLI = ROOT / 'scripts/cpe.py'
PROJECT = 'TEST-ACTION-STUDY'
EPISODE = PROJECT + '-EP1'
SCENE = 'Observatório ficcional'


def load(path):
    return json.loads(path.read_text(encoding='utf8'))


def write(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
    return path


def timestamp():
    return datetime.now(timezone.utc).isoformat()


def fixture_auth(operation):
    actor = 'Ensaio local sintético'
    return {'authorized': True, 'actor': actor, 'op_id': PROJECT + '-' + operation,
            'user_message_ref': 'SYNTHETIC-ACTION-STUDY-' + operation}


def draft(table, record_id, gate, **values):
    return {'table': table, 'id': record_id, 'expected_revision': None,
            'values': {'project_id': PROJECT, 'episode_id': EPISODE, 'is_test': True,
                       'gate_id': gate, 'version': 'estudo-1', 'status': 'DRAFT', **values}}


def stage_material(fixture, focal, geometry):
    plan = focal['cinematic_plan']
    changes = [
        draft('Screenplays', 'FREQ-SCRIPT', 'G4', title='A última frequência',
              text_or_ref=(HERE / 'roteiro.md').read_text(encoding='utf8'),
              source_refs='Material autoral ficcional do estudo'),
        draft('Locations', 'FREQ-OBSERVATORIO', 'G8', name=SCENE, geo_version=geometry['id'],
              anchors='Fachada leste, parede norte, passadiço, console e borda de piso',
              dimensions='12,8 × 9,2 × 5,4 m', light_weather=plan['lighting']),
        draft('Props', 'FREQ-FITA', 'G9', name='Fita com etiqueta branca', owner_character_id='FREQ-IARA',
              material_scale='Fita portátil em capa com nomes e carimbo', state='Mão esquerda de Iara no plano focal'),
    ]
    for character, name in [('IARA', 'Iara'), ('ABEL', 'Abel'), ('DARO', 'Daro')]:
        changes.append(draft('Characters', 'FREQ-' + character, 'G7', name=name,
                             identity=plan['cast'][character], performance='Ver direção e decupagem do estudo'))
    incoming = {'ambiente': 'fachada sombreia o salão'}
    for order, (shot_id, entries) in enumerate(itertools.groupby(fixture['events'], key=lambda item: item['shot_id']), 1):
        events = list(entries)
        is_focal = shot_id == focal['shot_id']
        outgoing = {'mudanca': events[-1]['consequence']}
        if shot_id == 'SA07':
            outgoing = plan['beats'][0]['entry']
        if is_focal:
            outgoing = plan['beats'][-1]['exit']
        changes.append(draft('Shot List', shot_id, 'G10', scene_beat=SCENE, order=order,
                             duration_s=events[-1]['end_s'] - events[0]['start_s'],
                             purpose=plan['objective'] if is_focal else events[-1]['consequence'],
                             action=' '.join(event['action'] for event in events),
                             character_ids='FREQ-IARA,FREQ-ABEL,FREQ-DARO' if is_focal else '',
                             location_id='FREQ-OBSERVATORIO', prop_ids='FREQ-FITA' if is_focal else '',
                             camera_blocking=plan['composition'] if is_focal else 'Ver storyboard e decupagem',
                             sound_edit=' '.join(beat['sound'] for beat in plan['beats']) if is_focal else 'Ver mapa sonoro',
                             start_end_state=json.dumps({'in': incoming, 'out': outgoing}, ensure_ascii=False)))
        incoming = outgoing
    return changes


def make_control(destination):
    from animatic import frame, WIDTH, HEIGHT, FPS

    ffmpeg = shutil.which('ffmpeg')
    if ffmpeg is None or shutil.which('ffprobe') is None:
        return None
    with destination.with_suffix('.ffmpeg.log').open('wb') as log:
        args = [ffmpeg, '-hide_banner', '-loglevel', 'error', '-n', '-f', 'rawvideo', '-pix_fmt', 'rgb24',
                '-s', f'{WIDTH}x{HEIGHT}', '-framerate', str(FPS), '-i', 'pipe:0', '-f', 'lavfi',
                '-i', 'sine=frequency=660:duration=12', '-t', '12', '-vf', 'setsar=1',
                '-af', "volume='if(lt(mod(t,4),0.18),0.15,0)':eval=frame", '-c:v', 'libx264',
                '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-movflags', '+faststart', str(destination)]
        with subprocess.Popen(args, stdin=subprocess.PIPE, stdout=log, stderr=log) as process:
            try:
                for number in range(FPS * 12):
                    process.stdin.write(frame(number / FPS).tobytes())
            except BrokenPipeError as error:
                raise RuntimeError('FFmpeg interrompeu a leitura do controle') from error
            finally:
                process.stdin.close()
            if process.wait(timeout=45):
                raise RuntimeError('FFmpeg falhou ao produzir o controle local')
    return destination


def run_study(work, *, control=True):
    if work.is_relative_to(ROOT):
        raise ValueError('Escolha uma pasta nova fora da instalação')
    work.mkdir(parents=True)
    snapshot = work / 'local-study-state.json'
    operations = {}

    def cli(command, spec=None, *, extra=(), label=None, expected_error=None):
        name = label or command
        args = [sys.executable, '-B', str(CLI), command, '--workspace', str(work), '--snapshot', str(snapshot),
                '--project', PROJECT, '--episode', EPISODE, '--include-test']
        if spec is not None:
            args += ['--input', str(write(work / (name + '-input.json'), spec))]
        result = subprocess.run(args + list(extra), capture_output=True, encoding='utf8')
        if expected_error:
            if result.returncode != 1 or expected_error not in result.stderr:
                raise AssertionError(name + ' expected rejection: ' + result.stdout + result.stderr)
            failure = json.loads(result.stderr)
            operations[name] = {'expected_rejection': failure['error'], 'events': failure['events']}
            return failure
        if result.returncode != 0:
            raise RuntimeError(name + ': ' + result.stderr.strip())
        receipt = json.loads(result.stdout)
        operations[name] = receipt
        return load(Path(receipt['result']))

    schema = load(ROOT / 'schemas/shared-state.tables.json')
    write(snapshot, {'schema_version': '3.1.0', 'spreadsheet_id': 'LOCAL-ACTION-STUDY-NO-GOOGLE',
                     'read_at': timestamp(), 'tables': {table: [] for table in schema['tables']}})
    fixture = load(HERE / 'episode-intent.json')
    focal = load(HERE / 'focal-shot.json')
    geometry = load(HERE / 'geometry.json')
    measured = cli('intent-audit', fixture)
    assert (measured['duration_s'], measured['action_s'], measured['story_s']) == (100, 65, 35)
    initial = cli('init', {'brief': {'project_id': PROJECT, 'project_name': 'A última frequência',
                                    'episode_id': EPISODE, 'episode_title': 'A última frequência',
                                    'target_seconds': 100, 'aspect_ratio': '16:9', 'genre': 'Ação de guerra', 'is_test': True},
                           'authorization': fixture_auth('INIT')})
    write(snapshot, initial['candidate'])
    cli('briefing-view')
    intent = cli('intent-plan', {**fixture, 'project_id': PROJECT, 'episode_id': EPISODE,
                                'decision_id': 'FREQ-INTENT', 'authorization': fixture_auth('INTENT'),
                                'reason': 'Contrato sintético do exercício local. Sem decisão artística do diretor.'})
    write(snapshot, intent['candidate'])
    staged = cli('prepare', {**fixture_auth('ASSETS'), 'at': timestamp(),
                            'changes': stage_material(fixture, focal, geometry)})
    write(snapshot, staged['candidate'])
    retrieved = cli('task', {'department': 'Direção', 'purpose': 'Entrega', 'problem': 'Continuidade',
                             'secondary_genres': ['Suspense'], 'scene_complexity': 'Coletiva',
                             'intention': 'Ação visível com consequências corporais e espaciais.'},
                    extra=('--gate', 'G10', '--model', focal['model_id']))
    assert 'engines/war-film.md' in retrieved['retrieved_hashes']
    assert retrieved['routing']['intent_mode'] == 'action_led_war'
    assert retrieved['routing']['examples'][0] == 'examples/action-study/README.md'
    board = cli('storyboard', {'episode_id': EPISODE, 'scene_beat': SCENE})
    assert len(board['cards']) == 12 and all(not row['continuity_review'] for row in board['cards'])
    card = cli('shot-card', {'shot_id': 'SA08'})
    request = {**focal, 'shot': card['shot']}
    seedance = cli('shot-handoff', request, label='handoff-seedance')
    minimax = cli('shot-handoff', {**request, 'model_id': 'minimax_h3', 'parameters': {'duration': 12}},
                  label='handoff-minimax')
    expected = ['FREQ-E08A', 'FREQ-E08B', 'FREQ-E08C']
    assert seedance['creative_intent'] == minimax['creative_intent']
    assert [event['id'] for event in seedance['creative_intent']['events']] == expected
    assert seedance['production_brief']['model_neutral_prompt'] == minimax['production_brief']['model_neutral_prompt']
    for name, packet in [('seedance', seedance), ('minimax', minimax)]:
        prompt = packet['delivery']['prompt']
        assert all(identifier in prompt for identifier in expected)
        (work / ('SA08-' + name + '.txt')).write_text(prompt + '\n', encoding='utf8')
    (work / 'SA08-master.txt').write_text(seedance['production_brief']['model_neutral_prompt'] + '\n', encoding='utf8')

    changed_plan = {**focal['cinematic_plan'], 'beats': [dict(beat) for beat in focal['cinematic_plan']['beats']]}
    changed_plan['beats'][0].pop('event_ids')
    cli('shot-handoff', {**request, 'cinematic_plan': changed_plan}, label='reject-missing-event',
        expected_error='Shot omits approved event FREQ-E08A')

    control_status = 'SKIPPED'
    if control:
        if shutil.which('ffmpeg') is None or shutil.which('ffprobe') is None:
            control_status = 'TOOLS_UNAVAILABLE'
        else:
            import importlib.util
            if importlib.util.find_spec('PIL') is None or importlib.util.find_spec('numpy') is None:
                control_status = 'PREVIS_DEPENDENCIES_UNAVAILABLE'
            else:
                layout = cli('previs', geometry)
                assert layout['geometry_valid'] and not layout['artistic_approval']
                media = make_control(work / 'SA08-controle-tecnico.mp4')
                compare = cli('shot-compare', {'handoff': seedance, 'path': str(media), 'rights_confirmed': True})
                assert compare['technical_review'] == 'SPEC_CHECKED' and not compare['approved']
                imported = cli('shot-import', {'handoff': seedance, 'shot': card['shot'], 'path': str(media),
                    'asset_id': 'FREQ-SA08-CONTROL', 'kind': 'TECHNICAL_PREVIS', 'origin': 'Prévia esquemática autoral com sinal de teste',
                    'rights_confirmed': True, 'rights': 'Material autoral do estudo', 'decision_id': 'FREQ-CONTROL-RETURN',
                    'reason': 'Comprovar o percurso técnico. Os volumes são marcações de encenação.',
                    'authorization': fixture_auth('RETURN')})
                assert imported['kind'] == 'WRITE_PLAN_NOT_SAVED' and imported['changes'][0]['after']['status'] == 'REVIEW_REQUIRED'
                write(snapshot, imported['candidate'])
                control_status = 'TECHNICAL_CONTROL_IMPORTED_IN_LOCAL_COPY'

    scope = {'project_id': PROJECT, 'episode_id': EPISODE, 'shot_id': 'SA08'}
    pin = seedance['creative_intent']['decision']
    pending = cli('intent-review', {**scope, 'observations': {'decision': pin, 'events': []}}, label='review-art-pending')
    negative = cli('intent-review', {**scope, 'observations': {'decision': pin, 'events': [{
        'id': 'FREQ-E08A', 'status': 'AUDIBLE_ONLY', 'evidence_ref': 'Controle negativo textual: 0–4 s do SA08'}]}},
        label='review-art-reject-offscreen')
    assert pending['outcome'] == 'UNKNOWN' and negative['outcome'] == 'REJECT' and not negative['approved']
    checkpoint = cli('checkpoint')
    recovered = cli('recover', load(Path(checkpoint['checkpoint'])))
    assert recovered['status'] == 'MATCHES_CURRENT_READ_COPY'
    return write(work / 'study-receipt.json', {'timeline': measured, 'focal': expected, 'models': [
        seedance['delivery']['model_id'], minimax['delivery']['model_id']], 'retrieved': retrieved['routing'],
        'technical_control': control_status, 'recovery': recovered['status'], 'artistic_approval': False,
        'external_generation': False, 'remote_writes': 0, 'local_runs': operations})


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workspace', type=Path, required=True, help='Pasta de trabalho nova fora do pacote')
    parser.add_argument('--no-control', action='store_true', help='Pular o controle audiovisual local')
    args = parser.parse_args()
    print(run_study(args.workspace.resolve(), control=not args.no_control))
