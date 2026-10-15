"""Account for every frozen pilot outcome without inventing visual judgments.

Writes a private artifact index and sanitized descriptive table. The full ledger
and native evidence remain local. No subset of retained winners replaces the18.
"""
from pathlib import Path
import argparse,json,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from experiment import Ledger
from workflow import atomic,digest,read

def collect(folder,roots_path,out):
 ledger=Ledger(ROOT,folder);roots=read(roots_path)['roots'];out=Path(out).resolve()
 if not out.is_relative_to(ROOT/'outputs'):raise ValueError('Use a project outputs folder')
 if len(ledger.data['trials'])!=18:raise ValueError('Expected all18 approved outcomes')
 results=[];index=[]
 for trial in ledger.data['trials']:
  if trial['status'] in ('pending','building'):raise ValueError('Account for every trial before final reporting')
  root=Path(roots[trial['id']]).resolve()
  if not root.is_relative_to(ROOT/'work/research32/pilot'):raise ValueError('Unexpected trial root')
  report=root/'completion-report.json'
  if not report.is_file():raise ValueError('Preserve a completion/failure report for every trial')
  data=read(report)
  if data.get('profile')!=trial['condition']:raise ValueError('Report condition differs from locked trial')
  evidence=trial.get('evidence')
  if evidence and digest(ROOT/evidence['path'])!=evidence['sha256']:raise ValueError('Stopped run evidence changed')
  run=read(ROOT/evidence['path']) if evidence else None
  # Measures come from the adapter ledger, not creator estimates or review scores.
  results.append({'trial':trial['id'],'brief':trial['brief'],'condition':trial['condition'],'repeat':trial['repeat'],
   'trial_outcome':trial['status'],'run_status':run['status'] if run else None,
   'active_seconds':trial.get('active_seconds'),'review_seconds':trial.get('review_seconds'),
   'planned_batches':trial.get('batches'),'host_calls':trial.get('tool_calls'),
   'correction_rounds':run.get('revision_rounds') if run else None,
   'reason':trial.get('reason'),'limitations':data.get('limitations',[]),
   'report_sha256':digest(report),'review_results':'Not inferred from creator report; use actual blind comparisons'})
  files=[report,root/'binding.json',root/'host-budget.json',root/'host-receipts.jsonl']
  for field in ('creator-image-actions.json','execution-issues.json','clock-diagnostics.jsonl'):
   if (root/field).is_file():files.append(root/field)
  if evidence:files.append(ROOT/evidence['path'])
  index.append({'trial':trial['id'],'artifacts':[{'path':str(p.relative_to(ROOT)),'sha256':digest(p)} for p in files]})
 out.mkdir(parents=True,exist_ok=True)
 atomic(out/'outcomes.json',{'protocol_sha256':ledger.data['protocol_sha256'],'independent_units':3,
  'expected_outcomes':18,'results':results,'quality_claim':'No preference or improvement inferred by this collector'})
 atomic(out/'private-artifact-index.json',index)
 lines=['# Complete pilot accounting','','All18 outcomes retained. Three briefs are independent task units; repeats are correlated.','',
  '| Trial | Outcome | Run status | Active min | Review wait min | Batches | Host calls |','| --- | --- | --- | ---: | ---: | ---: | ---: |']
 for r in results:
  lines.append(f"| {r['trial']} | {r['trial_outcome']} | {r['run_status'] or 'unavailable'} | {r['active_seconds']/60:.2f} | {r['review_seconds']/60:.2f} | {r['planned_batches']} | {r['host_calls']} |")
 (out/'outcomes.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
 return {'outcomes':str(out/'outcomes.json'),'count':len(results),'blind_comparisons':'separate observed evidence required'}

if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--experiment',required=True)
 parser.add_argument('--roots',required=True);parser.add_argument('--out',required=True);args=parser.parse_args()
 print(json.dumps(collect(args.experiment,args.roots,args.out),indent=2))
