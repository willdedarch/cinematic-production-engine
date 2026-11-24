#!/usr/bin/env python3
"""Resolve the reading route, with evidence of the files actually retrieved."""
import argparse
import hashlib
import json
from pathlib import Path

from knowledge_select import matching_genre_cases, words

ROOT = Path(__file__).resolve().parents[1]
ROUTER = json.loads((ROOT / 'orchestration/knowledge-router.json').read_text(encoding='utf-8'))
ALIASES = {
    'department': {'roteiro':'screenplay', 'direção':'direction', 'fotografia':'cinematography',
                   'direção de fotografia':'cinematography', 'arte':'art', 'elenco':'casting',
                   'montagem':'editing', 'som':'sound', 'continuidade':'continuity'},
    'purpose': {'pré-visualização':'previs', 'entrega':'handoff', 'comparar':'compare',
                'controle de qualidade':'qc', 'revisão':'revise'},
    'deliverable': {'storyboard':'previs', 'planta':'previs', 'cinematic plan':'handoff',
                    'plano cinematográfico':'handoff', 'pacote manual':'handoff', 'comparação de takes':'compare',
                    'relatório de controle de qualidade':'qc', 'reparo':'revise'},
    'problem': {'continuidade':'continuity', 'espaço':'spatial', 'atuação':'performance',
                'materiais':'materials', 'som':'sound'},
    'scene_complexity': {'simples':'simple', 'complexa':'complex', 'coletiva':'complex'},
    'facet': {'fotografia':'optics', 'óptica':'optics', 'composição':'composition', 'luz':'light',
              'encenação':'direction', 'atuação':'performance', 'continuidade':'continuity',
              'som':'sound', 'laboratório':'laboratory', 'guerra':'war', 'montagem':'continuity',
              'narrativa':'narrative', 'mídia':'media'},
}
COMPLEXITY = {'simple': [], 'complex': ['composition', 'performance', 'continuity']}
WAR_PILOT = {'G2':'README.md', 'G3':'roteiro.md', 'G4':'roteiro.md', 'G5':'direcao-e-decupagem.md',
             'G7':'direcao-e-decupagem.md', 'G8':'direcao-e-decupagem.md', 'G9':'direcao-e-decupagem.md',
             'G10':'focal-shot.json', 'G13':'revisao-e-estudos.md', 'G14':'revisao-e-estudos.md'}


def canonical_selector(kind, value, options):
    if isinstance(value, str) and (target := words(value)):
        for label, key in {**{key:key for key in options}, **ALIASES[kind]}.items():
            if words(label) == target:
                return key
    raise ValueError('Unknown knowledge ' + kind)


def route(command, conditions=(), *, facets=(), model_id='', department='', purpose='', problem='', scene_complexity='', deliverable=''):
    key = ROUTER['commands'].get(command.upper(), command.upper())
    if key not in ROUTER['gates']:
        raise ValueError('Resolve current eligible gate from fresh state first')

    gate = ROUTER['gates'][key]
    active = []
    for condition in conditions:
        name = condition.strip().casefold()
        if name in ROUTER['conditions']:
            active.append(name)
        else:
            active.extend(case['genre'] for case in matching_genre_cases(name)
                          if case['genre'] in ROUTER['conditions'])
    active = list(dict.fromkeys(active))

    selected_facets = [canonical_selector('facet', value, ROUTER['facets']) for value in facets]
    canonical = {}
    for selector, value in (('department', department), ('purpose', purpose), ('problem', problem), ('deliverable', deliverable),
                            ('scene_complexity', scene_complexity)):
        if not value:
            continue
        options = COMPLEXITY if selector == 'scene_complexity' else ROUTER['selectors']['purpose' if selector == 'deliverable' else selector]
        canonical[selector] = canonical_selector(selector, value, options)
        selected_facets.extend(options[canonical[selector]])
    selected_facets = list(dict.fromkeys(selected_facets))

    examples = [ROUTER['genre_examples'].get(condition, {}).get(key) for condition in active]
    examples = [path for path in examples if path] or [gate['example']]
    if 'guerra' in active and key in WAR_PILOT:
        examples.append('examples/pilot15/' + WAR_PILOT[key])
    paths = ROUTER['always'] + gate['read'] + examples
    for condition in active:
        paths.extend(ROUTER['conditions'][condition])
    for facet in selected_facets:
        if facet not in ROUTER['facets']:
            raise ValueError('Unknown knowledge facet')
        paths.extend(ROUTER['facets'][facet])
    if set(selected_facets) & {'direction', 'performance', 'composition', 'light', 'continuity', 'sound', 'prompts'}:
        paths.extend(['references/professional-methods-1.5.md','references/professional-study-cards-1.5.json'])

    model_example = ROUTER['model_examples'].get(model_id)
    if model_example and (key == 'G10' or 'prompts' in selected_facets):
        paths.append(model_example)
        examples.append(model_example)

    loaded = []
    for name in dict.fromkeys(paths):
        file = (ROOT / name).resolve()
        if not file.is_relative_to(ROOT) or not file.is_file():
            raise ValueError('Missing/outside route: ' + name)
        data = file.read_bytes()
        loaded.append({'file': name, 'sha256': hashlib.sha256(data).hexdigest(), 'text': data.decode('utf-8')})

    return {'gate': key, 'panel': gate['panel'], 'loaded': loaded,
            'selection': {'conditions': active, 'facets': selected_facets, 'examples': examples, 'selectors': canonical}}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('command')
    parser.add_argument('--condition', action='append', default=[])
    parser.add_argument('--facet', action='append', default=[])
    parser.add_argument('--model', default='')
    parser.add_argument('--department', default='')
    parser.add_argument('--purpose', default='')
    parser.add_argument('--problem', default='')
    parser.add_argument('--scene-complexity', default='')
    parser.add_argument('--deliverable', default='')
    args = parser.parse_args()
    result = route(args.command, args.condition, facets=args.facet, model_id=args.model,
                   department=args.department, purpose=args.purpose, problem=args.problem, scene_complexity=args.scene_complexity,
                   deliverable=args.deliverable)
    print(json.dumps(result, ensure_ascii=False, indent=2))
