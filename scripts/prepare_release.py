"""Create a checksummed source package from an explicitly sanitized public checkout."""
from pathlib import Path
import argparse,hashlib,json,subprocess,sys,zipfile
parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');a=parser.parse_args();ROOT=Path(__file__).resolve().parents[1]
if not (ROOT/'PUBLIC-PROVENANCE.json').is_file():raise SystemExit('Package only the explicitly sanitized public checkout created by public_checkout31.py.')
subprocess.run([sys.executable,str(ROOT/'scripts/check_public.py')],check=True,cwd=ROOT)
files=[p for p in ROOT.rglob('*') if p.is_file() and p.relative_to(ROOT).parts[0] not in ('.git','.local','baseline','work','outputs','.venv') and '__pycache__' not in p.parts and p.suffix!='.pyc' and not ('legacy' in p.parts and 'result' in p.name)]
# Public baseline examples belong in the package; only the private baseline root is excluded.
selected=json.loads((ROOT/'PUBLIC-PROVENANCE.json').read_text(encoding='utf-8'))['files'];included={p.relative_to(ROOT).as_posix() for p in files}
for item in selected:
 assert item['path'] in included,'Selected public file omitted: '+item['path']
 assert hashlib.sha256((ROOT/item['path']).read_bytes()).hexdigest()==item['public_sha256'],'Selected file changed after provenance: '+item['path']
if a.check:print(json.dumps({'package_files':len(files),'private_roots_excluded':True}));raise SystemExit
out=ROOT/'outputs/release';out.mkdir(parents=True,exist_ok=True);package=out/'vectorcraft-studio-mcp-v3.1.0-alpha.1.zip'
with zipfile.ZipFile(package,'w',zipfile.ZIP_DEFLATED) as z:
 for p in sorted(files):z.write(p,p.relative_to(ROOT).as_posix())
digest=hashlib.sha256(package.read_bytes()).hexdigest();(out/'SHA256SUMS.txt').write_text(digest+'  '+package.name+'\n',encoding='utf-8')
print(json.dumps({'package':str(package),'sha256':digest,'files':len(files),'publication_performed':False}))
