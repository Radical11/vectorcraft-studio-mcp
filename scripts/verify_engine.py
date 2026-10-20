"""Verify/stage the pinned official 0.12 portable release without switching installation."""
import argparse,hashlib,json,shutil,stat,subprocess,zipfile
from pathlib import Path

ARCHIVE='vectorcraft-0.12.0-windows-x64-portable.zip'
EXPECTED='fde42c30d14aadbb565cf0551f72f251321f8c9f875a24811b98e522aea6fe88'
SOURCE='https://github.com/storytold/vectorcraft/releases/tag/v0.12.0'

def sha(stream):
    h=hashlib.sha256()
    for chunk in iter(lambda:stream.read(1024*1024),b''):h.update(chunk)
    return h.hexdigest()

def verify(archive,sums,destination,stage=False):
    with archive.open('rb') as stream:actual=sha(stream)
    lines=[line for line in sums.read_text().splitlines() if line.strip().endswith(ARCHIVE)]
    if actual!=EXPECTED or len(lines)!=1 or lines[0].split()[0]!=EXPECTED:
        raise ValueError('Official pinned archive/checksum mismatch')
    destination=destination.resolve()
    if stage and destination.exists():raise ValueError('Stage only into a new sibling directory; never overwrite an installed engine')
    count=0
    with zipfile.ZipFile(archive) as z:
        members=[]
        for item in z.infolist():
            relative=Path(item.filename).relative_to(ARCHIVE[:-4])
            target=(destination/relative).resolve()
            if not target.is_relative_to(destination) or stat.S_ISLNK(item.external_attr>>16):raise ValueError('Unsafe archive member')
            members.append((item,target))
        if stage:
            for item,target in members:
                if item.is_dir():target.mkdir(parents=True,exist_ok=True)
                else:
                    target.parent.mkdir(parents=True,exist_ok=True)
                    with z.open(item) as packed,target.open('xb') as disk:shutil.copyfileobj(packed,disk)
        for item,target in members:
            if item.is_dir():continue
            with z.open(item) as packed,target.open('rb') as disk:
                if sha(packed)!=sha(disk):raise ValueError('Installed member differs: '+item.filename)
            count+=1
    cli=destination/'vectorcraft-cli.exe'
    with cli.open('rb') as stream:binary=sha(stream)
    version=subprocess.check_output([str(cli),'--version'],text=True).strip()
    if version!='vectorcraft-cli 0.12.0':raise ValueError('Unexpected staged engine version')
    return {'source':SOURCE,'archive':ARCHIVE,'archive_sha256':actual,'members_verified':count,
            'cli_version':version,'cli_sha256':binary,'installation_switched':False}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for key in ('archive','sums','destination','output'):p.add_argument('--'+key,type=Path,required=True)
    p.add_argument('--stage',action='store_true');a=p.parse_args()
    result=verify(a.archive,a.sums,a.destination,a.stage)
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(result,indent=2));print(json.dumps(result))

if __name__=='__main__':main()
