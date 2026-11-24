#!/usr/bin/env python3
"""Resolve the reading route, with evidence of the files actually retrieved."""
import argparse
import hashlib
import json
from pathlib import Path

from knowledge_select import canonical_genres, classify_intention, genre_cards, genre_catalog, tokens, words

ROOT = Path(__file__).resolve().parents[1]
ROUTER = json.loads((ROOT / 'orchestration/knowledge-router.json').read_text(encoding='utf-8'))
ALIASES = {
    'department': {'roteiro':'screenplay', 'direção':'direction', 'fotografia':'cinematography',
                   'direção de fotografia':'cinematography', 'arte':'art', 'elenco':'casting',
                   'montagem':'editing', 'som':'sound', 'continuidade':'continuity', 'história':'story',
                   'personagem':'story', 'retenção':'retention', 'atenção':'retention'},
    'purpose': {'pré-visualização':'previs', 'entrega':'handoff', 'comparar':'compare',
                'controle de qualidade':'qc', 'revisão':'revise', 'análise':'analysis', 'analisar':'analysis'},
    'deliverable': {'storyboard':'previs', 'planta':'previs', 'cinematic plan':'handoff',
                    'plano cinematográfico':'handoff', 'pacote manual':'handoff', 'comparação de takes':'compare',
                    'relatório de controle de qualidade':'qc', 'reparo':'revise'},
    'problem': {'continuidade':'continuity', 'espaço':'spatial', 'atuação':'performance',
                'materiais':'materials', 'som':'sound'},
    'scene_complexity': {'simples':'simple', 'complexa':'complex', 'coletiva':'complex'},
    'facet': {'fotografia':'optics', 'óptica':'optics', 'composição':'composition', 'luz':'light',
              'encenação':'direction', 'atuação':'performance', 'continuidade':'continuity',
              'som':'sound', 'laboratório':'laboratory', 'guerra':'war', 'montagem':'continuity',
              'narrativa':'narrative', 'mídia':'media', 'retenção':'attention', 'atenção':'attention',
              'personagem':'character', 'personagens':'character'},
}
COMPLEXITY = {'simple': [], 'complex': ['composition', 'performance', 'continuity']}
WAR_PILOT = {'G2':'README.md', 'G3':'roteiro.md', 'G4':'roteiro.md', 'G5':'direcao-e-decupagem.md',
             'G7':'direcao-e-decupagem.md', 'G8':'direcao-e-decupagem.md', 'G9':'direcao-e-decupagem.md',
             'G10':'focal-shot.json', 'G13':'revisao-e-estudos.md', 'G14':'revisao-e-estudos.md'}
ACTION_STUDY = 'examples/action-study/README.md'
VIDEO_MODELS = {'seedance_2_5', 'minimax_h3', 'wan2_7', 'kling3_0_turbo'}
GATE_RUBRICS = {'G1':('story',), 'G2':('story',), 'G3':('emotion','suspense'), 'G4':('screenplay','dialogue'),
                'G5':('direction','photography'), 'G6':('wardrobe','props'), 'G7':('casting','performance'),
                'G8':('locations','geometry'), 'G9':('props',), 'G10':('shot-design','prompts'),
                'G11':('composition','lighting'), 'G12':('continuity',), 'G13':('editing','sound'),
                'G14':('continuity',)}
DEPARTMENT_RUBRIC = {'cinematography':'photography', 'art':'composition'}


def canonical_selector(kind, value, options):
    if isinstance(value, str) and (target := words(value)):
        for label, key in {**{key:key for key in options}, **ALIASES[kind]}.items():
            if words(label) == target:
                return key
    raise ValueError('Unknown knowledge ' + kind)


def route(command, conditions=(), *, facets=(), model_id='', department='', purpose='', problem='', scene_complexity='',
          deliverable='', intention='', creative_profile=''):
    command_key = ' '.join(tokens(command)).upper()
    key = ROUTER['commands'].get(command_key, command_key)
    if key not in ROUTER['gates']:
        raise ValueError('Resolve current eligible gate from fresh state first')

    gate = ROUTER['gates'][key]
    conditions = tuple(conditions)
    genres = canonical_genres(conditions)
    special_conditions = [label.strip().casefold() for label in conditions
                          if label.strip().casefold() in ROUTER['conditions']]
    active = list(dict.fromkeys([*genres,*special_conditions]))
    mode = classify_intention(genres, intention, creative_profile)
    action_first = mode == 'action_led_war'
    catalog = genre_catalog()
    profiles = [catalog[genre] for genre in genres]
    cards = genre_cards(genres, action_first=action_first)
    primary = next((card for card in cards if card['case_id']=='WAR-ACTION-16'),cards[0] if cards else None)
    war_study_relevant = (not action_first and 'guerra' in genres and
                          (bool({'sobrevivência','suspense'} & set(genres)) or
                           bool(words(intention) & {'evacuacao','travessia','partilha','cuidado','escassez','evacuation','survival'})))

    selected_facets = list(ROUTER.get('command_facets',{}).get(command_key,()))
    selected_facets.extend(canonical_selector('facet', value, ROUTER['facets']) for value in facets)
    canonical = {}
    for selector, value in (('department', department), ('purpose', purpose), ('problem', problem), ('deliverable', deliverable),
                            ('scene_complexity', scene_complexity)):
        if not value:
            continue
        options = COMPLEXITY if selector == 'scene_complexity' else ROUTER['selectors']['purpose' if selector == 'deliverable' else selector]
        canonical[selector] = canonical_selector(selector, value, options)
        selected_facets.extend(options[canonical[selector]])
    selected_facets = list(dict.fromkeys(selected_facets))

    if action_first:
        examples = [ACTION_STUDY]
        if key == 'G10' and model_id in VIDEO_MODELS:
            examples.append('examples/action-study/focal-shot.json')
    else:
        examples = [ROUTER['genre_examples'].get(condition, {}).get(key) for condition in genres
                    if condition != 'guerra' or war_study_relevant]
        examples = [path for path in examples if path] or [gate['example']]
    if war_study_relevant and key in WAR_PILOT:
        examples.append('examples/pilot15/' + WAR_PILOT[key])
    paths = ROUTER['always'] + gate['read'] + examples
    for condition in active:
        paths.extend(ROUTER['conditions'].get(condition, ()))
    for profile in profiles:
        paths.extend(profile['specialization'])
    for facet in selected_facets:
        if facet not in ROUTER['facets']:
            raise ValueError('Unknown knowledge facet')
        paths.extend(ROUTER['facets'][facet])
    if set(selected_facets) & {'direction', 'performance', 'composition', 'light', 'continuity', 'sound', 'prompts'}:
        paths.extend(['references/professional-methods-1.5.md','references/professional-study-cards-1.5.json'])

    model_example = ROUTER['model_examples'].get(model_id)
    if not action_first and model_example and (key == 'G10' or 'prompts' in selected_facets):
        paths.append(model_example)
        examples.append(model_example)

    loaded = []
    for name in dict.fromkeys(paths):
        file = (ROOT / name).resolve()
        if not file.is_relative_to(ROOT) or not file.is_file():
            raise ValueError('Missing/outside route: ' + name)
        data = file.read_bytes()
        loaded.append({'file': name, 'sha256': hashlib.sha256(data).hexdigest(), 'text': data.decode('utf-8')})

    department_key = canonical.get('department','')
    rubric_keys = [DEPARTMENT_RUBRIC.get(department_key,department_key),*GATE_RUBRICS.get(key,())]
    if 'attention' in selected_facets:
        rubric_keys.insert(0,'retention')
    for profile in profiles:
        rubric_keys.extend(profile['rubrics'])
    data = json.loads((ROOT/'judgment-engine/rubrics.json').read_text(encoding='utf-8'))['rubrics']
    by_department = {rubric['department']: rubric for rubric in data}
    rubrics = [by_department[department_key] for department_key in dict.fromkeys(rubric_keys)
               if department_key in by_department]

    return {'gate': key, 'panel': gate['panel'], 'loaded': loaded,
            'genre_case':primary,'genre_profiles':profiles,'genre_cards':cards,'rubrics':rubrics,
            'selection': {'conditions': active, 'facets': selected_facets, 'examples': examples, 'selectors': canonical,
                          'genres':genres,'primary_genre':genres[0] if genres else None,'secondary_genres':genres[1:],
                          'example_ids':[card['case_id'] for card in cards],
                          'intent_mode':mode,'war_study_relevant':war_study_relevant}}


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
    parser.add_argument('--intention', default='')
    parser.add_argument('--creative-profile', default='')
    args = parser.parse_args()
    result = route(args.command, args.condition, facets=args.facet, model_id=args.model,
                   department=args.department, purpose=args.purpose, problem=args.problem, scene_complexity=args.scene_complexity,
                   deliverable=args.deliverable, intention=args.intention, creative_profile=args.creative_profile)
    print(json.dumps(result, ensure_ascii=False, indent=2))
