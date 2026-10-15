"""Export an explicit interim study derivative, retaining pending/failed units.

Only owned production captures/exports, visible review returns and summaries are
selected. Cached references, raw sessions, config, vault and input archives stay
private. This exporter never changes the ledger or completes a trial.
"""
from pathlib import Path
import argparse, hashlib, json, re, shutil, sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from experiment import Ledger
from workflow import read, digest

def export(folder, roots_path, out):
 ledger=Ledger(ROOT,folder);out=Path(out).resolve()
 if not out.is_relative_to(ROOT/'public-evidence') or out.exists():raise ValueError('Use a new public-evidence checkpoint')
 if any(t['status']=='building' for t in ledger.data['trials']):raise ValueError('Settle the active builder before publication')
 roots=read(roots_path)['roots'];out.mkdir(parents=True);manifest=[];omissions=[];rows=[]
 def clean(value):
  if isinstance(value,dict):return {clean(k):clean(v) for k,v in value.items()}
  if isinstance(value,list):return [clean(v) for v in value]
  if not isinstance(value,str):return value
  value=re.sub(re.escape(str(ROOT)), '<project>', value,flags=re.I)
  value=re.sub(re.escape(ROOT.as_posix()), '<project>', value,flags=re.I)
  value=re.sub(r'C:[/\\]+Users[/\\]+[^/\\\s]+[^\n]*', '[private user path withheld]',value,flags=re.I)
  return value
 def write(path,data):
  path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(clean(data),indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
 def copy(source,target,expected=None):
  source=Path(source).resolve()
  if expected and (not source.is_file() or digest(source)!=expected):
   omissions.append({'file':target.relative_to(out).as_posix(),'reason':'Source absent or changed from recorded artifact','expected_sha256':expected});return None
  if not source.is_file():return None
  target.parent.mkdir(parents=True,exist_ok=True)
  if source.suffix.lower()=='.json':write(target,read(source))
  elif source.suffix.lower() in ('.vectorcraft','.svg'):
   text=source.read_text(encoding='utf-8-sig')
   if re.search(r'C:[/\\]+Users[/\\]+|D:[/\\]+vectorcraftmcp|\[private user path withheld\]|\[private vault path withheld\]|gh[pousr]_[A-Za-z0-9]{30,}|sk-[A-Za-z0-9]{35,}',text,re.I):
    omissions.append({'file':target.relative_to(out).as_posix(),'reason':'Private path or credential pattern; source not rewritten'});return None
   shutil.copy2(source,target)
  else:shutil.copy2(source,target)
  manifest.append({'path':target.relative_to(out).as_posix(),'source_sha256':digest(source),'public_sha256':digest(target),
   'sanitized_derivative':digest(source)!=digest(target)})
  return str(target.relative_to(out).as_posix())
 for number,trial in enumerate(ledger.data['trials'],1):
  row={k:trial.get(k) for k in ('id','brief','condition','repeat','status','active_seconds','review_seconds','batches','tool_calls','reason')}
  row.update(order=number,production_capture=False,retained_version=None,run_status=None)
  if trial['status']=='pending':rows.append(row);continue
  root=Path(roots[trial['id']]).resolve()
  if not root.is_relative_to(ROOT/'work/research32/pilot'):raise ValueError('Unexpected trial root')
  dest=out/'attempts'/trial['id'];report=root/'completion-report.json'
  if not report.is_file():raise ValueError('An accounted attempt needs a real completion/failure report')
  copy(report,dest/'creator-report.json')
  for name in ('creator-image-actions.json','execution-issues.json','accounting-audit.json'):
   if (root/name).is_file():copy(root/name,dest/name)
  run_path=root/'work/vectorcraft-studio/artwork/run.json';run=read(run_path) if run_path.exists() else None
  row['result_receipts']=sum(1 for line in (root/'host-receipts.jsonl').read_text(encoding='utf-8').splitlines() if line.strip()) if (root/'host-receipts.jsonl').exists() else None
  if run:
   row.update(run_status=run['status'],retained_version=run.get('best_version') or run.get('working_version'),completed_stages=run.get('completed_stages',[]))
   summary={k:run.get(k) for k in ('format','version','quality_profile','status','revision','spec_revision','completed_stages','working_version','best_version','original_version','pending','uncertain','revision_rounds','no_improvement_streak','stop_reason')}
   summary['private_run_sha256']=digest(run_path);summary['versions']={}
   for name,snapshot in run.get('versions',{}).items():
    public={k:snapshot.get(k) for k in ('confirmed','role','revision','spec_revision','fingerprint','element_map')}
    for key in ('native','inspection','check'):
     if snapshot.get(key):
      artifact=snapshot[key];source=(run_path.parent/artifact['path']).resolve()
      if not source.is_relative_to(root):raise ValueError('Capture escapes its trial')
      public[key]=copy(source,dest/'versions'/name/source.name,artifact['sha256'])
    public['images']=[]
    for i,artifact in enumerate(snapshot.get('images',[])):
     source=(run_path.parent/artifact['path']).resolve()
     if not source.is_relative_to(root):raise ValueError('Image escapes its trial')
     p=copy(source,dest/'versions'/name/('full.png' if i==0 else 'use.png' if i==1 else f'detail-{i}.png'),artifact['sha256'])
     if p:public['images'].append(p)
    public['exports']=[]
    for i,artifact in enumerate(snapshot.get('exports',[])):
     source=(run_path.parent/artifact['path']).resolve()
     if not source.is_relative_to(root):raise ValueError('Export escapes its trial')
     p=copy(source,dest/'versions'/name/'exports'/f'{i:02d}-{source.name}',artifact['sha256'])
     if p:public['exports'].append(p)
    summary['versions'][name]=public
   row['production_capture']=bool(row['retained_version'] and summary['versions'].get(row['retained_version'],{}).get('native'))
   write(dest/'run-summary.json',summary)
  # Visible public review returns only; never copy targets, reference pictures or raw sessions.
  candidates=set(root.glob('concept*review*.json'))|set(root.glob('review-*.json'))
  packets=root/'work/vectorcraft-studio/artwork/review-packets'
  if packets.exists():
   candidates.update(packets.rglob('*return.json'));candidates.update(packets.rglob('*image-actions.json'))
  for p in sorted(candidates):copy(p,dest/'reviews'/p.relative_to(root))
  rows.append(row)
 accounted=sum(t['status']!='pending' for t in ledger.data['trials']);pending=len(rows)-accounted
 summary={'date':'2026-10-15','status':f'Interim publication; {pending} remaining builds deferred by owner',
  'method_commit_private':'9d47373687121da52c55d796a08fc91561f4dfdf',
  'protocol_sha256':digest(ledger.folder/'protocol.json'),'private_ledger_sha256':digest(ledger.folder/'ledger.json'),
  'accounted':accounted,'planned':len(rows),'independent_brief_units':3,
  'comparisons':'Not collected','owner_preferences':'Not collected','standardized_edits':'Not conducted',
  'default_promotion':False,'results':rows,
  'limits':['Completion, capture availability and independent acceptance are separate fields.',
   'Charged active time includes disruption and post-authoring overhead, not only construction.',
   'Sanitized model observations are not human reviews or authenticated perception.',
   'Publication before owner comparison creates additional exposure; do not claim guaranteed human blinding.',
   'Cached reference images, raw vault/context notes, config, sessions and private input archive excluded.',
   'Source/public hashes identify derivatives; private method commit is not a public repository commit.']}
 write(out/'checkpoint.json',summary);write(out/'artifact-manifest.json',{'files':manifest,'omissions':omissions})
 write(out/'method-input-hashes.json',{'protocol_sha256':digest(ledger.folder/'protocol.json'),
  'model_recorded':ledger.protocol['model'],'limits':ledger.protocol['limits'],
  'files':[{'path':p['path'].replace('\\','/'),'sha256':p['sha256']} for p in ledger.protocol['locked_files']],
  'reference_images':'Seven cached assets from six works; image bytes withheld from public distribution'})
 lines=['# Interim study checkpoint','', f'15 October 2026. {accounted} of {len(rows)} attempts accounted for; {pending} deferred. No comparison, owner preference or subsequent-edit result is available.', '',
  '| Order | Attempt | Outcome | Gateway status | Charged min | Review wait min | Batches | Instrumented attempts |',
  '| ---: | --- | --- | --- | ---: | ---: | ---: | ---: |']
 for r in rows:
  number=lambda key:f"{r[key]/60:.3f}" if r.get(key) is not None else '—'
  lines.append(f"| {r['order']} | {r['id']} | {r['status']} | {r['run_status'] or 'unavailable'} | {number('active_seconds')} | {number('review_seconds')} | {r.get('batches') if r.get('batches') is not None else '—'} | {r.get('tool_calls') if r.get('tool_calls') is not None else '—'} |")
 lines+=['','Charged time includes disruption and reporting overhead. Failed/active rows can contain real retained artwork; they are not passing workflow outcomes. Pending attempts have no started allowance.','',
  'The original four-of-six release gate cannot be established: three full-process attempts lack accepted production artwork. Keep all eighteen units and do not change the threshold.','',
  'Artifacts are owned production captures/exports and sanitized visible model returns. Images in versions are intermediate or unconfirmed unless their summary says otherwise. No cached third-party references, targets, raw sessions, credentials, configuration or vault notes are redistributed. Source/public SHA values and missing superseded exports are recorded in artifact-manifest.json. The historical paper is unchanged.']
 (out/'README.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
 return {'out':str(out),'accounted':summary['accounted'],'pending':sum(t['status']=='pending' for t in ledger.data['trials']),'copied':len(manifest),'omissions':len(omissions)}

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--experiment',required=True);p.add_argument('--roots',required=True);p.add_argument('--out',required=True)
 a=p.parse_args();print(json.dumps(export(a.experiment,a.roots,a.out),indent=2))
