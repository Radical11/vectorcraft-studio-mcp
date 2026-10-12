"""Capture reproducible final tests; fixture checks do not establish design quality."""
from pathlib import Path
import json,re,subprocess,sys,argparse
from datetime import datetime,timezone
parser=argparse.ArgumentParser();parser.add_argument('--unit-only',action='store_true');a=parser.parse_args()
ROOT=Path(__file__).resolve().parents[1];out=ROOT/'outputs/verification31';out.mkdir(parents=True,exist_ok=True)
commands=[('workflow-v3',['-m','unittest','discover','-s','tests','-p','test_workflow.py','-q']),
 ('designer-v1',['-m','unittest','discover','-s','tests','-p','test_designer.py','-q']),
 ('portable-install',['-m','unittest','discover','-s','tests','-p','test_install.py','-q']),
 ('native-passthrough',['-m','unittest','discover','-s','tests','-p','test_passthrough_live.py','-q']),
 ('gateway-v3-live',['-m','unittest','discover','-s','tests','-p','test_gateway_workflow_live.py','-q']),
 ('legacy-v1',['tests/legacy/test-studio-ledger.py']),('legacy-v2-vault',['tests/legacy/test-studio-v2.py']),
 ('desktop-handoff',['tests/legacy/test-vectorcraft-gateway.py']),('desktop-recovery',['tests/legacy/test-vectorcraft-recovery.py'])]
results=[]
if a.unit_only:commands=[c for c in commands if c[0] in ('workflow-v3','designer-v1','portable-install','legacy-v1','legacy-v2-vault')]
for name,args in commands:
 r=subprocess.run([sys.executable,*args],cwd=ROOT,text=True,encoding='utf-8',errors='replace',capture_output=True)
 log=r.stdout+'\n'+r.stderr;(out/(name+'.log')).write_text(log,encoding='utf-8');m=re.search(r'Ran (\d+) tests?',log)
 results.append({'suite':name,'passed':r.returncode==0,'count':int(m[1]) if m else 4 if name=='desktop-recovery' else 1,'log':name+'.log'})
 print(json.dumps(results[-1]),flush=True)
 if r.returncode:raise SystemExit(log)
(out/('unit-test-results.json' if a.unit_only else 'test-results.json')).write_text(json.dumps({'at':datetime.now(timezone.utc).isoformat(),'python':sys.version,'scope':'self-contained fixtures' if a.unit_only else 'local Windows integration plus fixtures','suites':results,'total':sum(r['count'] for r in results),'all_passed':True},indent=2),encoding='utf-8')
