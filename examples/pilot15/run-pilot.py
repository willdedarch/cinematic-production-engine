"""Execute the original study through the local CPE commands and keep their receipts."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CLI = ROOT / 'scripts/cpe.py'
PROJECT = 'TEST-P15'
EPISODE = PROJECT + '-EP1'


def inspect_json(path):
    return json.loads(path.read_text(encoding='utf8'))


def write(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
    return path


def rehearsal_auth(operation):
    return {'authorized': True, 'actor': 'Fixture local do piloto', 'op_id': 'TEST-P15-' + operation,
            'user_message_ref': 'SYNTHETIC-P15-' + operation}


def run_study(work, media):
    work.mkdir(parents=True)
    snapshot_file = work / 'local-rehearsal-state.json'
    run_records = {}

    def call(command, spec=None, *, extra=(), should_fail=False, name=None):
        label = name or command
        args = [sys.executable, '-B', str(CLI), command, '--workspace', str(work),
                '--snapshot', str(snapshot_file), '--project', PROJECT, '--episode', EPISODE, '--include-test']
        if spec is not None:
            args += ['--input', str(write(work / (label + '-input.json'), spec))]
        done = subprocess.run(args + list(extra), capture_output=True, encoding='utf8')
        if should_fail and done.returncode == 1:
            failed = json.loads(done.stderr)
            run_records[label] = {'expected_rejection': failed['error'], 'events': failed['events']}
            return failed
        done.check_returncode()
        if should_fail:
            raise AssertionError(label + ' should have failed')
        receipt = json.loads(done.stdout)
        run_records[label] = receipt
        return inspect_json(Path(receipt['result']))

    now = datetime.now(timezone.utc).isoformat()
    schema = inspect_json(ROOT / 'schemas/shared-state.tables.json')
    write(snapshot_file, {'schema_version': '3.1.0', 'spreadsheet_id': 'LOCAL-P15-NO-GOOGLE',
                          'read_at': now, 'tables': {name: [] for name in schema['tables']}})
    initial = call('init', {'brief': {'project_id': PROJECT, 'project_name': 'A linha azul',
                                    'episode_id': EPISODE, 'episode_title': 'A mão desocupada',
                                    'target_seconds': 67, 'genre': 'Ação de guerra', 'is_test': True},
                            'authorization': rehearsal_auth('INIT')})['candidate']
    write(snapshot_file, initial)
    card = inspect_json(HERE / 'focal-card.json')
    source = inspect_json(HERE / 'focal-shot.json')

    def change(table, record_id, gate, **values):
        return {'table': table, 'id': record_id, 'expected_revision': None,
                'values': {'project_id': PROJECT, 'episode_id': EPISODE, 'is_test': True, 'gate_id': gate,
                           'version': 'pilot-1', 'status': 'DRAFT', **values}}

    changes = [
        change('Characters', 'P15-JOA', 'G7', name='Joana', identity='Funcionária adulta do terminal',
               costume='Casaco azul-petróleo com poeira na manga esquerda', performance=card['performance']),
        change('Characters', 'P15-EMA', 'G7', name='Ema', identity='Passageira adulta', costume='Colete ocre'),
        change('Characters', 'P15-BEN', 'G7', name='Bento', identity='Barqueiro adulto', costume='Gorro cinza'),
        change('Locations', 'P15-TERMINAL', 'G8', name='Terminal fluvial', geo_version='planta-1',
               anchors='Banco fixo, faixa azul, arco norte e portão leste', state='Portão leste fechado',
               light_weather=source['cinematic_plan']['lighting']),
        change('Props', 'P15-CADERNO', 'G9', name='Caderno', material_scale='Capa vermelha, bordas úmidas',
               owner_character_id='P15-JOA', state=card['in']['caderno']),
        change('Shot List', card['shot_id'], 'G10', scene_beat='Terminal fluvial', order=5,
               duration_s=card['duration_s'], purpose=card['decision'], action=card['action'],
               character_ids='P15-JOA,P15-EMA,P15-BEN', location_id='P15-TERMINAL', prop_ids='P15-CADERNO',
               camera_blocking=card['camera'], sound_edit=card['sound'],
               start_end_state=json.dumps({key: card[key] for key in ('in', 'out')}, ensure_ascii=False)),
    ]
    staged = call('prepare', {**rehearsal_auth('ASSETS'), 'at': now, 'changes': changes})
    write(snapshot_file, staged['candidate'])
    task = call('task', {'department': 'Direção', 'purpose': 'Entrega', 'problem': 'Continuidade',
                         'secondary_genres': ['Suspense'], 'scene_complexity': 'Coletiva', 'intention': card['decision']},
                extra=('--gate', 'G10', '--model', source['model_id']))
    assert 'engines/war-film.md' in task['retrieved_hashes']
    assert {'guerra', 'suspense'} <= set(task['routing']['conditions'])
    call('briefing-view')
    call('bible')
    layout = call('previs', inspect_json(HERE / 'geometry.json'))
    assert layout['geometry_valid'] and not layout['artistic_approval']
    storyboard = call('storyboard', {'episode_id': EPISODE, 'scene_beat': 'Terminal fluvial'})
    selected = call('shot-card', {'shot_id': card['shot_id']})
    assert storyboard['cards'][0]['shot'] == selected['shot']
    seedance = call('shot-handoff', {**source, 'shot': selected['shot']}, name='handoff-seedance')
    minimax = call('shot-handoff', {**source, 'shot': selected['shot'], 'model_id': 'minimax_h3',
                                   'parameters': {'duration': 8}}, name='handoff-minimax')
    assert seedance['production_brief']['model_neutral_prompt'] == minimax['production_brief']['model_neutral_prompt']
    assert seedance['handoff_sha256'] != minimax['handoff_sha256']
    assert len(seedance['production_brief']['entities']) == 5
    evidence = {'seedance_sha256': seedance['handoff_sha256'], 'minimax_sha256': minimax['handoff_sha256'],
                'resolved_shot': selected['shot'], 'route': task['routing'], 'media_comparisons': []}

    missing = ROOT / 'examples/series-worked/SH06-previs.mp4'
    invalid = call('shot-compare', {'handoff': seedance, 'path': str(missing), 'rights_confirmed': True}, name='compare-unrelated')
    assert invalid['technical_review'] in {'MISMATCH', 'UNAVAILABLE'} and not invalid['approved']
    evidence['media_comparisons'].append(invalid)
    if media:
        good = call('shot-compare', {'handoff': seedance, 'path': str(media), 'rights_confirmed': True}, name='compare-original')
        assert good['technical_review'] in {'SPEC_CHECKED', 'INCOMPLETE', 'UNAVAILABLE'} and not good['approved']
        evidence['media_comparisons'].append(good)
        call('inspect', extra=('--source', str(media), '--max-seconds', '8', '--sample-fps', '1'))
        import_request = {'handoff': seedance, 'shot': seedance['shot'], 'path': str(media),
            'asset_id': 'P15-SH05-ANIMATIC', 'kind': 'NARRATIVE_PREVIS', 'origin': 'Bloqueio esquemático autoral local',
            'rights_confirmed': True, 'rights': 'Autoral, para demonstração', 'decision_id': 'P15-RETURN-PROVENANCE',
            'reason': 'Material recebido para conferência técnica e revisão de direção',
            'authorization': rehearsal_auth('RETURN')}
        if invalid['technical_review']=='MISMATCH':
            wrong = call('shot-import', {**import_request, 'path':str(missing)}, should_fail=True, name='import-unrelated')
            assert 'differs from the handoff' in wrong['error']
        imported = call('shot-import', import_request)
        assert imported['kind'] == 'WRITE_PLAN_NOT_SAVED'
        assert imported['changes'][0]['after']['status'] == 'REVIEW_REQUIRED'
        evidence['return_provenance'] = imported['return_provenance']
        evidence['import_planned_only'] = True
        before_review = inspect_json(snapshot_file)
        write(snapshot_file, imported['candidate'])
        try:
            review = call('judge', {'department':'direction',
                'target':{'id':import_request['asset_id'],'revision':1,'path':str(media)},
                'context':{'genre':'Ação de guerra','intention':card['decision'],'format':'prévia esquemática'},
            })
        finally:
            write(snapshot_file, before_review)
        assert review['kind']=='REVIEW_PACKET_NOT_JUDGED' and review['observed_quality'] is None
    correction = call('revise', {'round':0,'max_rounds':2,'changed_elements':['ênfase do olhar'],
                               'protected_elements':['eixo','estado final do caderno']})
    assert not correction['auto_approve']
    checkpoint = call('checkpoint')
    recovered = call('recover', inspect_json(Path(checkpoint['checkpoint'])))
    assert recovered['status'] == 'MATCHES_CURRENT_READ_COPY'
    evidence.update(recovery=recovered['status'], paid_credits=0, remote_writes=0, artistic_approval=False)
    return write(work / 'pilot-receipt.json', {**evidence, 'local_runs': run_records})


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workspace', type=Path, required=True, help='New directory outside the package')
    parser.add_argument('--media', type=Path, default=HERE/'SH05-animatic.mp4', help='Authorized local 8-second schematic')
    args = parser.parse_args()
    print(run_study(args.workspace.resolve(), args.media.resolve() if args.media else None))
