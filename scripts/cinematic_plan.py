"""Translate an optional authored beat plan while checking temporal and reference identity."""
import math

PLAN_DIRECTIONS = {
    'objective': 'Intenção', 'space': 'Espaço', 'perspective': 'Ponto de vista',
    'composition': 'Composição', 'lighting': 'Luz', 'optics': 'Óptica',
    'environment': 'Ambiente',
}
BEAT_DIRECTIONS = {
    'action': 'Ação', 'performance': 'Atuação', 'attention': 'Atenção',
    'gaze': 'Olhar', 'subtext': 'Subtexto', 'camera': 'Câmera', 'sound': 'Som',
}


class PlanError(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise PlanError(message)


def finite_number(value):
    return type(value) in (int, float) and math.isfinite(value)


def compile_plan(plan, model, parameters, references):
    require(isinstance(plan, dict), 'Cinematic plan must be an object')
    require(set(plan) <= {*PLAN_DIRECTIONS, 'cast', 'beats', 'protected', 'duration_s'},
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
    for field in (*PLAN_DIRECTIONS, 'protected'):
        require(isinstance(plan.get(field, ''), str), 'Plan text must be text')
    beats = plan.get('beats')
    require(isinstance(beats, list) and beats, 'Provide the authored beats')
    known_refs = {item['id'] for item in references}
    previous_end = 0
    state = {}
    seen = set()
    lines = []
    for field, label in PLAN_DIRECTIONS.items():
        if plan.get(field, '').strip():
            lines.append(label + ' — ' + plan[field].strip())
    lines.append('Pessoas — ' + ' / '.join(key + ' = ' + value for key, value in sorted(cast.items())))
    warnings = []
    for beat in beats:
        require(isinstance(beat, dict) and set(beat) <= {
            *BEAT_DIRECTIONS, 'id', 'start_s', 'end_s', 'subjects', 'simultaneous',
            'entry', 'exit', 'references', 'continuity_exception', 'event_ids'},
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
        event_ids = beat.get('event_ids', [])
        require(isinstance(event_ids,list) and all(isinstance(value,str) and value.strip() for value in event_ids)
                and len(event_ids)==len(set(event_ids)), 'Invalid beat event identities')
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
        if event_ids:
            lines.append('Acontecimentos — ' + ', '.join(event_ids))
        for field, label in BEAT_DIRECTIONS.items():
            value = beat.get(field, '')
            require(isinstance(value, str), 'Beat directions must be text')
            if value.strip():
                lines.append(label + ' — ' + value.strip())
        simultaneous = beat.get('simultaneous', [])
        require(isinstance(simultaneous, list), 'Simultaneous actions must be a list')
        for activity in simultaneous:
            require(isinstance(activity, dict) and set(activity) == {'subjects', 'action'},
                    'Each simultaneous action needs subjects and an observable action')
            actors, action = activity['subjects'], activity['action']
            require(isinstance(actors, list) and actors and all(actor in subjects for actor in actors)
                    and len(actors) == len(set(actors)), 'Simultaneous action introduces unknown or repeated subjects')
            require(isinstance(action, str) and action.strip(), 'Describe the simultaneous action')
            lines.append('Em paralelo — ' + ', '.join(cast[actor] for actor in actors) + ' · ' + action.strip())
        for label, values in [('Entrada', entry), ('Saída', exit_state)]:
            if values:
                lines.append(label + ' — ' + ' / '.join(key + ' = ' + value for key, value in sorted(values.items())))
        if attached:
            lines.append('Referências anexadas — ' + ', '.join(attached))
    if previous_end < duration:
        warnings.append('The end of the planned shot has no authored action')
    if plan.get('protected', '').strip():
        lines.append('Preservar — ' + plan['protected'].strip())
    warnings.append('Beat timing and text are editorial requests; adherence requires viewing the returned video')
    return '\n'.join(lines), warnings
