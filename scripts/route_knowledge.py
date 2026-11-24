#!/usr/bin/env python3
"""Resolve the reading route, with evidence of the files actually retrieved."""
import argparse
import hashlib
import json
from pathlib import Path

from knowledge_select import matching_genre_cases

ROOT = Path(__file__).resolve().parents[1]
ROUTER = json.loads((ROOT / 'orchestration/knowledge-router.json').read_text(encoding='utf-8'))


def route(command, conditions=(), *, facets=(), model_id='', department='', purpose='', problem=''):
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

    selected_facets = list(facets)
    for selector, value in (('department', department), ('purpose', purpose), ('problem', problem)):
        if not value:
            continue
        options = ROUTER['selectors'][selector]
        if not isinstance(value, str) or value not in options:
            raise ValueError('Unknown knowledge ' + selector)
        selected_facets.extend(options[value])
    selected_facets = list(dict.fromkeys(selected_facets))

    examples = [ROUTER['genre_examples'].get(condition, {}).get(key) for condition in active]
    examples = [path for path in examples if path] or [gate['example']]
    paths = ROUTER['always'] + gate['read'] + examples
    for condition in active:
        paths.extend(ROUTER['conditions'][condition])
    for facet in selected_facets:
        if facet not in ROUTER['facets']:
            raise ValueError('Unknown knowledge facet')
        paths.extend(ROUTER['facets'][facet])

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
            'selection': {'conditions': active, 'facets': selected_facets, 'examples': examples}}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('command')
    parser.add_argument('--condition', action='append', default=[])
    parser.add_argument('--facet', action='append', default=[])
    parser.add_argument('--model', default='')
    parser.add_argument('--department', default='')
    parser.add_argument('--purpose', default='')
    parser.add_argument('--problem', default='')
    args = parser.parse_args()
    result = route(args.command, args.condition, facets=args.facet, model_id=args.model,
                   department=args.department, purpose=args.purpose, problem=args.problem)
    print(json.dumps(result, ensure_ascii=False, indent=2))
