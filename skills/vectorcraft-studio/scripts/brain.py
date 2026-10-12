"""Small Obsidian vault writer: immutable sources, optimistic concurrency, append-only log."""
import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import uuid

KINDS = ('sources', 'principles', 'styles', 'projects', 'lessons')


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


@contextmanager
def lock(vault):
    path = Path(vault) / '.design-brain.lock'
    try:
        fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        raise ValueError('Vault busy: retry after the writer completes; do not erase its lock')
    try:
        os.write(fd, str(os.getpid()).encode()); os.close(fd)
        yield
    finally:
        path.unlink()


def atomic_text(path, text):
    temp = path.with_name(path.name + '.' + uuid.uuid4().hex + '.tmp')
    temp.write_text(text, encoding='utf-8')
    os.replace(temp, path)


def init(vault):
    vault = Path(vault).resolve(); vault.mkdir(parents=True, exist_ok=True)
    with lock(vault):
        for kind in KINDS: (vault / kind).mkdir(exist_ok=True)
        for name, text in {
            'Home.md': '# Design Brain\n\nResearch and design knowledge maintained by VectorCraft Studio.\n\nStart at [[index]]; operating rules are in [[AGENTS]].\n',
            'index.md': '# Design Brain index\n\n',
            'log.md': '# Append-only activity log\n\n',
            '.gitignore': '.obsidian/\n.design-brain.lock\n*.tmp\n',
        }.items():
            if not (vault / name).exists(): (vault / name).write_text(text, encoding='utf-8')
    return str(vault)


def write(vault, kind, name, file, expected=None, context=''):
    vault = Path(vault).resolve()
    if kind not in KINDS or not re.fullmatch(r'[A-Za-z0-9_-]{1,100}', name):
        raise ValueError('Use a known note kind and filename-safe name')
    text = Path(file).read_text(encoding='utf-8-sig')
    if not text.strip(): raise ValueError('Empty notes are not knowledge')
    if kind == 'sources' and not re.search(r'https?://', text):
        raise ValueError('Source records require attribution URL')
    if not (vault / 'Home.md').is_file(): raise ValueError('Initialize the vault first')
    target = (vault / kind / (name + '.md')).resolve()
    if not target.is_relative_to(vault): raise ValueError('Note escapes vault')
    with lock(vault):
        if target.exists():
            if kind == 'sources': raise ValueError('Source records are immutable; add a dated new source')
            if not expected or digest(target) != expected:
                raise ValueError('Note changed: re-read, merge, and supply its current SHA-256')
        elif expected:
            raise ValueError('Expected an existing note; re-read the vault')
        atomic_text(target, text)
        link = f'[[{kind}/{name}]]'
        index = vault / 'index.md'
        if link not in index.read_text(encoding='utf-8'):
            with index.open('a', encoding='utf-8') as stream: stream.write('- ' + link + '\n')
        entry = {'at': datetime.now(timezone.utc).isoformat(), 'note': f'{kind}/{name}.md',
                 'sha256': digest(target), 'context': context.replace('\n', ' ')}
        with (vault / 'log.md').open('a', encoding='utf-8') as stream:
            stream.write('- ' + json.dumps(entry, ensure_ascii=False) + '\n')
    return entry


def search(vault, query):
    words = set(re.findall(r'\w+', query.casefold()))
    matches = []
    for kind in KINDS:
        for file in (Path(vault) / kind).glob('*.md'):
            text = file.read_text(encoding='utf-8')
            score = len(words & set(re.findall(r'\w+', text.casefold())))
            if score: matches.append({'path': str(file.resolve()), 'sha256': digest(file), 'terms_matched': score})
    return sorted(matches, key=lambda m: (-m['terms_matched'], m['path']))[:20]


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--vault', default=r'D:\Design Brain')
    sub = p.add_subparsers(dest='cmd', required=True)
    sub.add_parser('init')
    q = sub.add_parser('write'); q.add_argument('--kind', choices=KINDS, required=True)
    q.add_argument('--name', required=True); q.add_argument('--file', required=True)
    q.add_argument('--expected-sha'); q.add_argument('--context', default='')
    q = sub.add_parser('search'); q.add_argument('--query', required=True)
    a = p.parse_args()
    if a.cmd == 'init': result = init(a.vault)
    elif a.cmd == 'search': result = search(a.vault, a.query)
    else: result = write(a.vault, a.kind, a.name, a.file, a.expected_sha, a.context)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    try: main()
    except (OSError, ValueError) as error: raise SystemExit(str(error))
