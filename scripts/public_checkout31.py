"""Build an explicit sanitized public tree; local Git history/private evidence stay intact."""
from pathlib import Path
import argparse,hashlib,json,shutil,subprocess
ROOT=Path(__file__).resolve().parents[1];parser=argparse.ArgumentParser();parser.add_argument('--destination',default='work/public-release31');a=parser.parse_args();dest=(ROOT/a.destination).resolve()
assert dest.is_relative_to(ROOT/'work') and dest!=ROOT/'work'
if dest.exists():raise SystemExit('Preserve existing public checkout; use a fresh destination')
dest.mkdir(parents=True)
roots=['src','skills','tests','docs','.github','site','examples','public-evidence'];top=['README.md','LICENSE-MIT','LICENSE-APACHE','NOTICE','ASSETS.md','CONTRIBUTING.md','RELEASE-NOTES.md','.gitignore','.gitattributes','AGENTS.md','requirements-dev.txt']
scripts=['install.py','test_suite.py','validate_skills.py','verify_installation.py','check_public.py','prepare_release.py','activation31.py','public_checkout31.py']
selected=[ROOT/p for p in top]+[ROOT/'scripts'/p for p in scripts]
for folder in roots:selected += [p for p in (ROOT/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc' and not ('legacy' in p.parts and 'result' in p.name)]
selected += [p for p in (ROOT/'benchmarks/briefs31').glob('*.md')]
manifest=[]
for source in sorted(selected):
 if not source.is_file():raise RuntimeError('Required release file missing: '+str(source))
 rel=source.relative_to(ROOT);p=dest/rel;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,p);changed=False
 if rel.as_posix()=='AGENTS.md':p.write_bytes(p.read_bytes().replace(b'Installed Crafting Apps binaries remain under D:\\Crafting Apps.',b'Installed engine binaries remain in their separately configured folders.'));changed=True
 if p.suffix.lower() in ('.py','.md','.json','.toml','.html','.css','.txt','.yml','.yaml','.svg','.vectorcraft','.bib') or p.name in ('LICENSE-MIT','LICENSE-APACHE','NOTICE','.gitignore','.gitattributes'):
  raw=p.read_bytes();normalized=raw.replace(b'\r\n',b'\n');changed=changed or normalized!=raw;p.write_bytes(normalized)
 manifest.append({'path':rel.as_posix(),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'public_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'sanitized_derivative':changed})
(dest/'PUBLIC-PROVENANCE.json').write_text(json.dumps({'description':'Explicit sanitized derivative; private baseline/configuration/vault/run records excluded. Source hashes refer to maintained project artifacts, not private file paths.','files':manifest},indent=2),encoding='utf-8')
subprocess.run(['git','init','--initial-branch=main'],cwd=dest,check=True,capture_output=True)
print(json.dumps({'public_checkout':str(dest),'selected_files':len(selected),'local_history_preserved':True,'push_performed':False}))
