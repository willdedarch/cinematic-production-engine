"""Run the operation declared by a laboratory or prepare its directed viewing sheet."""
from pathlib import Path
import importlib.util
from optics import optics


def run_laboratory(plan, run_dir, source=None):
    lab = plan['laboratory']
    variants = plan['spec']['variants']
    tool = plan['tool']
    if tool == 'native_image':
        return {**plan, 'execution_mode': 'NATIVE_REQUEST', 'next': 'Present the scoped request to the host'}
    if tool == 'context':
        return {**plan, 'kind': 'GUIDED_REVIEW_READY', 'execution_mode': 'GUIDED',
                'worksheet': {'procedure': lab['procedure'], 'criteria': lab['criteria'],
                              'checklist': lab['checklist'], 'variants': variants,
                              'response_fields': ['variant_id', 'observation', 'evidence_ref', 'decision', 'reason']},
                'next': 'Inspect the material against each criterion and return the observations in a new message.'}

    def missing(reason):
        return {**plan, 'kind': 'LAB_RESOURCE_REQUIRED', 'execution_mode': 'AWAITING_RESOURCE',
                'required_resource': reason, 'criteria': lab['criteria'], 'procedure': lab['procedure']}

    if tool in {'overlay', 'previs_2d', 'image_analysis'}:
        if any(importlib.util.find_spec(pkg) is None for pkg in ('PIL', 'numpy')):
            return missing('Existing Pillow and NumPy, or guided human inspection of the supplied material')
    inputs = {}
    for variant in variants:
        if tool in {'overlay', 'image_analysis'}:
            filename = variant.get('settings', {}).get('source') or source
            if not filename or not Path(filename).is_file():
                return missing(f"Accessible local image for variant {variant['id']}")
            inputs[variant['id']] = Path(filename)
    outputs = []
    for variant in variants:
        settings = dict(variant.get('settings', {}))
        ident = variant['id']
        if tool == 'optics':
            value = optics(settings)
        elif tool == 'previs_2d':
            from previs import plan as draw_plan
            value = draw_plan(settings, run_dir / ident)
        elif tool == 'overlay':
            from image_tools import overlay
            settings.pop('source', None)
            value = overlay(inputs[ident], run_dir / (ident + '.png'), settings)
        elif tool == 'image_analysis':
            from image_tools import analyze
            settings.pop('source', None)
            if settings:
                raise ValueError('Image analysis accepts source only. Supply a prepared image for each material variant.')
            value = analyze(inputs[ident], run_dir / ident)
        else:
            raise ValueError('Unsupported laboratory tool: ' + tool)
        outputs.append({'variant_id': ident, 'observed_technical_result': value})

    result = {**plan, 'kind': 'LOCAL_EXPERIMENT_EXECUTED', 'execution_mode': 'EXECUTED',
              'observed_result': outputs, 'artistic_decision': 'PENDING'}
    if tool == 'image_analysis' and len(outputs)>1:
        hashes={row['observed_technical_result']['sha256'] for row in outputs}
        if len(hashes)==1:
            result.update(design='REPLICATION',design_basis='Identical source content',
                          single_variable_controlled=False,changed_variables=[])
    return result
