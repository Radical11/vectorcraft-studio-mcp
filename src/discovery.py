"""Bounded executable discovery; never scans drives or changes PATH."""
from pathlib import Path
import json,os,shutil
def executables(cli=None,desktop=None,manifest=None,environ=None):
    env=os.environ if environ is None else environ
    cli=cli or env.get('VECTORCRAFT_CLI');desktop=desktop or env.get('VECTORCRAFT_DESKTOP')
    manifest=manifest or env.get('CRAFTING_APPS_MANIFEST')
    if not cli and not desktop:
        candidate=Path(manifest or r'D:\Crafting Apps\download-manifest.json')
        if candidate.is_file():
            entry=next((e for e in json.loads(candidate.read_text(encoding='utf-8-sig')) if e['App'].casefold()=='vectorcraft'),None)
            if entry:desktop=entry['Executable']
        elif manifest:raise FileNotFoundError('Configured application manifest is missing')
    if cli and not desktop:desktop=str(Path(cli).with_name('vectorcraft.exe'))
    if desktop and not cli:cli=str(Path(desktop).with_name('vectorcraft-cli.exe'))
    if not cli:
        cli=shutil.which('vectorcraft-cli.exe',path=env.get('PATH',''))
        desktop=str(Path(cli).with_name('vectorcraft.exe')) if cli else None
    if not cli:
        folder=Path(env.get('ProgramFiles',r'C:\Program Files'))/'VectorCraft';cli=str(folder/'vectorcraft-cli.exe');desktop=str(folder/'vectorcraft.exe')
    paths=tuple(Path(p).expanduser().resolve() for p in (cli,desktop))
    for label,p in zip(('CLI','desktop'),paths):
        if not p.is_file():raise FileNotFoundError(f'VectorCraft {label} missing: {p}. Supply --cli and --desktop or their environment variables.')
    return paths
