"""Opt-in focused execution policy. Image judgments are attested, never inferred."""
from copy import deepcopy
from workflow import STAGES, nonempty, safe_id, nodes_from_native, atomic, now

PROFILE = 'focused-execution-v1'
STAGE_CHECKS = {
    'composition': ('placement_scale', 'reading_order', 'focal_separation'),
    'typography': ('exact_copy', 'live_text_fonts', 'use_size_readability'),
    'imagery': ('recognizable_forms', 'proportions', 'critical_interactions'),
    'finishing': ('scene_cohesion', 'visible_defects', 'production_readiness'),
}
SCHEMA = {
    'begin': {'task_id': 'unique filename-safe id; reuse only for an unresolved task',
              'goal': 'one component or connected-group outcome',
              'entities': '1..3 current spec IDs', 'preserve': 'nonempty preservation requirements',
              'checks': '2..3 {id,description} observable checks',
              'finding_id': 'required when addressing the first correction-queue item'},
    'confirm': {'outcome': 'pass|revise|blocked',
                'check_results': '[{id,outcome:pass|fail|not_applicable,observation,reason?}]',
                'image_inspection': 'performed, paths including full/use/target, observations',
                'image_observation': 'tool, evidence, observation',
                'preservation_observation': 'observed effects on neighbors and whole scene',
                'element_map': 'cumulative introduced spec IDs -> actual native IDs',
                'stage_complete': 'explicit boolean, default false',
                'stage_checks': 'required on completion: all three stage keys -> {outcome,observation,reason?}',
                'reason': 'required for revise/blocked', 'detail_images': 'optional project image paths'},
    'scope': 'Declarative guidance, not a per-object sandbox; judgments remain agent-attested.',
}


def enabled(w):
    return bool(w.state and w.state.get('quality_profile') in (PROFILE, 'designer-process-v1') and w.state['mode'] == 'full')


def state(w):
    return w.state['focused']


def invalidate(w, stage=None):
    f = state(w)
    f['verified_revision'] = None
    if stage:
        removed = STAGES[STAGES.index(stage):]
        w.state['completed_stages'] = [s for s in w.state['completed_stages'] if s not in removed]
        for s in removed:
            f['acceptances'].pop(s, None)
    else:
        w.state['completed_stages'] = []
        f['acceptances'] = {}
        f['mapping'] = {}
        for task in f['tasks'].values():
            task['stale'] = True
        known = {e['id'] for e in (w.data('spec') or {}).get('elements', [])}
        for finding in f['queue']:
            finding['stale'] = True
            finding['entities'] = [e for e in finding.get('entities', []) if e in known]


def begin(w, stage, plan):
    f = state(w)
    task_id = safe_id(plan.get('task_id'))
    for key in ('goal', 'preserve'):
        nonempty(plan.get(key), key)
    entities = plan.get('entities')
    known = {e['id'] for e in w.data('spec')['elements']}
    if (not isinstance(entities, list) or not 1 <= len(entities) <= 3
            or not all(isinstance(e, str) for e in entities)
            or len(set(entities)) != len(entities) or not set(entities) <= known):
        raise ValueError('Focused task needs one to three known semantic entities')
    checks = plan.get('checks')
    if not isinstance(checks, list) or not 2 <= len(checks) <= 3:
        raise ValueError('Focused task needs two or three observable checks')
    ids = []
    for check in checks:
        if not isinstance(check, dict):
            raise ValueError('Observable checks must be objects')
        ids.append(safe_id(check.get('id')))
        nonempty(check.get('description'), 'check description')
    if len(set(ids)) != len(ids):
        raise ValueError('Check IDs must be unique')
    previous = f['tasks'].get(task_id)
    if previous and (previous['outcome'] == 'pass' or previous.get('stale')):
        raise ValueError('Use a new task ID after a passed or stale task')
    if previous and (previous['stage'] != stage or previous['entities'] != entities):
        raise ValueError('An unresolved task keeps its stage and entities')
    queue = f['queue']
    if queue and plan.get('finding_id') != queue[0]['id']:
        raise ValueError('Address the first correction-queue finding')
    if not queue and plan.get('finding_id'):
        raise ValueError('Unknown correction finding')
    if queue and queue[0].get('entities') and not set(queue[0]['entities']) <= set(entities):
        raise ValueError('Correction must include the affected entities')
    unresolved = [t for t in f['tasks'].values()
                  if not t.get('stale') and t['outcome'] != 'pass']
    if any(t['task_id'] != task_id for t in unresolved):
        raise ValueError('Resolve the existing task before starting another')


def result(item, label):
    if not isinstance(item, dict) or item.get('outcome') not in ('pass', 'fail', 'not_applicable'):
        raise ValueError(label + ' needs pass, fail or not_applicable')
    nonempty(item.get('observation'), label + ' observation')
    if item['outcome'] == 'not_applicable':
        nonempty(item.get('reason'), label + ' inapplicable reason')
    return item['outcome'] != 'fail'


def confirm(w, version, data):
    import designer
    s, f = w.state, state(w)
    pending, snap = s['pending'], s['versions'][version]
    plan, stage = pending['plan'], pending['stage']
    outcome = data.get('outcome')
    if outcome not in ('pass', 'revise', 'blocked'):
        raise ValueError('Focused outcome must be pass, revise or blocked')
    nonempty(data.get('observations'), 'actual image observations')
    nonempty(data.get('preservation_observation'), 'preservation observation')
    results = data.get('check_results', [])
    expected = {c['id'] for c in plan['checks']}
    if (not isinstance(results, list) or any(not isinstance(c, dict) for c in results)
            or len(results) != len(expected) or {c.get('id') for c in results} != expected):
        raise ValueError('Assess each planned check exactly once')
    checks_pass = all([result(c, 'task check') for c in results])
    if outcome == 'pass' and not checks_pass:
        raise ValueError('A failed check cannot pass the task')
    if outcome != 'pass':
        nonempty(data.get('reason'), 'unresolved task reason')
    complete = data.get('stage_complete', False)
    if type(complete) is not bool or complete and outcome != 'pass':
        raise ValueError('Stage completion requires an explicit passing task')
    images = [w.run / a['path'] for a in snap['images']]
    images.append(w.run / w.latest('target')['attachments'][0]['path'])
    designer.inspection(w, data, images)
    mapping = data.get('element_map', {})
    if not isinstance(mapping, dict):
        raise ValueError('Element map must be an object')
    nodes = nodes_from_native(w.run / snap['native']['path'])
    spec = w.data('spec')
    known = {e['id'] for e in spec['elements']}
    if not set(mapping) <= known:
        raise ValueError('Unknown mapped semantic entity')
    required = set(f['mapping']) | set(plan['entities'])
    if complete:
        reached = set(s['completed_stages']) | {stage}
        required |= {e['id'] for e in spec['elements'] if e['stage'] in reached}
    for entity in set(mapping) | required:
        ids = mapping.get(entity)
        if not isinstance(ids, list) or not ids or any(str(i) not in nodes for i in ids):
            raise ValueError('Missing actual document objects for ' + entity)
    if complete:
        stage_checks = data.get('stage_checks', {})
        if not isinstance(stage_checks, dict) or set(stage_checks) != set(STAGE_CHECKS[stage]):
            raise ValueError('Assess all three stage completion checks')
        if not all([result(v, 'stage check') for v in stage_checks.values()]):
            raise ValueError('Failed stage check prevents completion')
    queue = deepcopy(f['queue'])
    if outcome == 'pass' and plan.get('finding_id'):
        queue = [q for q in queue if q['id'] != plan['finding_id']]
    if complete and queue:
        raise ValueError('Resolve blocking findings before stage completion')
    details = [w.artifact(p, 'detail-image') for p in data.get('detail_images', [])]
    for departure in data.get('departures', []):
        if departure.get('element') not in known:
            raise ValueError('Unknown departure element')
        nonempty(departure.get('reason'), 'intentional departure rationale')
    task_id = plan['task_id']
    if outcome != 'pass' and not queue:
        queue.append({'id': 'task-' + task_id, 'entities': plan['entities'], 'stage': stage,
                      'reason': data['reason'], 'severity': 'major',
                      'revision': s['revision'], 'spec_revision': s['spec_revision']})
    dest = w.run / 'focused-confirm-input.json'
    atomic(dest, data)
    snap.update(check=w.artifact(dest, 'focused-observation'), confirmed=True,
                element_map=deepcopy(mapping), task_outcome=outcome, detail_images=details)
    f['tasks'][task_id] = {'task_id': task_id, 'stage': stage, 'entities': plan['entities'],
                           'goal': plan['goal'], 'outcome': outcome, 'version': version,
                           'revision': s['revision'], 'spec_revision': s['spec_revision'],
                           'observation': snap['check'], 'stale': False}
    f['mapping'], f['queue'] = deepcopy(mapping), queue
    f['mapping_revision'], f['mapping_spec_revision'] = s['revision'], s['spec_revision']
    if outcome == 'pass':
        f['verified_revision'] = s['revision']
        if complete:
            f['acceptances'][stage] = {'version': version, 'revision': s['revision'],
                                       'spec_revision': s['spec_revision'], 'observation': snap['check']}
            if stage not in s['completed_stages']:
                s['completed_stages'].append(stage)
    else:
        f['verified_revision'] = None
        invalidate(w, stage)
    s['events'].append({'event': 'focused_checkpoint', 'at': now(), 'version': version,
                        'task_id': task_id, 'outcome': outcome, 'stage_complete': complete})
    s['working_version'], s['pending'] = version, None
    s['ready_versions'] = []
    w.persist()
    return w.response()


def preflight(w):
    s, f = w.state, state(w)
    if (f['queue'] or any(not t.get('stale') and t['outcome'] != 'pass' for t in f['tasks'].values())
            or f['verified_revision'] != s['revision']
            or set(f['acceptances']) != set(STAGES)
            or any(a['spec_revision'] != s['spec_revision'] for a in f['acceptances'].values())):
        raise ValueError('Focused preflight requires current accepted stages and no unresolved tasks/findings')


def reviewed(w, data):
    """Queue consequential candidate findings only while further correction is allowed."""
    if w.state['status'] != 'active':
        return
    f = state(w)
    for item in data['reviews']:
        for index, finding in enumerate(item['review']['findings']):
            if finding['severity'] not in ('major', 'critical'):
                continue
            f['queue'].append({'id': f"review-{len(w.state['reviews'])}-{item['role']}-{index}",
                               'reason': finding['evidence'], 'fix': finding['fix'],
                               'location': finding['location'], 'severity': finding['severity'],
                               'revision': w.state['revision'], 'spec_revision': w.state['spec_revision']})
    f['queue'].sort(key=lambda q: 0 if q['severity'] == 'critical' else 1)


def packet(w):
    s, f = w.state, state(w)
    pending = s['pending']
    version = (pending or {}).get('captured') or s['working_version']
    snap = s['versions'].get(version, {})
    current = snap.get('revision') == s['revision'] and snap.get('spec_revision') == s['spec_revision']
    active = deepcopy(pending['plan']) if pending else None
    if active:
        active = {k: active[k] for k in ('task_id', 'goal', 'entities', 'preserve', 'checks', 'finding_id') if k in active}
    unresolved = [t for t in f['tasks'].values() if not t.get('stale') and t['outcome'] != 'pass']
    stage = pending['stage'] if pending else (unresolved[0]['stage'] if unresolved else next((x for x in STAGES if x not in s['completed_stages']), 'finishing'))
    if s['status'] != 'active':
        next_action = 'Deliver best_version with recorded limitations'
    elif s['uncertain']:
        next_action = 'Inspect recovery and resume in a fresh connection; never replay edits'
    elif pending:
        next_action = 'Inspect full/use/target then confirm' if pending.get('captured') else 'Execute current task then capture'
    elif unresolved or f['queue']:
        next_action = 'Plan one correction for the first unresolved finding'
    elif not all(w.latest(k) for k in ('research', 'calibration', 'directions', 'concept_review', 'target', 'spec')):
        next_action = 'Complete designer prerequisites; consult full workflow_status schemas'
    elif stage in ('imagery', 'finishing') and not w.latest('construction_study'):
        next_action = 'Record an actually observed representative construction study before imagery'
    elif set(s['completed_stages']) != set(STAGES):
        next_action = 'Plan a focused task or explicit stage acceptance for ' + stage
    elif any(r['version'] == s['working_version'] for r in s['reviews']):
        next_action = 'Plan a correction from the latest observed review, or deliver retained best with limitations'
    elif s['ready_versions']:
        next_action = 'Create neutral packet and obtain fresh independent specialist reviews'
    else:
        next_action = 'Export and inspect SVG/PDF/PNG, then preflight'
    entities = active['entities'] if active else (unresolved[0]['entities'] if unresolved else [])
    refs = {k: str(w.run / r['artifact']['path']) for k in ('research', 'calibration', 'directions', 'concept_review', 'target', 'spec', 'construction_study') if (r := w.latest(k))}
    if s['reviews']:
        latest = next((r for r in reversed(s['reviews']) if r['version'] == s['working_version']), s['reviews'][-1])
        refs['latest_review'] = str(w.run / latest['artifact']['path'])
    return {'profile': PROFILE, 'run': str(w.run), 'status': s['status'], 'revision': s['revision'],
            'spec_revision': s['spec_revision'], 'stage': stage, 'active_task': active,
            'relevant_object_ids': {e: f['mapping'].get(e, []) for e in entities},
            'mapping_current': f.get('mapping_revision') == s['revision'] and f.get('mapping_spec_revision') == s['spec_revision'],
            'preview_current': current, 'preview_revision': snap.get('revision'),
            'full_preview': str(w.run / snap['images'][0]['path']) if snap else None,
            'use_preview': str(w.run / snap['images'][1]['path']) if snap else None,
            'detail_images': [str(w.run / a['path']) for a in snap.get('detail_images', [])],
            'stage_completion_checks': list(STAGE_CHECKS[stage]),
            'unresolved_findings': deepcopy(f['queue']), 'next_action': next_action,
            'references': refs, 'contract': SCHEMA,
            'scope': 'Guidance only. Verify neighbors and whole scene after edits; image judgments are attested.'}
