"""Freeze approved inputs and isolated roots before the first held-out build.

Requires a project-local, attributed reference pack. Does not download artwork,
start builders, edit configuration, or manufacture experiment outcomes.
"""
from pathlib import Path
import argparse,json,shutil,subprocess,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from experiment import create,Ledger
from workflow import atomic,digest

def prepare(name,pack,model,effort,context):
 pack=Path(pack).resolve()
 if not pack.is_relative_to(ROOT) or not (pack/'reference-metadata.json').is_file():
  raise ValueError('Use an attributed project-local reference pack')
 metadata=json.loads((pack/'reference-metadata.json').read_text(encoding='utf-8-sig'))
 images=sorted((pack/'references').iterdir())
 if not images or any(not p.is_file() for p in images):raise ValueError('Reference images required')
 if any(not Path(r['image']).is_file() for r in metadata):raise ValueError('Reference metadata image missing')
 context=Path(context).resolve()
 if not context.is_relative_to(ROOT) or not context.is_file():raise ValueError('Use a frozen project-local common context')
 if not context.with_name('context-provenance.json').is_file():raise ValueError('Frozen common context requires its provenance record')
 status=subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True)
 if status.strip():raise ValueError('Commit reviewable source changes before freezing the pilot')
 commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
 base=ROOT/'work/research32/pilot'/name
 if base.exists():raise ValueError('Preserve previous pilot roots')
 # Frozen source includes deployable instructions and host policy, not private config.
 tracked=subprocess.check_output(['git','ls-files'],cwd=ROOT,text=True).splitlines()
 code=[ROOT/p for p in tracked if p.startswith(('src/','skills/','benchmarks/'))]
 briefs=[{'id':identifier,'genre':genre,'path':str(ROOT/'benchmarks/briefs32'/filename),'use_width':width}
  for identifier,genre,filename,width in [('exchange','poster','book-exchange.md',450),
   ('tyre','illustration','tyre-repair.md',768),('library','information','library-paths.md',600)]]
 base.mkdir(parents=True)
 atomic(base/'environment.json',{'code_commit':commit,'model':model,'reasoning_effort':effort,
  'python':sys.version,'settings_provenance':'root turn metadata; builders inherit without overrides',
  'per_agent_model_receipt':'record when exposed; missing receipts are disclosed',
  'reference_status':'cached attributed works; each builder must actually view them',
  'reference_count':len(images),'token_telemetry':'unavailable unless host exposes receipts'})
 folder=create(ROOT,name,briefs,[pack/'reference-metadata.json',*images],model,
  locked_files=[*code,base/'environment.json',ROOT/'docs/research/PROTOCOL.md',context,context.with_name('context-provenance.json')])
 ledger=Ledger(ROOT,folder)
 for trial in ledger.data['trials']:
  brief=next(b for b in briefs if b['id']==trial['brief'])
  dest=base/trial['id'];dest.mkdir();(dest/'references').mkdir()
  shutil.copy2(brief['path'],dest/'brief.md')
  shutil.copy2(context,dest/'common-context.md')
  for image in images:shutil.copy2(image,dest/'references'/image.name)
  refs=[]
  for ref in metadata:
   item={**ref,'image':str(dest/'references'/Path(ref['image']).name)}
   item.pop('visual_inspection',None)
   item['status']='Cached metadata; fresh actual viewing required by this builder'
   refs.append(item)
  atomic(dest/'reference-metadata.json',refs)
  inputs=[{'path':str(p.relative_to(dest)),'sha256':digest(p)} for p in
   [dest/'brief.md',dest/'common-context.md',dest/'reference-metadata.json',*sorted((dest/'references').iterdir())]]
  atomic(dest/'binding.json',{'phase':'held-out','profile':trial['condition'],'use_width':brief['use_width'],
   'experiment':str(folder),'trial':trial['id'],'inputs':inputs})
 atomic(base/'trial-roots.json',{'experiment':str(folder),'code_commit':commit,
  'roots':{t['id']:str(base/t['id']) for t in ledger.data['trials']}})
 return {'experiment':str(folder),'roots':str(base/'trial-roots.json'),'code_commit':commit,'trials':18}

if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--name',required=True)
 parser.add_argument('--reference-pack',required=True);parser.add_argument('--model',required=True)
 parser.add_argument('--effort',required=True)
 parser.add_argument('--context',required=True);args=parser.parse_args()
 print(json.dumps(prepare(args.name,args.reference_pack,args.model,args.effort,args.context),indent=2))
