"""Research-first workflow evidence. Validates records, never aesthetic judgments."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import shutil
import uuid

STAGES = ('composition', 'typography', 'imagery', 'finishing')


def now():
    return datetime.now(timezone.utc).isoformat()


def nonempty(value, label):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(label + ' must be nonempty text')


def init_v2(studio, root, run_id, brief, max_rounds=3):
    run, state = studio.init(root, run_id, brief, max_rounds)
    state.update(version=2, workflow={'records': [], 'events': [], 'pending': None,
        'completed_stages': [], 'ready_versions': [], 'working_version': None,
        'original_version': None, 'research_gaps': []})
    studio.atomic(run / 'run.json', state)
    return run, state


def evidence(studio, run, state, source, role):
    source = Path(source).resolve()
    if not source.is_relative_to(Path(state['project_root'])) or not source.is_file():
        raise ValueError('Workflow evidence must be a project file')
    target = run / 'workflow' / (uuid.uuid4().hex + source.suffix)
    target.parent.mkdir(exist_ok=True)
    shutil.copy2(source, target)
    return studio.artifact(run, target, role)


def load_v2(studio, run):
    run, state = studio.load(run)
    if state['version'] != 2:
        raise ValueError('Legacy run: use its original snapshot/review commands; do not retrofit research')
    if state['status'] != 'active':
        raise ValueError('Run has stopped')
    return run, state


def latest(state, kind):
    return next((r for r in reversed(state['workflow']['records']) if r['kind'] == kind), None)


def validate_research(data, verified):
    if not verified:
        raise ValueError('Parent must verify actual source-image tool use')
    nonempty(data.get('subject_summary'), 'subject_summary')
    nonempty(data.get('audience_and_use'), 'audience_and_use')
    nonempty(data.get('synthesis'), 'synthesis')
    for fact in data.get('facts', []):
        nonempty(fact.get('claim'), 'fact claim')
        nonempty(fact.get('source_url'), 'fact source_url')
    if not isinstance(data.get('assumptions'), list) or not isinstance(data.get('gaps'), list):
        raise ValueError('Research requires assumptions and gaps lists')
    refs = data.get('references', [])
    if not refs:
        raise ValueError('No inspected visual reference; mark research unavailable, do not invent it')
    seen = set()
    for ref in refs:
        for key in ('title', 'creator', 'url', 'accessed', 'source_type', 'observation', 'transformation'):
            nonempty(ref.get(key), key)
        if not re.match(r'https?://', ref['url']):
            raise ValueError('Reference URL must be http(s)')
        visual = ref.get('visual_inspection', {})
        for key in ('tool', 'evidence', 'observation'):
            nonempty(visual.get(key), 'visual_inspection.' + key)
        key = (ref['creator'].casefold(), ref['title'].casefold())
        if key in seen:
            raise ValueError('Duplicate work/creator cannot increase the reference count')
        seen.add(key)
    types = {ref['source_type'] for ref in refs}
    if (len(refs) < 15 or len(types) < 4) and not data['gaps']:
        raise ValueError('Below research target: explain missing references/source diversity in gaps')
    if data.get('discovery_passes', 1) != 1 or data.get('gap_filling_passes', 0) not in (0, 1):
        raise ValueError('Research is bounded to discovery plus one gap-filling pass')


def record(studio, run, kind, source, verified=False):
    run, state = load_v2(studio, run)
    data = studio.read(source)
    extra = []
    if kind == 'research':
        validate_research(data, verified)
        state['workflow']['research_gaps'] = data['gaps']
    elif kind == 'directions':
        if not latest(state, 'research'):
            raise ValueError('Research synthesis must precede directions')
        directions = data.get('directions', [])
        if len(directions) != 3 or len({d.get('id') for d in directions}) != 3:
            raise ValueError('Three distinct directions are required')
        for direction in directions:
            for key in ('id', 'concept', 'metaphor', 'visual_language', 'thumbnail'):
                nonempty(direction.get(key), key)
            extra.append(evidence(studio, run, state, direction['thumbnail'], 'thumbnail'))
        if data.get('selected') not in {d['id'] for d in directions}:
            raise ValueError('Selected direction must exist')
        nonempty(data.get('selection_reason'), 'selection_reason')
    elif kind == 'layout':
        if not latest(state, 'directions'):
            raise ValueError('Direction exploration must precede layout')
        for key in ('hierarchy', 'focal_point', 'placement', 'spacing', 'typography', 'palette', 'reading_sequence'):
            nonempty(data.get(key), key)
    else:
        raise ValueError('Unknown record kind')
    item = {'id': uuid.uuid4().hex, 'kind': kind, 'at': now(),
            'artifact': evidence(studio, run, state, source, kind), 'attachments': extra,
            'parent_verified_visuals': verified if kind == 'research' else None}
    state['workflow']['records'].append(item)
    state['workflow']['ready_versions'] = []
    studio.atomic(run / 'run.json', state)
    return state


def begin(studio, run, stage, plan):
    run, state = load_v2(studio, run)
    wf = state['workflow']
    if wf['pending']:
        raise ValueError('Inspect and finish the pending batch before another edit batch')
    if not all(latest(state, k) for k in ('research', 'directions', 'layout')):
        raise ValueError('Research, directions and layout required before artwork edits')
    if stage not in STAGES:
        raise ValueError('Unknown construction stage')
    if any(s not in wf['completed_stages'] for s in STAGES[:STAGES.index(stage)]):
        raise ValueError('Inspect earlier stages before advancing')
    data = studio.read(plan)
    for key in ('purpose', 'expected_result', 'changes', 'checks'):
        nonempty(data.get(key), key)
    wf['ready_versions'] = []
    wf['pending'] = {'id': uuid.uuid4().hex, 'stage': stage, 'at': now(),
        'plan': evidence(studio, run, state, plan, 'batch-plan'),
        'layout_record': latest(state, 'layout')['id'], 'before_versions': list(state['versions'])}
    wf['events'].append({'event': 'begin', **wf['pending']})
    studio.atomic(run / 'run.json', state)
    return state


def checkpoint(studio, run, version, inspection, verified=False):
    run, state = load_v2(studio, run)
    wf = state['workflow']; pending = wf['pending']
    if not pending or version not in state['versions'] or version in pending['before_versions']:
        raise ValueError('Checkpoint requires a new snapshot following a planned batch')
    if not verified:
        raise ValueError('Parent must verify image tool use for the stage preview')
    data = studio.read(inspection)
    images = [str(run / a['path']) for a in state['versions'][version]['artifacts'] if a['role'] == 'image']
    paths = data.get('paths', [])
    if not all(any(Path(p).is_file() and studio.digest(p) == studio.digest(image) for p in paths) for image in images):
        raise ValueError('Inspect the actual full and use-size checkpoint images')
    for key in ('observations', 'alignment', 'optical_balance', 'readability', 'style_consistency', 'subject_relevance', 'originality', 'decision'):
        nonempty(data.get(key), key)
    event = {'event': 'checkpoint', 'at': now(), 'batch': pending['id'], 'stage': pending['stage'],
             'version': version, 'inspection': evidence(studio, run, state, inspection, 'self-check'),
             'parent_verified_images': True, 'layout_record': pending['layout_record']}
    wf['events'].append(event)
    wf['pending'] = None
    if pending['stage'] not in wf['completed_stages']:
        wf['completed_stages'].append(pending['stage'])
    wf['working_version'] = version
    studio.atomic(run / 'run.json', state)
    return state


def preflight(studio, run, version, source):
    run, state = load_v2(studio, run)
    wf = state['workflow']
    if wf['pending'] or set(wf['completed_stages']) != set(STAGES) or version != wf['working_version']:
        raise ValueError('Finish and inspect all construction stages before final critique')
    checkpoint_event = next(e for e in reversed(wf['events']) if e['event'] == 'checkpoint')
    if checkpoint_event['layout_record'] != latest(state, 'layout')['id']:
        raise ValueError('Inspect a planned batch against the amended layout before final critique')
    data = studio.read(source)
    for key in ('required_content', 'export_files', 'font_warnings', 'clipping_and_readability'):
        nonempty(data.get(key), key)
    exports = [evidence(studio, run, state, p, 'export') for p in data.get('files', [])]
    if not data.get('files'):
        raise ValueError('Preflight needs at least one actual exported file')
    wf['events'].append({'event': 'preflight', 'version': version, 'at': now(),
                         'artifact': evidence(studio, run, state, source, 'preflight'), 'exports': exports})
    wf['ready_versions'].append(version)
    studio.atomic(run / 'run.json', state)
    return state


def assert_snapshot(state, role):
    if state.get('version') != 2:
        return
    wf = state['workflow']
    if role == 'original':
        if state['versions'] or wf['original_version']:
            raise ValueError('Untouched original must be preserved before other snapshots')
    elif not wf['pending']:
        raise ValueError('Plan a batch before artwork snapshots; use role original only for untouched input')


def assert_review(state, version):
    if state.get('version') == 2 and version not in state['workflow']['ready_versions']:
        raise ValueError('Independent critique is final-only: inspected stages and export preflight required')


def integrity_artifacts(state):
    if state.get('version') != 2:
        return []
    wf = state['workflow']; out = []
    for r in wf['records']:
        out.extend([r['artifact'], *r['attachments']])
    for event in wf['events']:
        out.extend(event.get('exports', []))
        for key in ('plan', 'inspection', 'artifact'):
            if key in event:
                out.append(event[key])
    return out


def main():
    import studio_run as studio
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest='cmd', required=True)
    for name in ('record', 'begin', 'checkpoint', 'preflight'):
        q = sub.add_parser(name); q.add_argument('--run', required=True)
        q.add_argument('--file', required=True)
        if name == 'record': q.add_argument('--kind', choices=['research', 'directions', 'layout'], required=True)
        if name == 'begin': q.add_argument('--stage', choices=STAGES, required=True)
        if name in ('checkpoint', 'preflight'): q.add_argument('--version', required=True)
        if name in ('record', 'checkpoint'): q.add_argument('--images-verified', action='store_true')
    args = p.parse_args()
    if args.cmd == 'record': state = record(studio, args.run, args.kind, args.file, args.images_verified)
    elif args.cmd == 'begin': state = begin(studio, args.run, args.stage, args.file)
    elif args.cmd == 'checkpoint': state = checkpoint(studio, args.run, args.version, args.file, args.images_verified)
    else: state = preflight(studio, args.run, args.version, args.file)
    print(json.dumps(state, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, KeyError, TypeError) as error:
        raise SystemExit(str(error))
