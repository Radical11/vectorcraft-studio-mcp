"""Publish an additive stage supplement and render the read-only research explorer.

Export reads existing trial records; it never starts a Session or calls the engine.
Render/check need only the public supplement. No visual preference is inferred.
"""
from pathlib import Path
import argparse
import hashlib
import html
import json
import re
import shutil

ROOT = Path(__file__).resolve().parents[1]
CHECKPOINT = Path('public-evidence/process-study-20261015')
SUPPLEMENT = Path('public-evidence/process-stages-20261015')
STAGES = {
    'roughs': ('Native roughs', 'Compare overall ideas, placement, scale and reading experience.'),
    'construction-study': ('Construction study', 'Check a representative native form or interaction before production.'),
    'composition': ('Composition', 'Check placement, scale, reading order and focal separation.'),
    'typography': ('Typography', 'Check exact copy, live text, fonts and intended-size readability.'),
    'imagery': ('Imagery', 'Check recognizable forms, proportions and critical interactions.'),
    'finishing': ('Finishing', 'Check whole-scene cohesion, consequential defects and production readiness.'),
}
PROFILES = ['designer-v1', 'layout-blockout-v1', 'designer-process-v1']
PROFILE_NAMES = {'designer-v1': 'Standard', 'focused-execution-v1': 'Focused build',
                 'layout-blockout-v1': 'Layout first', 'designer-process-v1': 'Full process'}
BRIEF_NAMES = {'tyre': 'Repair', 'exchange': 'Book exchange', 'library': 'Library guide'}
STAGE_NAMES = {'roughs': 'Try layouts', 'construction-study': 'Test a detail',
               'composition': 'Arrange the scene', 'typography': 'Set the text',
               'imagery': 'Build the drawing', 'finishing': 'Polish and check'}
STEP_GUIDE = Path('docs/research/STEP-GUIDE.json')


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def encode(data):
    return json.dumps(data, indent=2, ensure_ascii=False) + '\n'


def scrub(value, root):
    if isinstance(value, dict):
        return {scrub(k, root): scrub(v, root) for k, v in value.items()}
    if isinstance(value, list):
        return [scrub(v, root) for v in value]
    if isinstance(value, str):
        value = re.sub(re.escape(str(root)), '<project>', value, flags=re.I)
        value = re.sub(re.escape(root.as_posix()), '<project>', value, flags=re.I)
        value = re.sub(r'C:[/\\]+Users[/\\]+[^/\\\s"<>]+', '<private-user>', value, flags=re.I)
    return value


def safe_artifact(root, path):
    resolved = (root / path.replace('\\', '/')).resolve()
    if not resolved.is_relative_to(root.resolve()):
        raise ValueError('Artifact path escapes its root')
    return resolved


def stage_binding(run, version, snapshot):
    """Use explicit events/timestamps, never infer stage from a version name."""
    begin = None
    for i, event in enumerate(run.get('events', [])):
        if event['event'] == 'begin':
            begin = (i, event)
        if event.get('version') == version and event['event'] in ('checkpoint', 'focused_checkpoint'):
            stage = event.get('stage') or (begin[1]['stage'] if begin else None)
            return stage, begin, i, event
    # Unconfirmed captures have no confirm event. Bind to the actual begin at capture time.
    eligible = [(i, e) for i, e in enumerate(run.get('events', []))
                if e['event'] == 'begin' and e.get('at', '') <= snapshot.get('at', '')]
    if not eligible:
        raise ValueError('Capture has no explicit stage binding: ' + version)
    begin = eligible[-1]
    return begin[1]['stage'], begin, None, {}


def label(row):
    if row['status'] == 'pending':
        return 'Pending — deferred'
    if row.get('run_status') == 'review_passed':
        return 'Final construction review passed'
    if row['status'] == 'failed':
        return 'Delivered; quality acceptance unresolved'
    if row.get('production_capture'):
        return 'Partial production work; no final acceptance'
    return 'Disrupted; no final production artwork'


def export(root, checkpoint, roots_path, out):
    root = root.resolve()
    out = out.resolve()
    if not out.is_relative_to(root / 'public-evidence') or out.exists():
        raise ValueError('Use a new supplement under public-evidence')
    cp = read(checkpoint / 'checkpoint.json')
    if any(r['status'] == 'building' for r in cp['results']):
        raise ValueError('Cannot publish an active builder')
    roots = read(roots_path)['roots']
    out.mkdir(parents=True)
    omissions, trials = [], []

    def artifact(base, item, destination):
        if not item:
            return None
        source = safe_artifact(base, item['path'])
        if not source.is_file() or sha(source) != item['sha256']:
            omissions.append({'path': destination.as_posix(), 'reason': 'Recorded source absent or changed'})
            return None
        if source.suffix == '.vectorcraft' and re.search(
                r'[A-Z]:[/\\]|gh[pousr]_[A-Za-z0-9]{30,}|sk-[A-Za-z0-9]{35,}',
                source.read_text(encoding='utf-8-sig')):
            omissions.append({'path': destination.as_posix(), 'reason': 'Unsafe native metadata; omitted without rewriting'})
            return None
        target = out / destination
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        return {'path': target.relative_to(root).as_posix(), 'sha256': sha(target)}

    for row in cp['results']:
        trial = {k: row[k] for k in ('id', 'brief', 'repeat', 'condition', 'status', 'order')}
        trial.update(label=label(row), captures=[], retained_version=row.get('retained_version'),
                     completed_stages=row.get('completed_stages', []), run_status=row.get('run_status'))
        trials.append(trial)
        public_base = checkpoint / 'attempts' / row['id']
        if row['status'] == 'pending':
            continue
        report = public_base / 'creator-report.json'
        trial['report'] = {'path': report.relative_to(root).as_posix(), 'sha256': sha(report)}
        private_base = Path(roots[row['id']]).resolve()
        if not private_base.is_relative_to(root / 'work/research32/pilot'):
            raise ValueError('Unexpected private trial root')
        run_path = private_base / 'work/vectorcraft-studio/artwork/run.json'
        if not run_path.is_file():
            continue  # Legitimately never initialized; do not fabricate startup records.
        run = read(run_path)
        summary = read(public_base / 'run-summary.json')
        if sha(run_path) != summary['private_run_sha256']:
            raise ValueError('Run changed since the interim snapshot: ' + row['id'])
        trial['source_run_sha256'] = sha(run_path)
        trial['source_summary'] = {'path': (public_base / 'run-summary.json').relative_to(root).as_posix(), 'sha256': sha(public_base / 'run-summary.json')}
        trial['best_version'] = run.get('best_version')
        trial['working_version'] = run.get('working_version')
        events_path = out / 'attempts' / row['id'] / 'stage-events.json'
        events_path.parent.mkdir(parents=True, exist_ok=True)
        events_path.write_text(encode({'source_run_sha256': sha(run_path), 'events': [
            {k: e[k] for k in ('event', 'at', 'stage', 'version', 'outcome', 'stage_complete') if k in e}
            for e in run.get('events', [])]}), encoding='utf-8', newline='\n')
        trial['source_events'] = {'path': events_path.relative_to(root).as_posix(), 'sha256': sha(events_path)}
        blockout_ids = set()
        directions_at = next((x['at'] for x in run.get('records', []) if x['kind'] == 'directions'), None)
        for record in run.get('records', []):
            if record['kind'] == 'blockout':
                p = safe_artifact(run_path.parent, record['artifact']['path'])
                if p.is_file() and sha(p) == record['artifact']['sha256']:
                    blockout_ids.add(read(p)['study_id'])
        captures = []
        for study_id, study in run.get('design_process', {}).get('studies', {}).items():
            study_base = Path(study['run']).resolve()
            if not study_base.is_relative_to(private_base):
                raise ValueError('Study escapes trial')
            study_run_path = study_base / 'run.json'
            if not study_run_path.is_file():
                continue
            sr = read(study_run_path)
            for version, snap in sr.get('versions', {}).items():
                plan = study.get('plan', {})
                captures.append((snap.get('at', ''), {
                    'id': 'study-' + study_id + '-' + version, 'version': version, 'kind': 'study',
                    'stage': 'roughs' if study_id in blockout_ids or not directions_at or snap.get('at', '') < directions_at else 'construction-study',
                    'study_id': study_id, 'study_closed': study.get('closed', False),
                    'source_run_sha256': sha(study_run_path),
                    'confirmed': bool(snap.get('confirmed')), 'retained_best': False,
                    'working': False, 'selected_for_display': False,
                    'task_outcome': snap.get('task_outcome'),
                    'plan': {k: plan[k] for k in ('purpose', 'changes', 'expected_result', 'checks') if k in plan},
                }, snap, study_base, None))
        for version, snap in run.get('versions', {}).items():
            stage, begin, event_index, event = stage_binding(run, version, snap)
            if stage not in STAGES:
                raise ValueError('Unknown recorded stage: ' + str(stage))
            plan = begin[1].get('plan', {}) if begin else {}
            captures.append((snap.get('at', ''), {
                'id': 'production-' + version, 'version': version, 'kind': 'production', 'stage': stage,
                'confirmed': bool(snap.get('confirmed')), 'retained_best': run.get('best_version') == version,
                'working': run.get('working_version') == version,
                'selected_for_display': row.get('retained_version') == version,
                'task_outcome': snap.get('task_outcome') or event.get('outcome'),
                'stage_complete': event.get('stage_complete'), 'source_run_sha256': sha(run_path),
                'source_begin_event': begin[0] if begin else None, 'source_confirm_event': event_index,
                'plan': {k: plan[k] for k in ('task_id', 'goal', 'purpose', 'changes', 'expected_result', 'preserve', 'checks') if k in plan},
            }, snap, run_path.parent, summary['versions'][version]))
        for order, (at, entry, snap, base, published) in enumerate(sorted(captures, key=lambda c: c[0]), 1):
            entry.update(order=order, at=at, revision=snap.get('revision'), spec_revision=snap.get('spec_revision'))
            entry['images'] = {}
            if published:
                for key, source in zip(('full', 'use'), published.get('images', [])):
                    p = checkpoint / source
                    entry['images'][key] = {'path': p.relative_to(root).as_posix(), 'sha256': sha(p)}
                if published.get('native'):
                    p = checkpoint / published['native']
                    entry['native'] = {'path': p.relative_to(root).as_posix(), 'sha256': sha(p)}
            else:
                dest = Path('attempts') / row['id'] / entry['id']
                entry['native'] = artifact(base, snap.get('native'), dest / 'artwork.vectorcraft')
                for key, source in zip(('full', 'use'), snap.get('images', [])):
                    result = artifact(base, source, dest / (key + '.png'))
                    if result:
                        entry['images'][key] = result
            check = snap.get('check')
            entry['observations'] = {'attribution': 'No recorded confirmation observation for this capture.'}
            if check:
                p = safe_artifact(base, check['path'])
                if p.is_file() and sha(p) == check['sha256']:
                    data = read(p)
                    entry['source_check_sha256'] = sha(p)
                    entry['observations'] = {'attribution': 'Existing creator checkpoint; not a new independent review.',
                        **{k: data[k] for k in ('observations', 'decision', 'reason', 'preservation_observation', 'check_results', 'stage_checks') if k in data}}
                    if not data.get('observations'):
                        entry['observations']['observations'] = data.get('image_inspection', {}).get('observations', [])
                else:
                    omissions.append({'path': entry['id'], 'reason': 'Checkpoint observation absent or changed'})
            trial['captures'].append(scrub(entry, root))
    data = {'format': 'vectorcraft-stage-evidence', 'version': 1, 'date': '2026-10-15',
            'checkpoint': {'path': (checkpoint / 'checkpoint.json').relative_to(root).as_posix(), 'sha256': sha(checkpoint / 'checkpoint.json')},
            'stages': {k: {'title': v[0], 'purpose': v[1]} for k, v in STAGES.items()},
            'limits': ['Existing observations only; no new preference collection or aesthetic ranking.',
                       'Roughs are a separate supplement; the dated checkpoint and paper remain unchanged.',
                       'Production stage assignment follows explicit events and timestamps, never filenames.'],
            'trials': trials, 'omissions': omissions}
    (out / 'index.json').write_text(encode(data), encoding='utf-8', newline='\n')
    (out / 'README.md').write_text('# Stage evidence supplement\n\nAdditional owned native roughs and a source-bound index of existing stage captures. The original 15 October checkpoint is unchanged. No raw sessions, cached references, targets, or private context are included.\n\nSee [progress](../../docs/research/PROGRESS.md) and [index.json](index.json). Captions are recorded creator observations, not new ratings. Missing and unconfirmed captures retain those labels. Source-run and checkpoint hashes identify private originals without distributing their paths.\n', encoding='utf-8')
    validate(root, data)
    return data


def validate(root, data):
    cp = read(safe_artifact(root, data['checkpoint']['path']))
    if sha(safe_artifact(root, data['checkpoint']['path'])) != data['checkpoint']['sha256']:
        raise ValueError('Changed source checkpoint')
    expected = {r['id']: r for r in cp['results']}
    if len(data['trials']) != len(expected) or {t['id'] for t in data['trials']} != set(expected):
        raise ValueError('Missing or duplicate trial rows')
    for trial in data['trials']:
        original = expected[trial['id']]
        if any(trial[k] != original[k] for k in ('brief', 'repeat', 'condition', 'status')):
            raise ValueError('Incorrect trial mapping')
        ids = set()
        events = None
        summary = None
        if trial.get('source_summary'):
            p = safe_artifact(root, trial['source_summary']['path'])
            if sha(p) != trial['source_summary']['sha256']:
                raise ValueError('Changed source run summary')
            summary = read(p)
            versions = [c['version'] for c in trial['captures'] if c['kind'] == 'production']
            if len(versions) != len(set(versions)) or set(versions) != set(summary['versions']):
                raise ValueError('Missing or duplicate production captures')
            if trial.get('best_version') != summary.get('best_version'):
                raise ValueError('Retained best differs from source summary')
        if trial.get('source_events'):
            p = safe_artifact(root, trial['source_events']['path'])
            if sha(p) != trial['source_events']['sha256']:
                raise ValueError('Changed source event extract')
            events = read(p)
        for capture in trial['captures']:
            if capture['id'] in ids or capture['stage'] not in STAGES:
                raise ValueError('Duplicate capture or unknown stage')
            ids.add(capture['id'])
            if capture['kind'] == 'production':
                stage, begin, confirm, event = stage_binding(events, capture['version'], capture)
                if stage != capture['stage'] or confirm != capture['source_confirm_event'] or (begin[0] if begin else None) != capture['source_begin_event']:
                    raise ValueError('Stage mapping does not match recorded events')
                if capture['selected_for_display'] != (capture['version'] == original.get('retained_version')):
                    raise ValueError('Incorrect checkpoint display selection')
                if summary and capture['confirmed'] != bool(summary['versions'][capture['version']]['confirmed']):
                    raise ValueError('Confirmation differs from source capture')
            if capture['retained_best'] and (capture['kind'] != 'production' or capture['version'] != trial.get('best_version') or not capture['confirmed']):
                raise ValueError('Incorrect retained-best label')
            for artifact in [capture.get('native'), *capture['images'].values()]:
                if artifact and sha(safe_artifact(root, artifact['path'])) != artifact['sha256']:
                    raise ValueError('Changed stage artifact')
        if original['status'] == 'pending' and trial['captures']:
            raise ValueError('Pending trial has fabricated captures')
        if trial.get('report') and sha(safe_artifact(root, trial['report']['path'])) != trial['report']['sha256']:
            raise ValueError('Changed source report')


def presentation(data, guide):
    """Add display labels without changing source identities or inferring quality."""
    result = json.loads(json.dumps(data))
    result['profile_names'] = PROFILE_NAMES
    for key, stage in result['stages'].items():
        stage['technical_name'] = stage['title']
        stage['title'] = STAGE_NAMES[key]
    expected = {(t['id'], c['id']) for t in data['trials'] for c in t['captures']}
    entries = {}
    for row in guide['steps']:
        key = (row['trial_id'], row['capture_id'])
        if key in entries:
            raise ValueError('Duplicate step description')
        if not all(isinstance(row.get(k), str) and row[k].strip() for k in ('title', 'change', 'reading')):
            raise ValueError('Incomplete step description')
        entries[key] = row
    if set(entries) != expected:
        raise ValueError('Missing or unknown step descriptions')
    for trial in result['trials']:
        trial['short_id'] = f"T{trial['order']:02}"
        trial['display_name'] = f"{BRIEF_NAMES[trial['brief']]} · {PROFILE_NAMES[trial['condition']]} · Run {trial['repeat']}"
        for number, capture in enumerate(trial['captures'], 1):
            if capture['order'] != number:
                raise ValueError('Step order differs from capture index')
            row = entries[(trial['id'], capture['id'])]
            if row['full_sha256'] != capture['images']['full']['sha256']:
                raise ValueError('Step description image binding changed')
            capture['step'] = f"{trial['short_id']}.{number:02}"
            capture['title'] = row['title']
            capture['change'] = row['change']
            capture['reading'] = row['reading']
            # These labels describe recorded state, never a new visual rating.
            capture['progress_label'] = ('Not confirmed' if not capture['confirmed'] else
                                         'Needs correction' if capture.get('task_outcome') == 'revise' else
                                         'Recorded step')
    return result


def markdown(data):
    lines = ['## All eighteen attempts', '', '| Attempt | Outcome | Available captures |', '| --- | --- | ---: |']
    for t in data['trials']:
        lines.append(f"| [{t['short_id']} — {t['display_name']}](#{t['id']}) | {t['label']} | {len(t['captures'])} |")
    lines += ['', '## Stage-by-stage records', '',
              'Images link to exact stored full/use captures. Captions below quote or summarize existing checkpoint fields. Blank stages are not reconstructed.', '']
    for t in data['trials']:
        lines += [f'<a id="{t["id"]}"></a>', '', f"### {t['short_id']} — {t['display_name']}", '',
                  f"{t['label']}. Source ID: `{t['id']}`.", '']
        if t.get('report'):
            lines += [f"[Creator report](../../{t['report']['path']})", '']
        if not t['captures']:
            lines += ['No captured stages available in this supplement.', '']
        for c in t['captures']:
            flags = ['confirmed' if c['confirmed'] else 'unconfirmed', 'retained best' if c['retained_best'] else 'working at stop' if c['working'] else 'historical capture']
            links = ' · '.join(f"[{k}](../../{v['path']})" for k, v in c['images'].items())
            observation = c['observations'].get('observations') or c['observations'].get('decision') or 'No confirmation observation recorded.'
            if isinstance(observation, list):
                observation = ' '.join(str(x) for x in observation)
            lines += [f"**{c['step']} — {c['title']}** · {data['stages'][c['stage']]['title']} ({', '.join(flags)}). {links}", '',
                      f"**Change / check:** {c['change']}", '', f"**Purpose:** {data['stages'][c['stage']]['purpose']}", '',
                      '**Recorded observation:** ' + str(observation).replace('\n', ' '), '',
                      f"**How to read the progress:** {c['reading']}", '',
                      f"Source version: `{c['version']}`. *{c['observations']['attribution']}*", '']
    return '\n'.join(lines).rstrip() + '\n'


def render(root, supplement, check=False):
    data = read(supplement / 'index.json')
    validate(root, data)
    page_data = presentation(data, read(root / STEP_GUIDE))
    assets = {}
    for trial in page_data['trials']:
        for capture in trial['captures']:
            for image in capture['images'].values():
                source = safe_artifact(root, image['path'])
                target = 'assets/stages/' + image['sha256'] + '.png'
                assets[root / 'site' / target] = source.read_bytes()
                image['site_path'] = target
    payload = encode(page_data)
    assets[root / 'site/assets/stages/index.json'] = payload.encode('utf-8')
    # Embedded JSON also supports file:// inspection without a local data fetch.
    template = (root / 'site/research.template.html').read_text(encoding='utf-8')
    template = template.replace('research.js"', 'research.js?v=' + sha(root / 'site/research.js')[:12] + '"')
    template = template.replace('research.css"', 'research.css?v=' + sha(root / 'site/research.css')[:12] + '"')
    assets[root / 'site/research.html'] = template.replace('<!-- STAGE_DATA -->', payload.replace('<', '\\u003c')).encode('utf-8')
    progress = root / 'docs/research/PROGRESS.md'
    text = progress.read_text(encoding='utf-8')
    begin, end = '<!-- BEGIN GENERATED STAGE INDEX -->', '<!-- END GENERATED STAGE INDEX -->'
    if text.count(begin) != 1 or text.count(end) != 1:
        raise ValueError('Progress guide generated-region markers missing or duplicated')
    updated = text.split(begin)[0] + begin + '\n' + markdown(page_data) + end + text.split(end)[1]
    assets[progress] = updated.encode('utf-8')
    for path, content in assets.items():
        if check:
            if not path.is_file() or path.read_bytes() != content:
                raise ValueError('Generated presentation stale: ' + path.relative_to(root).as_posix())
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
    return {'trials': len(data['trials']), 'captures': sum(len(t['captures']) for t in data['trials']), 'site_images': len(assets) - 3, 'check': check}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='action', required=True)
    e = sub.add_parser('export'); e.add_argument('--roots', required=True); e.add_argument('--out', default=str(SUPPLEMENT))
    e.add_argument('--ledger', default='work/experiments/process-pilot-20261013')
    p = sub.add_parser('render'); p.add_argument('--supplement', default=str(SUPPLEMENT)); p.add_argument('--check', action='store_true')
    args = parser.parse_args()
    if args.action == 'export':
        import sys
        sys.path.insert(0, str(ROOT / 'src'))
        from experiment import Ledger
        ledger = Ledger(ROOT, ROOT / args.ledger)  # Verify original frozen files before reading trials.
        if any(t['status'] == 'building' for t in ledger.data['trials']):
            raise SystemExit('Active builder blocks export')
        data = export(ROOT, ROOT / CHECKPOINT, Path(args.roots), ROOT / args.out)
        print(encode({'trials': len(data['trials']), 'omissions': len(data['omissions'])}))
    else:
        print(encode(render(ROOT, ROOT / args.supplement, args.check)))
