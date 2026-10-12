"""Portable owned-section installer. Private snapshots; conflict-aware rollback."""
from pathlib import Path
import argparse,hashlib,json,os,re,shutil,sys,tomllib,uuid
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from discovery import executables
OWNED=('vectorcraft','vectorcraft-studio')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def files(root):return sorted(p for p in Path(root).rglob('*') if p.is_file() and '__pycache__' not in p.parts)
def atomic(p,content):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);temp=p.with_name(p.name+'.'+uuid.uuid4().hex+'.tmp')
    try:temp.write_bytes(content);os.replace(temp,p)
    finally:
        if temp.exists():temp.unlink()
def parse(text):return tomllib.loads(text.lstrip('\ufeff'))
def owned(text):return parse(text).get('mcp_servers',{}).get('vectorcraft')
def others(text):
    data=parse(text);data.get('mcp_servers',{}).pop('vectorcraft',None)
    if data.get('mcp_servers')=={}:data.pop('mcp_servers')
    return data
def value(v):
    if isinstance(v,str):return json.dumps(v,ensure_ascii=False)
    if isinstance(v,bool):return str(v).lower()
    if type(v) in (int,float):return repr(v)
    if isinstance(v,list):return '['+', '.join(value(x) for x in v)+']'
    raise ValueError('Unsupported owned TOML value; nothing changed')
def table(data,path=('mcp_servers','vectorcraft')):
    rows=['['+'.'.join(json.dumps(k) for k in path)+']']
    for k,v in data.items():
        if not isinstance(v,dict):rows.append(json.dumps(k)+' = '+value(v))
    text='\n'.join(rows)+'\n'
    for k,v in data.items():
        if isinstance(v,dict):text+='\n'+table(v,(*path,k))
    return text
def is_owned_header(header):
    try:return '__probe__' in str(parse(header+'\n__probe__ = true').get('mcp_servers',{}).get('vectorcraft',{}))
    except tomllib.TOMLDecodeError:return False
def replace_owned(text,replacement):
    matches=list(re.finditer(r'(?m)^\s*(\[[^\n]+\])[^\n]*\n?',text));pieces=[];cursor=0;found=False
    for i,m in enumerate(matches):
        end=matches[i+1].start() if i+1<len(matches) else len(text)
        if is_owned_header(m.group(1)):pieces.append(text[cursor:m.start()]);cursor=end;found=True
    pieces.append(text[cursor:]);result=''.join(pieces)
    if owned(text) is not None and not found:raise ValueError('Inline VectorCraft configuration needs a dedicated table; nothing changed')
    if replacement is not None:result=result.rstrip()+'\n\n'+table(replacement)
    if others(result)!=others(text):raise ValueError('Unrelated configuration would change')
    return result
def protected(home,path):
    resolved=Path(path).resolve()
    if not resolved.is_relative_to(Path(home).resolve()):raise ValueError('Owned path escapes Codex home')
    return resolved
def install(home,cli,desktop,vault,dry=False,root=ROOT):
    home=Path(home).resolve();root=Path(root).resolve();config=home/'config.toml';text=config.read_text(encoding='utf-8-sig') if config.exists() else ''
    section=dict(owned(text) or {});env=dict(section.get('env',{}))
    env.update(VECTORCRAFT_CLI=str(cli),VECTORCRAFT_DESKTOP=str(desktop),VECTORCRAFT_BRAIN=str(vault))
    section.update(command=sys.executable,args=[str(root/'src/launch_mcp.py'),'vectorcraft'],env=env)
    updated=replace_owned(text,section);targets=[]
    for name in OWNED:
        for p in files(root/'skills'/name):
            dest=protected(home,home/'skills'/name/p.relative_to(root/'skills'/name));targets.append((p,dest))
    if not targets:raise ValueError('Owned skills are missing')
    if dry:return {'valid':True,'action':'install','owned_skill_files':len(targets),'config':str(config)}
    stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ');snapshot=root/'.local/install-snapshots'/stamp;snapshot.mkdir(parents=True)
    before={};after={dest.relative_to(home).as_posix():sha(p) for p,dest in targets}
    existing=[p for name in OWNED for p in files(protected(home,home/'skills'/name))]
    for dest in existing:after.setdefault(dest.relative_to(home).as_posix(),sha(dest))
    for dest in dict.fromkeys([dest for _,dest in targets]+existing):
        rel=dest.relative_to(home).as_posix();before[rel]=sha(dest) if dest.is_file() else None
        if dest.exists():backup=snapshot/'files'/rel;backup.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(dest,backup)
    if config.exists():shutil.copy2(config,snapshot/'config.toml')
    record={'version':2,'codex_home':str(home),'config_existed':config.exists(),'before_section':owned(text),'after_section':section,'before':before,'after':after,'status':'prepared'}
    atomic(snapshot/'manifest.json',json.dumps(record,indent=2).encode());applied=[]
    try:
        for source,dest in targets:atomic(dest,source.read_bytes());applied.append(dest)
        atomic(config,updated.encode());record['status']='installed';atomic(snapshot/'manifest.json',json.dumps(record,indent=2).encode())
        atomic(root/'.local/installation.json',json.dumps({'snapshot':stamp}).encode())
    except Exception:
        for dest in applied:
            rel=dest.relative_to(home).as_posix()
            if dest.exists() and sha(dest)==record['after'][rel]:
                if before[rel] is None:dest.unlink()
                else:atomic(dest,(snapshot/'files'/rel).read_bytes())
        if config.exists() and owned(config.read_text(encoding='utf-8-sig'))==section:
            if record['config_existed']:atomic(config,(snapshot/'config.toml').read_bytes())
            else:atomic(config,replace_owned(config.read_text(encoding='utf-8-sig'),None).encode())
        raise
    return {'action':'install','snapshot':stamp,'owned_skill_files':len(targets),'other_configuration_unchanged':True}
def rollback(root=ROOT,snapshot=None,dry=False):
    root=Path(root).resolve();snaproot=root/'.local/install-snapshots'
    snapshot=snapshot or json.loads((root/'.local/installation.json').read_text())['snapshot'];folder=(snaproot/snapshot).resolve()
    if not folder.is_relative_to(snaproot.resolve()):raise ValueError('Snapshot escapes private snapshot directory')
    record=json.loads((folder/'manifest.json').read_text());home=Path(record['codex_home']).resolve();config=home/'config.toml'
    text=config.read_text(encoding='utf-8-sig') if config.exists() else ''
    if owned(text)!=record['after_section']:raise ValueError('Rollback conflict: VectorCraft configuration changed since installation')
    for rel,expected in record['after'].items():
        p=protected(home,home/rel)
        if not p.is_file() or sha(p)!=expected:raise ValueError('Rollback conflict: owned skill changed: '+rel)
    for rel,expected in record['before'].items():
        if expected is not None and sha(folder/'files'/rel)!=expected:raise ValueError('Snapshot integrity failed')
    updated=replace_owned(text,record['before_section'])
    if dry:return {'valid':True,'action':'rollback','snapshot':snapshot}
    for rel,expected in record['before'].items():
        p=protected(home,home/rel)
        if expected is None:p.unlink()
        else:atomic(p,(folder/'files'/rel).read_bytes())
    if not record['config_existed'] and not parse(updated):config.unlink(missing_ok=True)
    else:atomic(config,updated.encode())
    record['status']='rolled_back';atomic(folder/'manifest.json',json.dumps(record,indent=2).encode())
    return {'action':'rollback','snapshot':snapshot,'other_configuration_unchanged':True}
def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for option in ('cli','desktop','codex-home','vault','snapshot'):parser.add_argument('--'+option)
    parser.add_argument('--rollback',action='store_true');parser.add_argument('--dry-run',action='store_true');a=parser.parse_args()
    if a.rollback:result=rollback(snapshot=a.snapshot,dry=a.dry_run)
    else:
        cli,desktop=executables(a.cli,a.desktop);home=Path(a.codex_home or os.environ.get('CODEX_HOME',Path.home()/'.codex'))
        vault=Path(a.vault or os.environ.get('VECTORCRAFT_BRAIN',Path.home()/'Documents/Design Brain')).resolve();result=install(home,cli,desktop,vault,a.dry_run)
    print(json.dumps(result))
if __name__=='__main__':main()
