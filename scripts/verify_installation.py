"""Exercise real owned-section installation, rollback and reinstallation without baseline files."""
from pathlib import Path
import argparse,json,os,subprocess,sys,tempfile
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from vectorcraft_gateway import NativeMcp
from discovery import executables
from install import files,sha,parse,others
parser=argparse.ArgumentParser();parser.add_argument('--codex-home');parser.add_argument('--vault');parser.add_argument('--fresh',action='store_true');a=parser.parse_args()
temporary=tempfile.TemporaryDirectory(prefix='vectorcraft-install-') if a.fresh else None
pointer=ROOT/'.local/installation.json';previous_pointer=pointer.read_bytes() if pointer.exists() else None
home=Path(temporary.name) if temporary else Path(a.codex_home or os.environ.get('CODEX_HOME',Path.home()/'.codex')).resolve()
vault=Path(a.vault or os.environ.get('VECTORCRAFT_BRAIN',Path.home()/'Documents/Design Brain')).resolve();cli,desktop=executables();config=home/'config.toml';before=config.read_text(encoding='utf-8-sig') if config.exists() else '';before_files={p.relative_to(home).as_posix():sha(p) for name in ('vectorcraft','vectorcraft-studio') for p in files(home/'skills'/name)}
def execute(*extra):
 r=subprocess.run([sys.executable,str(ROOT/'scripts/install.py'),*extra],cwd=ROOT,capture_output=True,text=True,encoding='utf-8',check=True);return json.loads(r.stdout)
def probe():
 section=parse(config.read_text(encoding='utf-8-sig'))['mcp_servers']['vectorcraft'];prior={k:os.environ.get(k) for k in section['env']}
 try:
  os.environ.update(section['env']);c=NativeMcp([section['command'],*section['args']],ROOT)
  try:
   tools=c.request('tools/list',{})['tools'];ids=sorted(t['name'] for t in tools if t['name'].startswith('workflow_'));assert len(ids)==5;assert 'companion' in c.initialize_result['serverInfo']['title'].lower();assert 'designer-v1' in c.initialize_result['instructions'];assert c.request('resources/list',{}) is not None
   return {'workflow_tools':ids,'companion_identity':True,'native_resources_available':True}
  finally:c.close()
 finally:
  for k,v in prior.items():
   if v is None:os.environ.pop(k,None)
   else:os.environ[k]=v
arguments=['--codex-home',str(home),'--cli',str(cli),'--desktop',str(desktop),'--vault',str(vault)]
try:
 installed=execute(*arguments);first=probe();assert others(config.read_text(encoding='utf-8-sig'))==others(before)
 rolled=execute('--rollback','--snapshot',installed['snapshot']);after=config.read_text(encoding='utf-8-sig') if config.exists() else '';assert parse(after)==parse(before)
 for rel,h in before_files.items():assert sha(home/rel)==h
 after_files={p.relative_to(home).as_posix():sha(p) for name in ('vectorcraft','vectorcraft-studio') for p in files(home/'skills'/name)};assert after_files==before_files
 reinstalled=execute(*arguments);second=probe();assert others(config.read_text(encoding='utf-8-sig'))==others(before)
 result={'fresh_home':a.fresh,'installed_probe':first,'rollback_owned_bytes_restored':True,'unrelated_settings_preserved':True,'reinstalled_probe':second,'snapshot':reinstalled['snapshot'],'baseline_access_required':False}
 out=ROOT/'outputs/verification31';out.mkdir(parents=True,exist_ok=True);(out/('fresh-installation.json' if a.fresh else 'installation-rollback.json')).write_text(json.dumps(result,indent=2));print(json.dumps(result))
finally:
 if temporary:
  temporary.cleanup()
  if previous_pointer is None:pointer.unlink(missing_ok=True)
  else:pointer.write_bytes(previous_pointer)
