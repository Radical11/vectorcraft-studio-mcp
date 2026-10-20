"""Opt-in execution transport. This module never grants visual acceptance."""
from copy import deepcopy
import hashlib
import json
import re
from pathlib import Path

PROFILE = 'efficient-v1'
LIMIT = 8192
_IDENTITIES = {}


def enabled(w):
    return bool(w.state and w.state.get('execution_profile') == PROFILE)


def identity(cli, version):
    path = Path(cli).resolve()
    stat = path.stat()
    key = (str(path), stat.st_size, stat.st_mtime_ns)
    if key not in _IDENTITIES:
        _IDENTITIES[key] = {'version': version, 'binary_sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
    return deepcopy(_IDENTITIES[key])


def capabilities(catalog):
    tools = {t['name']: t for t in catalog['tools']}
    description = tools.get('command_batch', {}).get('description', '')
    props = tools.get('draw_shape', {}).get('inputSchema', {}).get('properties', {})
    return {'draw_batch': 'draw_path' in description and 'draw_shape' in description,
            'inline_style': all(k in props for k in ('name', 'opacity', 'cap', 'join')),
            'schema_sha256': hashlib.sha256(json.dumps(catalog, sort_keys=True).encode()).hexdigest()}


def owner(gateway):
    return getattr(gateway, 'efficient_owner', gateway.workflow)


def batch(gateway, args):
    """Check the entire batch envelope before dispatch, including references."""
    if not enabled(owner(gateway)):
        return args
    steps = args.get('steps')
    if not isinstance(steps, list) or not 1 <= len(steps) <= 32:
        raise ValueError('Efficient batches require 1..32 coherent steps')
    for index, step in enumerate(steps):
        if not isinstance(step, dict) or not isinstance(step.get('id'), str) or not isinstance(step.get('params', {}), dict):
            raise ValueError('Each step needs a command id and object params')
        if set(step) - {'id', 'params'}:
            raise ValueError('Unknown batch step keys')
        if step['id'] in ('draw_path', 'draw_shape'):
            if not gateway.engine_capabilities.get('draw_batch'):
                raise ValueError('Engine lacks drawing batches; choose individual drawing calls before editing')
            schema = gateway.tool_catalog[step['id']]['inputSchema']
            params = step.get('params', {})
            if set(params) - set(schema['properties']) or set(schema.get('required', [])) - set(params):
                raise ValueError('Drawing step has missing or unknown tool arguments')
            if step['id'] == 'draw_shape' and params.get('shape') not in schema['properties']['shape']['enum']:
                raise ValueError('Unknown native shape')
            if step['id']=='draw_shape':
                dimensions={'rectangle':('x','y','width','height'),'ellipse':('x','y','width','height'),
                            'polygon':('cx','cy','radius'),'star':('cx','cy','radius1','radius2'),
                            'line':('x1','y1','x2','y2')}[params['shape']]
                if any(k not in params for k in dimensions):raise ValueError('Missing shape dimensions')
            elif not (params.get('d') or params.get('points')):raise ValueError('Path needs geometry')
        def visit(value):
            if isinstance(value, dict):
                for child in value.values(): visit(child)
            elif isinstance(value, list):
                for child in value: visit(child)
            elif isinstance(value, str):
                match = re.fullmatch(r'\$(\d+|last)\..+', value)
                if match and (index == 0 or match[1] != 'last' and int(match[1]) >= index):
                    raise ValueError('Batch reference must name an earlier step')
        visit(step.get('params', {}))
    result = dict(args)
    result.setdefault('stop_on_error', True)
    result.setdefault('atomic', True)
    result.setdefault('label', 'Focused component')
    if result['stop_on_error'] is not True or result['atomic'] is not True or not str(result['label']).strip():
        raise ValueError('Efficient batches require stop_on_error, a named undo group and atomic:true (not rollback)')
    return result


def packet(w, original):
    result = deepcopy(original)
    result.pop('contract', None)
    # Completed prerequisite artifacts remain in the integrity-checked state index.
    # Avoid repeating seven long absolute paths on every edit response.
    if result.pop('references', None):
        result['records_reference'] = '/records (latest record of each kind, relative to run)'
    studies = result.pop('studies', {})
    if studies:
        result['study_summary'] = {k: v.get('outcome') for k, v in studies.items()}
    # Full state remains on disk, already bound by revision/spec and its digest.
    state_path = w.run / 'run.json'
    reference = {'path': str(state_path), 'sha256': hashlib.sha256(state_path.read_bytes()).hexdigest(),
                 'revision': w.state['revision'], 'spec_revision': w.state['spec_revision']}
    result.update(execution_profile=PROFILE, packet_version=2, state_reference=reference,
                  engine_identity=w.state.get('engine_identity'), schemas_action='workflow_status view:full')
    if w.state['status']=='stopped_unresolved':
        result['next_action']='Preserve retained artwork and unresolved evidence. Resume with explicit feedback and verified recovery, within the stored correction budget.'
    result['omitted_fields'] = {}
    for key, pointer in (('study_summary', '/design_process/studies'), ('graph_entities', '/records'),
                         ('applicable_relationships', '/design_process/relations'), ('unresolved_findings', '/focused/queue'),
                         ('detail_images', '/versions'), ('global_style', '/records'),
                         ('active_task', '/pending/plan'), ('relevant_object_ids', '/focused/mapping')):
        if len(json.dumps(result, ensure_ascii=False).encode()) <= LIMIT:
            break
        if key in result and result[key]:
            result['omitted_fields'][key] = {'state_pointer': pointer, 'retrieve_before_dependent_edits': True}
            if key == 'unresolved_findings':
                result['blocking_finding_count'] = len(result[key])
            del result[key]
    if result['omitted_fields']:
        result['context_complete'] = False
        result['next_action'] = 'Retrieve omitted task context from state_reference and referenced records before dependent edits. ' + result['next_action']
    else:
        result['context_complete'] = True
    # Safety/state fields are never silently truncated to satisfy a byte target.
    result['within_packet_target'] = len(json.dumps(result, ensure_ascii=False).encode()) <= LIMIT
    return result


def area_options(backend, object_id):
    from workflow import result_payload
    try:
        result = result_payload(backend.checked_call('command_run', {'id': 'text.areaOptions', 'params': {'ids': [object_id]}}))
    except RuntimeError as error:
        # A definite disabled query can be retried with selection. Never retry edits.
        if not any(term in str(error).lower() for term in ('disabled', 'not enabled', 'nothing selected', 'requires a selection', 'select an')):
            raise
        before = result_payload(backend.checked_call('doc_inspect', {}))
        selected = before.get('selection', [])
        try:
            backend.checked_call('command_run', {'id': 'select.set', 'params': {'ids': [object_id]}})
            result = result_payload(backend.checked_call('command_run', {'id': 'text.areaOptions', 'params': {'ids': [object_id]}}))
        finally:
            backend.checked_call('command_run', {'id': 'select.set', 'params': {'ids': selected}})
    if (not isinstance(result, dict) or type(result.get('overflow')) is not bool or
            type(result.get('fitScale')) not in (int, float) or not 0 < result['fitScale'] <= 1):
        raise ValueError('Cannot verify actual area-text overflow/fitScale')
    return result


def stop(w, data):
    from workflow import nonempty, atomic
    if not w.state or w.state['status'] != 'active' or w.state['mode'] != 'full':
        raise ValueError('An active full v3 run is required to stop unresolved')
    w.verify()
    nonempty(data.get('reason'), 'unresolved stop reason')
    findings = data.get('unresolved_findings')
    if not isinstance(findings, list) or not findings:
        raise ValueError('Disclose unresolved findings')
    for finding in findings: nonempty(finding, 'unresolved finding')
    path = w.run / 'unresolved-stop.json'
    atomic(path, {'reason': data['reason'], 'unresolved_findings': findings,
                  'uncertain': bool(w.state['uncertain']), 'pending_preserved': bool(w.state['pending'])})
    w.state['records'].append({'kind': 'stop', 'artifact': w.artifact(path, 'unresolved-stop'),
                               'spec_revision': w.state['spec_revision']})
    w.state.update(status='stopped_unresolved', stop_reason=data['reason'])
    w.persist()
    return w.response()
