"""Copy committed public inputs into a clean existing Git checkout.

No config/vault reads, Git pushes, engine calls, paper rebuilds, or hand-authored
page replacement. Only the explicit stage generated region/template is rendered.
"""
from pathlib import Path
import argparse
import hashlib
import json
import re
import subprocess

from build_stage_evidence import ROOT, SUPPLEMENT, CHECKPOINT, encode, read, render, sha

TEXT = {'.py', '.md', '.json', '.toml', '.html', '.css', '.txt', '.yml', '.yaml', '.svg', '.bib', '.mjs', '.ps1'}
TOP = {'README.md', 'LICENSE-MIT', 'LICENSE-APACHE', 'NOTICE', 'ASSETS.md', 'CONTRIBUTING.md',
       'CHANGELOG.md', 'RELEASE-NOTES.md', '.gitignore', '.gitattributes', 'AGENTS.md', 'requirements-dev.txt'}
PUBLIC_SCRIPTS = {'install.py', 'test_suite.py', 'validate_skills.py', 'verify_installation.py',
                  'check_public.py', 'prepare_release.py', 'activation31.py', 'public_checkout31.py',
                  'export_interim_study.py', 'build_stage_evidence.py', 'stage_public.py', 'README.md'}
PUBLIC_BENCH = {'process_host.py', 'edit_host.py', 'prepare_process_pilot.py', 'prepare_blind_comparisons.py',
                'prepare_edit_tasks.py', 'collect_process_results.py', 'assess_process_pilot.py', 'README.md'}
PROTECTED = ('docs/peer-review/', 'docs/research/editions/',
             'public-evidence/process-study-20261015/', 'public-evidence/process-calibration-20261015/')


def git(root, *args):
    return subprocess.check_output(['git', *args], cwd=root, text=True, encoding='utf-8').strip()


def selected(path):
    parts = Path(path).parts
    if '__pycache__' in parts or path.endswith('.pyc') or ('legacy' in parts and 'result' in parts[-1]):
        return False
    if path.startswith('docs/peer-review/'):
        return False  # Preserve the already published historical edition byte-for-byte.
    if path in TOP:
        return True
    if parts[0] == 'scripts':
        return parts[-1] in PUBLIC_SCRIPTS
    if parts[0] == 'benchmarks':
        return parts[-1] in PUBLIC_BENCH or (len(parts) == 3 and parts[1] in ('briefs31', 'briefs32') and path.endswith('.md'))
    return parts[0] in {'src', 'skills', 'tests', 'docs', '.github', 'site', 'examples', 'public-evidence'}


def public_bytes(path, content):
    if path == 'AGENTS.md':
        content = content.replace(b'Installed Crafting Apps binaries remain under D:\\Crafting Apps.',
                                  b'Installed engine binaries remain in their separately configured folders.')
    if Path(path).suffix.lower() in TEXT or path in TOP:
        text = content.decode('utf-8').replace('\r\n', '\n')
        text = re.sub(r'D:[/\\]+vectorcraftmcp', 'PROJECT_ROOT', text, flags=re.I)
        text = re.sub(r'D:[/\\]+Design Brain', '[private vault path withheld]', text, flags=re.I)
        text = re.sub(r'C:[/\\]+Users[/\\]+[^/\\\s]+', '[private user path withheld]', text, flags=re.I)
        content = text.encode('utf-8')
    return content


def snapshot_audit(root):
    """Additive disclosure; never rewrite the original checkpoint's inner manifest."""
    rows = []
    for entry in read(root / CHECKPOINT / 'artifact-manifest.json')['files']:
        rel = (CHECKPOINT / entry['path']).as_posix()
        original = (root / rel).read_bytes()
        actual = hashlib.sha256(public_bytes(rel, original)).hexdigest()
        if actual != entry['public_sha256']:
            rows.append({'path': rel, 'original_inner_manifest_sha256': entry['public_sha256'],
                         'published_sha256': actual})
    return {'format': 'vectorcraft-publication-redaction-audit', 'date': '2026-10-15',
            'reason': 'The initial public staging normalized JSON line endings and redacted paths after the inner manifest was created. The original snapshot is retained unchanged. These are byte-provenance corrections, not changed study outcomes.',
            'authoritative_public_files': 'PUBLIC-PROVENANCE.json and the public hashes below', 'files': rows}


def stage(root, destination, dry_run=False):
    root, destination = root.resolve(), destination.resolve()
    if not destination.is_relative_to(root / 'work') or destination == root / 'work' or not (destination / '.git').is_dir():
        raise ValueError('Use an existing Git checkout below work/')
    if git(root, 'status', '--porcelain'):
        raise ValueError('Commit intended source changes before staging')
    if git(destination, 'status', '--porcelain'):
        raise ValueError('Destination has uncommitted changes; inspect them before staging')
    paths = [p for p in git(root, 'ls-files').splitlines() if selected(p)]
    copies = {p: public_bytes(p, (root / p).read_bytes()) for p in paths}
    preserved = {p.relative_to(destination).as_posix(): sha(p) for prefix in PROTECTED
                 for p in (destination / prefix).rglob('*') if p.is_file()}
    for rel, content in copies.items():
        if rel in preserved and hashlib.sha256(content).hexdigest() != preserved[rel]:
            raise ValueError('Refusing to rewrite a dated public snapshot: ' + rel)
    if dry_run:
        return {'selected_files': len(paths), 'preserved_files': len(preserved), 'writes': False}
    for rel, content in copies.items():
        p = destination / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(content)
    # Bind the new supplemental index to actual sanitized public bytes while
    # retaining its original source digest. Old snapshot records are never edited.
    index_path = destination / SUPPLEMENT / 'index.json'
    data = read(index_path)
    def refresh(value):
        if isinstance(value, dict):
            if 'path' in value and 'sha256' in value:
                p = (destination / value['path']).resolve()
                if not p.is_relative_to(destination):
                    raise ValueError('Reference escaped publication')
                actual = sha(p)
                if actual != value['sha256']:
                    value.setdefault('source_sha256', value['sha256'])
                    value['sha256'] = actual
            for x in value.values():
                refresh(x)
        elif isinstance(value, list):
            for x in value:
                refresh(x)
    refresh(data)
    index_path.write_bytes(encode(data).encode('utf-8'))
    render(destination, destination / SUPPLEMENT)
    for rel, digest in preserved.items():
        if sha(destination / rel) != digest:
            raise ValueError('Historical artifact changed: ' + rel)
    all_paths = set(git(destination, 'ls-files').splitlines()) | set(paths)
    all_paths.update(p.relative_to(destination).as_posix() for p in (destination / 'site/assets/stages').glob('*') if p.is_file())
    manifest = []
    for rel in sorted(all_paths - {'PUBLIC-PROVENANCE.json'}):
        p = destination / rel
        original = root / rel
        if not p.is_file():
            raise ValueError('Unexpected missing public file: ' + rel)
        source_hash = sha(original) if original.is_file() else sha(p)
        manifest.append({'path': rel, 'source_sha256': source_hash, 'public_sha256': sha(p),
                         'sanitized_derivative': source_hash != sha(p)})
    (destination / 'PUBLIC-PROVENANCE.json').write_bytes(encode({
        'description': 'Explicit sanitized derivative; historical snapshots preserved; new stage references bind actual public bytes.',
        'files': manifest}).encode('utf-8'))
    return {'selected_files': len(paths), 'preserved_files': len(preserved), 'public_files': len(manifest), 'writes': True}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='action', required=True)
    p = sub.add_parser('stage'); p.add_argument('--destination', required=True); p.add_argument('--dry-run', action='store_true')
    sub.add_parser('audit')
    args = parser.parse_args()
    if args.action == 'audit':
        result = snapshot_audit(ROOT)
        (ROOT / SUPPLEMENT / 'publication-audit.json').write_bytes(encode(result).encode('utf-8'))
        print(encode({'disclosed_inner_manifest_differences': len(result['files'])}))
    else:
        print(encode(stage(ROOT, Path(args.destination), args.dry_run)))
