"""Translate an optional authored beat plan while checking temporal and reference identity."""
import math


class PlanError(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise PlanError(message)


def finite_number(value):
    return type(value) in (int, float) and math.isfinite(value)


def compile_plan(plan, model, parameters, references):
    require(isinstance(plan, dict), 'Cinematic plan must be an object')
    require(set(plan) <= {'objective', 'space', 'cast', 'beats', 'protected', 'duration_s'},
            'Unknown cinematic plan field')
    require(model['output_type'] == 'video', 'A timed plan needs a video model')
    duration = plan.get('duration_s', parameters.get('duration'))
    require(finite_number(duration) and duration > 0, 'Provide a positive planned duration')
    native_duration = parameters.get('duration')
    require(native_duration is None or duration == native_duration, 'Plan and native duration differ')
    cast = plan.get('cast', {})
    require(isinstance(cast, dict) and cast and
            all(isinstance(k, str) and k.strip() and isinstance(v, str) and v.strip() for k, v in cast.items()),
            'Name the people or subjects in this shot')
    for field in ('objective', 'space', 'protected'):
        require(isinstance(plan.get(field, ''), str), 'Plan text must be text')
    beats = plan.get('beats')
    require(isinstance(beats, list) and beats, 'Provide the authored beats')
    known_refs = {item['id'] for item in references}
    previous_end = 0
    state = {}
    seen = set()
    lines = []
    for field, label in [('objective', 'Intenção'), ('space', 'Espaço')]:
        if plan.get(field, '').strip():
            lines.append(label + ' — ' + plan[field].strip())
    lines.append('Pessoas — ' + ' / '.join(key + ' = ' + value for key, value in cast.items()))
    warnings = []
    for beat in beats:
        require(isinstance(beat, dict) and set(beat) <= {
            'id', 'start_s', 'end_s', 'subjects', 'action', 'performance', 'attention', 'camera',
            'sound', 'entry', 'exit', 'references', 'continuity_exception'},
            'Unknown beat field')
        identifier = beat.get('id')
        require(isinstance(identifier, str) and identifier.strip() and identifier not in seen,
                'Every beat needs a unique identity')
        seen.add(identifier)
        start, end = beat.get('start_s'), beat.get('end_s')
        require(finite_number(start) and finite_number(end) and
                0 <= start < end <= duration and start >= previous_end,
                'Beat times overlap or exceed the planned duration')
        if start > previous_end:
            warnings.append(identifier + ' leaves an interval with no authored action')
        previous_end = end
        subjects = beat.get('subjects', [])
        require(isinstance(subjects, list) and subjects and all(isinstance(subject,str) for subject in subjects) and
                len(subjects) == len(set(subjects)) and all(subject in cast for subject in subjects),
                'A beat references an unknown or repeated subject')
        require(isinstance(beat.get('action'), str) and beat['action'].strip(),
                'Describe an observable action')
        attached = beat.get('references', [])
        require(isinstance(attached, list) and all(isinstance(r, str) and r in known_refs for r in attached),
                'A beat references material outside the attachment manifest')
        entry, exit_state = beat.get('entry', {}), beat.get('exit', {})
        for states in (entry, exit_state):
            require(isinstance(states, dict) and all(isinstance(k, str) and k.strip() and
                    isinstance(v, str) and v.strip() for k, v in states.items()), 'State must use named textual facts')
        exception = beat.get('continuity_exception', '')
        require(isinstance(exception, str), 'A continuity exception must name its authored reason')
        changed = [key for key, value in entry.items() if key in state and state[key] != value]
        require(not changed or exception.strip(), 'Unexplained state jump before ' + identifier)
        if changed:
            warnings.append(identifier + ' has an authored continuity exception requiring director review')
        state.update(entry)
        state.update(exit_state)
        lines.append(f'{start:g}–{end:g} s · {identifier} · ' + ', '.join(cast[s] for s in subjects))
        for field, label in [('action', 'Ação'), ('performance', 'Atuação'), ('attention', 'Atenção'),
                             ('camera', 'Câmera'), ('sound', 'Som')]:
            value = beat.get(field, '')
            require(isinstance(value, str), 'Beat directions must be text')
            if value.strip():
                lines.append(label + ' — ' + value.strip())
        for label, values in [('Entrada', entry), ('Saída', exit_state)]:
            if values:
                lines.append(label + ' — ' + ' / '.join(key + ' = ' + value for key, value in values.items()))
        if attached:
            lines.append('Referências anexadas — ' + ', '.join(attached))
    if previous_end < duration:
        warnings.append('The end of the planned shot has no authored action')
    if plan.get('protected', '').strip():
        lines.append('Preservar — ' + plan['protected'].strip())
    warnings.append('Beat timing and text are editorial requests; adherence requires viewing the returned video')
    return '\n'.join(lines), warnings
