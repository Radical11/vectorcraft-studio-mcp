"""Prepare neutral, separate native copies for the frozen standardized edits."""
from pathlib import Path
import argparse,json,random,shutil,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from experiment import Ledger
from workflow import atomic,digest,read

def prepare(folder,roots_path,out):
 ledger=Ledger(ROOT,folder);roots=read(roots_path)['roots'];out=Path(out).resolve()
 if any(t['status'] in ('pending','building') for t in ledger.data['trials']):raise ValueError('Account for every build first')
 if not out.is_relative_to(ROOT/'work/research32/editing'):raise ValueError('Use isolated editing roots')
 if out.exists():raise ValueError('Preserve existing edit attempts and budgets')
 out.mkdir(parents=True);trials=list(ledger.data['trials']);random.Random(ledger.protocol['seed']+2).shuffle(trials)
 mapping=[];index=[]
 for number,trial in enumerate(trials,1):
  label=f'edit-{number:02d}';dest=out/label;dest.mkdir();root=Path(roots[trial['id']]).resolve()
  if not root.is_relative_to(ROOT/'work/research32/pilot'):raise ValueError('Unexpected construction root')
  brief=next(b for b in ledger.protocol['inputs'] if b['id']==trial['brief'])
  shutil.copy2(ROOT/brief['source']['path'],dest/'brief.md')
  run_path=root/'work/vectorcraft-studio/artwork/run.json'
  run=read(run_path) if run_path.is_file() else None
  if trial.get('evidence') and digest(ROOT/trial['evidence']['path'])!=trial['evidence']['sha256']:raise ValueError('Stopped build changed')
  version=(run.get('best_version') or run.get('working_version')) if run else None
  snapshot=run['versions'].get(version) if version else None
  if not snapshot:
   atomic(dest/'completion-report.json',{'status':'unavailable','reason':'No constructed production capture for standardized editing','editing_allowance_used':False})
   index.append({'id':label,'root':str(dest),'status':'unavailable'})
  else:
   source=run_path.parent/snapshot['native']['path']
   if digest(source)!=snapshot['native']['sha256']:raise ValueError('Captured native changed')
   shutil.copy2(source,dest/'source.vectorcraft')
   (dest/'before').mkdir()
   for i,artifact in enumerate(snapshot['images']):
    image=run_path.parent/artifact['path']
    if digest(image)!=artifact['sha256']:raise ValueError('Captured source preview changed')
    shutil.copy2(image,dest/'before'/('full.png' if i==0 else 'use.png' if i==1 else f'detail-{i-1}.png'))
   text=(dest/'brief.md').read_text(encoding='utf-8-sig')
   task=text.split('Subsequent standardized edit task:',1)[-1].strip()
   (dest/'task.md').write_text(task+'\n',encoding='utf-8')
   atomic(dest/'binding.json',{'native':{'path':'source.vectorcraft','sha256':digest(dest/'source.vectorcraft')},
    'scope':task,'use_width':brief['use_width'],'limits':{'active_seconds':600,'batches':4},
    'instruction':'Native/brief only; no creator process records or scripts. Observe before/after and preserve unrelated content.'})
   index.append({'id':label,'root':str(dest),'status':'pending'})
  mapping.append({'id':label,'trial':trial['id'],'source_version':version})
 atomic(out/'index.json',index);atomic(ledger.folder/'edit-map-private.json',mapping)
 return {'tasks':len(index),'neutral_index':str(out/'index.json'),'unavailable':sum(i['status']=='unavailable' for i in index)}

if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--experiment',required=True)
 parser.add_argument('--roots',required=True);parser.add_argument('--out',required=True);args=parser.parse_args()
 print(json.dumps(prepare(args.experiment,args.roots,args.out),indent=2))
