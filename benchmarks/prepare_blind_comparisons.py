"""Make balanced common-brief image packets after every trial is accounted for.

Copies actual captured bytes; no generated replacements, creator rationale,
condition labels, construction target, or scores enter the neutral packets.
"""
from pathlib import Path
import argparse,json,shutil,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from experiment import Ledger
from workflow import atomic,digest,read

FIELDS={'id','name','kind','text','bounds','children','layers','anchors','closed','visible','locked','fontFamily','fontStyle',
        'artboards','x','y','width','height','overflow','fitScale'}
def structure(value):
 if isinstance(value,list):return [structure(v) for v in value]
 if isinstance(value,dict):return {k:structure(v) for k,v in value.items() if k in FIELDS}
 if isinstance(value,str):
  if ':\\' in value or ':/' in value or 'file://' in value:return '[local resource]'
  for condition in ('designer-process-v1','layout-blockout-v1','designer-v1'):value=value.replace(condition,'[condition omitted]')
 return value

def prepare(folder,roots_path,out):
 ledger=Ledger(ROOT,folder);pairs=ledger.blind_schedule();roots=read(roots_path)['roots'];out=Path(out).resolve()
 if not out.is_relative_to(ROOT/'work/research32'):raise ValueError('Use a normal project-contained evaluation root')
 if out.exists():raise ValueError('Preserve frozen packets; do not silently regenerate')
 out.mkdir(parents=True)
 index=[]
 for number,pair in enumerate(pairs,1):
  dest=out/f'pair-{number:02d}';dest.mkdir()
  brief=next(b for b in ledger.protocol['inputs'] if b['id']==pair['brief'])
  shutil.copy2(ROOT/brief['source']['path'],dest/'brief.md')
  variants={};images=[]
  for label in ('A','B'):
   identifier=pair[label];trial=ledger.trial(identifier);root=Path(roots[identifier]).resolve()
   if not root.is_relative_to(ROOT/'work/research32/pilot'):raise ValueError('Unexpected trial root')
   run_path=root/'work/vectorcraft-studio/artwork/run.json'
   if not run_path.is_file():
    variants[label]={'availability':'No production document available','images':[]};continue
   run=read(run_path);evidence=trial.get('evidence')
   if evidence and digest(ROOT/evidence['path'])!=evidence['sha256']:raise ValueError('Stopped trial evidence changed')
   version=run.get('best_version') or run.get('working_version') or run.get('original_version')
   snapshot=run['versions'].get(version)
   if not snapshot:
    variants[label]={'availability':'No captured production artwork available','images':[]};continue
   variant=dest/label;variant.mkdir();copied=[]
   for i,artifact in enumerate(snapshot['images']):
    source=run_path.parent/artifact['path']
    if digest(source)!=artifact['sha256']:raise ValueError('Captured image changed')
    target=variant/('full.png' if i==0 else 'use.png' if i==1 else f'detail-{i-1}.png')
    shutil.copy2(source,target);copied.append(str(target));images.append(str(target))
   inspection=read(run_path.parent/snapshot['inspection']['path'])
   atomic(variant/'inspection.json',structure(inspection))
   variants[label]={'availability':'Retained production capture' if version!=run.get('original_version') else 'Original production capture only',
    'images':copied,'structure':str(variant/'inspection.json')}
  packet={'id':dest.name,'brief':str(dest/'brief.md'),'variants':variants,'required_image_paths':images,
   'evaluation':'Common-brief suitability, consequential defects and separate dimensions; no target fidelity scoring',
   'response':{'winner':'A|B|equal|cannot_assess','visible_reason':'actual image observations',
    'consequential_regression':{'present':'boolean','variant':'A|B|neither','evidence':'visible consequential loss'},
    'dimensions':'communication, typography/layout, imagery/craft, cohesion, distinctiveness, production/editability',
    'image_actions':'actual tool/action/path records; every available full/use image must be viewed',
    'limitations':'required, including missing evidence and shared weaknesses'}}
  atomic(dest/'packet.json',packet);index.append({'id':dest.name,'packet':str(dest/'packet.json')})
 atomic(out/'index.json',index)
 return {'pairs':len(index),'neutral_index':str(out/'index.json'),'private_map':str(ledger.folder/'blind-map-private.json')}

if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--experiment',required=True)
 parser.add_argument('--roots',required=True);parser.add_argument('--out',required=True);args=parser.parse_args()
 print(json.dumps(prepare(args.experiment,args.roots,args.out),indent=2))
