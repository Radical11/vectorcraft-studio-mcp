"""Immutable design evidence and bounded review ledger; no aesthetic grading."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import sys
import uuid

sys.path.insert(0, str(Path(__file__).parent))
import pipeline

CRITERIA = ('brief', 'composition', 'alignment', 'typography', 'color', 'style', 'distinctiveness', 'craft')


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def atomic(path, value):
    path = Path(path)
    temporary = path.with_name(path.name + '.' + uuid.uuid4().hex + '.tmp')
    temporary.write_text(json.dumps(value, indent=2, ensure_ascii=False), encoding='utf-8')
    os.replace(temporary, path)


def load(run):
    run = Path(run).resolve()
    state = read(run / 'run.json')
    root = Path(state['project_root']).resolve()
    if not run.is_relative_to(root / 'work' / 'vectorcraft-studio'):
        raise ValueError('Run resolves outside the project studio folder')
    for artifact in [state['brief'], *[a for v in state['versions'].values() for a in v['artifacts']], *pipeline.integrity_artifacts(state)]:
        path = (run / artifact['path']).resolve()
        if not path.is_relative_to(run) or digest(path) != artifact['sha256']:
            raise ValueError('Snapshot integrity check failed: ' + artifact['path'])
    for item in state['reviews']:
        path = (run / item['path']).resolve()
        if not path.is_relative_to(run) or digest(path) != item['sha256']:
            raise ValueError('Review integrity check failed: ' + item['path'])
    return run, state


def artifact(run, path, role):
    return {'role': role, 'path': str(path.relative_to(run)), 'sha256': digest(path)}


def init(root, run_id, brief, max_rounds=3):
    root = Path(root).resolve()
    if not re.fullmatch(r'[a-zA-Z0-9_-]{1,80}', run_id):
        raise ValueError('Run id must be a short filename-safe identifier')
    if not 1 <= max_rounds <= 20:
        raise ValueError('Revision budget must be 1..20')
    run = (root / 'work' / 'vectorcraft-studio' / run_id).resolve()
    if not run.is_relative_to(root):
        raise ValueError('Studio folder resolves outside the project')
    source = Path(brief).resolve()
    if not source.is_relative_to(root) or not source.is_file():
        raise ValueError('Brief must be a file inside the project')
    run.mkdir(parents=True, exist_ok=False)
    shutil.copy2(source, run / 'brief.md')
    state = {'format': 'vectorcraft-studio-run', 'version': 1, 'project_root': str(root),
             'brief': artifact(run, run / 'brief.md', 'brief'), 'max_rounds': max_rounds,
             'revision_rounds': 0, 'no_improvement_streak': 0, 'best_version': None,
             'status': 'active', 'stop_reason': None, 'versions': {}, 'reviews': []}
    atomic(run / 'run.json', state)
    return run, state


def snapshot(run, version, native, images, inspection, role='working'):
    run, state = load(run)
    pipeline.assert_snapshot(state, role)
    if not re.fullmatch(r'[a-zA-Z0-9_-]{1,64}', version) or version in state['versions']:
        raise ValueError('Version name is invalid or already exists; snapshots cannot be overwritten')
    if len(images) < 2:
        raise ValueError('Supply full and intended-size/thumbnail images')
    root = Path(state['project_root'])
    sources = [Path(p).resolve() for p in [native, *images, inspection]]
    if any(not p.is_relative_to(root) or not p.is_file() for p in sources):
        raise ValueError('Evidence must be files inside the current project')
    if read(sources[0]).get('format') != 'vectorcraft':
        raise ValueError('Editable original must be a native VectorCraft document')
    read(sources[-1])
    if any(not p.read_bytes().startswith(b'\x89PNG\r\n\x1a\n') for p in sources[1:-1]):
        raise ValueError('Review images must be PNG renders')
    target = (run / 'versions' / version).resolve()
    if not target.is_relative_to(run):
        raise ValueError('Version folder resolves outside the run')
    target.mkdir(parents=True, exist_ok=False)
    artifacts = []
    destinations = [('artwork.vectorcraft', 'native'), *[(f'image-{i:02}.png', 'image') for i in range(len(images))], ('inspection.json', 'inspection')]
    for source, (name, artifact_role) in zip(sources, destinations):
        dest = target / name
        shutil.copy2(source, dest)
        artifacts.append(artifact(run, dest, artifact_role))
    state['versions'][version] = {'artifacts': artifacts}
    if state['version'] == 2:
        state['versions'][version]['at'] = pipeline.now()
        state['versions'][version]['role'] = role
        if role == 'original': state['workflow']['original_version'] = version
    atomic(run / 'run.json', state)
    return state


def validate_review(review, expected_images):
    seen = review.get('image_inspection', {})
    if seen.get('performed') is not True or not seen.get('observations') or not all(isinstance(x, str) and x.strip() for x in seen['observations']):
        raise ValueError('Review lacks actual image-inspection evidence')
    seen_paths = {str(Path(p).resolve()) for p in seen.get('paths', [])}
    if not set(expected_images).issubset(seen_paths):
        # Neutral review packets contain byte-identical copies with no version history.
        remaining = list(seen_paths)
        for expected in expected_images:
            matching = next((p for p in remaining if Path(p).is_file() and digest(p) == digest(expected)), None)
            if matching is None:
                raise ValueError('Reviewer must inspect full and use-size evidence for each compared version')
            remaining.remove(matching)
    scores = review.get('scores', {})
    if set(scores) != set(CRITERIA):
        raise ValueError('All eight rubric criteria are required')
    applicable = []
    for item in scores.values():
        score = item.get('score')
        if not isinstance(item.get('reason'), str) or not item['reason'].strip():
            raise ValueError('Every criterion needs an evidence-based reason, including N/A')
        if score is not None:
            if type(score) is not int or score not in range(1, 6):
                raise ValueError('Scores must be integers 1..5 or null')
            applicable.append(score)
    if not applicable:
        raise ValueError('At least one criterion must apply')
    findings = review.get('findings')
    if not isinstance(findings, list):
        raise ValueError('Findings must be a list')
    for f in findings:
        if f.get('criterion') not in CRITERIA or f.get('severity') not in ('critical', 'major', 'minor', 'preference'):
            raise ValueError('Invalid finding criterion/severity')
        if any(not isinstance(f.get(k), str) or not f[k].strip() for k in ('location', 'evidence', 'impact', 'fix')):
            raise ValueError('Findings require location, evidence, impact and correction')
    comparison = review.get('comparison', {})
    if comparison.get('winner') not in ('no_baseline', 'candidate', 'incumbent', 'equal') or not comparison.get('reason'):
        raise ValueError('Review requires a comparison verdict and reason')
    if not isinstance(review.get('summary'), str) or not review['summary'].strip():
        raise ValueError('Review requires a summary')
    return all(s >= 4 for s in applicable) and not any(f['severity'] in ('critical', 'major') for f in findings)


def review_packet(run, version, other=None):
    run, state = load(run)
    if state['version'] == 2: pipeline.assert_review(state, version)
    incumbent = other or state['best_version'] or (state.get('workflow', {}).get('original_version'))
    versions = [version] + ([incumbent] if incumbent and incumbent != version else [])
    if any(v not in state['versions'] for v in versions):
        raise ValueError('Unknown packet version')
    packet = (run / 'review-packets' / uuid.uuid4().hex[:12]).resolve()
    if not packet.is_relative_to(run):
        raise ValueError('Review packet resolves outside run')
    packet.mkdir(parents=True, exist_ok=False)
    shutil.copy2(run / state['brief']['path'], packet / 'brief.md')
    result = {'packet': str(packet), 'brief': str(packet / 'brief.md'), 'candidate': 'A', 'incumbent': 'B' if len(versions)>1 else None, 'evidence': {}}
    for label, v in zip(['A','B'], versions):
        target = packet / label
        target.mkdir()
        result['evidence'][label] = []
        for a in state['versions'][v]['artifacts']:
            if a['role'] in ('image','inspection'):
                dest = target / Path(a['path']).name
                if a['role'] == 'inspection':
                    inspection = read(run / a['path'])
                    atomic(dest, {k: inspection[k] for k in ('artboards', 'layers', 'objects', 'colorMode', 'units') if k in inspection})
                else:
                    shutil.copy2(run / a['path'], dest)
                result['evidence'][label].append(str(dest))
    return result


def record_review(run, version, review, kind, images_verified=False):
    run, state = load(run)
    pipeline.assert_review(state, version)
    if not images_verified:
        raise ValueError('Parent must verify reviewer image tool use before recording a review')
    if state['status'] != 'active':
        raise ValueError('Run has stopped; extend only after an explicit user request')
    if version not in state['versions'] or any(x['version'] == version for x in state['reviews']):
        raise ValueError('Unknown or already reviewed version')
    first = state['best_version'] is None
    incumbent = state['best_version'] or state.get('workflow', {}).get('original_version')
    if (kind == 'initial') != first:
        raise ValueError('Use initial for the first selected baseline, revision afterward')
    compared = [version] + ([incumbent] if incumbent else [])
    expected = [str((run / a['path']).resolve()) for v in compared for a in state['versions'][v]['artifacts'] if a['role'] == 'image']
    passed = validate_review(review, expected)
    winner = review['comparison']['winner']
    if (incumbent is None) != (winner == 'no_baseline'):
        raise ValueError('Initial review has no baseline; revisions must compare to the best version')
    added_major = False
    original_passed = False
    if incumbent:
        if first:
            earlier = review.get('incumbent_assessment')
            if not isinstance(earlier, dict):
                raise ValueError('First comparison requires a complete independent assessment of the preserved original')
            original_images = [str((run / a['path']).resolve()) for a in state['versions'][incumbent]['artifacts'] if a['role'] == 'image']
            original_passed = validate_review(earlier, original_images)
            if earlier['comparison']['winner'] != 'no_baseline':
                raise ValueError('Original assessment itself must use no_baseline')
        else:
            previous = next(x for x in reversed(state['reviews']) if x['version'] == incumbent)
            earlier = read(run / previous['path'])
        old_issues = {(f['criterion'], f['location']) for f in earlier['findings'] if f['severity'] in ('critical', 'major')}
        new_issues = {(f['criterion'], f['location']) for f in review['findings'] if f['severity'] in ('critical', 'major')}
        added_major = bool(new_issues - old_issues)
    accepted = incumbent is None or (winner == 'candidate' and not added_major)
    if accepted:
        state['best_version'] = version
    if kind == 'revision':
        state['revision_rounds'] += 1
        state['no_improvement_streak'] = 0 if accepted else state['no_improvement_streak'] + 1
    review_dir = (run / 'reviews').resolve()
    if not review_dir.is_relative_to(run):
        raise ValueError('Reviews folder resolves outside the run')
    review_dir.mkdir(exist_ok=True)
    path = review_dir / f'{len(state["reviews"]):02}-{version}.json'
    if path.exists():
        raise ValueError('Review already exists')
    if first and incumbent:
        original_path = review_dir / f'original-{incumbent}.json'
        atomic(original_path, earlier)
        state['reviews'].append({'version': incumbent, 'kind': 'preserved_original_final',
            'path': str(original_path.relative_to(run)), 'sha256': digest(original_path),
            'accepted_as_best': not accepted, 'candidate_passed': original_passed, 'parent_verified_images': True})
        if not accepted: state['best_version'] = incumbent
    atomic(path, review)
    state['reviews'].append({'version': version, 'kind': kind, 'path': str(path.relative_to(run)), 'sha256': digest(path), 'accepted_as_best': accepted, 'candidate_passed': passed, 'parent_verified_images': True})
    if (accepted and passed) or (first and incumbent and not accepted and original_passed):
        state['status'], state['stop_reason'] = 'review_passed', 'Applicable scores >=4 with no major/critical findings'
    elif state['no_improvement_streak'] >= 2:
        state['status'], state['stop_reason'] = 'stalled', 'Two consecutive revisions offered no clear net improvement'
    elif state['revision_rounds'] >= state['max_rounds']:
        state['status'], state['stop_reason'] = 'budget_exhausted', 'Revision budget reached; retain best available version'
    atomic(run / 'run.json', state)
    return state


def main():
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, 'reconfigure'):
            stream.reconfigure(encoding='utf-8')
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    p = sub.add_parser('init', help='Create a run and immutable brief')
    p.add_argument('--project-root', required=True)
    p.add_argument('--run-id', default=uuid.uuid4().hex[:12])
    p.add_argument('--brief', required=True)
    p.add_argument('--max-rounds', type=int, default=3)
    p.add_argument('--legacy', action='store_true', help='Explicitly create a version-one run for compatibility only')
    p = sub.add_parser('snapshot', help='Copy native file, >=2 PNGs and inspection into an immutable version')
    p.add_argument('--run', required=True)
    p.add_argument('--version', required=True)
    p.add_argument('--native', required=True)
    p.add_argument('--images', nargs='+', required=True)
    p.add_argument('--inspection', required=True)
    p.add_argument('--role', choices=['working', 'original'], default='working')
    p = sub.add_parser('review', help='Record independent critique, compare best and enforce stop rules')
    p.add_argument('--run', required=True)
    p.add_argument('--version', required=True)
    p.add_argument('--review', required=True)
    p.add_argument('--kind', choices=['initial', 'revision'], required=True)
    p.add_argument('--images-verified', action='store_true', help='Parent verified the reviewer used an image-inspection tool')
    p = sub.add_parser('status', help='Verify integrity and report resume state')
    p.add_argument('--run', required=True)
    p = sub.add_parser('packet', help='Copy review evidence into neutral A/B folders without version history')
    p.add_argument('--run', required=True)
    p.add_argument('--version', required=True)
    p.add_argument('--other', help='Optional other saved concept for initial concept selection')
    p = sub.add_parser('unavailable', help='Stop honestly when independent review cannot be completed')
    p.add_argument('--run', required=True)
    p.add_argument('--reason', required=True)
    p = sub.add_parser('extend', help='Add revision budget ONLY after explicit user request')
    p.add_argument('--run', required=True)
    p.add_argument('--rounds', type=int, required=True)
    args = parser.parse_args()
    if args.command == 'init':
        factory = init if args.legacy else lambda *a: pipeline.init_v2(sys.modules[__name__], *a)
        run, state = factory(args.project_root, args.run_id, args.brief, args.max_rounds)
    elif args.command == 'snapshot':
        run = Path(args.run).resolve()
        state = snapshot(run, args.version, args.native, args.images, args.inspection, args.role)
    elif args.command == 'review':
        run = Path(args.run).resolve()
        state = record_review(run, args.version, read(args.review), args.kind, args.images_verified)
    elif args.command == 'packet':
        print(json.dumps(review_packet(args.run, args.version, args.other), indent=2))
        return
    else:
        run, state = load(args.run)
        if args.command == 'unavailable':
            state['status'], state['stop_reason'] = 'review_unavailable', args.reason
            atomic(run / 'run.json', state)
        elif args.command == 'extend':
            if not 1 <= args.rounds <= 20:
                raise ValueError('Extra budget must be 1..20')
            state['max_rounds'] = state['revision_rounds'] + args.rounds
            state['status'], state['stop_reason'], state['no_improvement_streak'] = 'active', None, 0
            atomic(run / 'run.json', state)
    print(json.dumps({'run': str(run), **state}, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, KeyError, TypeError) as error:
        print(json.dumps({'error': str(error)}), file=sys.stderr)
        sys.exit(1)
