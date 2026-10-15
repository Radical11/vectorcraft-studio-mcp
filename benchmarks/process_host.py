"""Sequential host adapter: native receipts, resume, budgets; never invented observations.

Builders may import Session in project-contained scripts. A trial binding makes
the shared experiment ledger mandatory. Calibration has the same local ceilings.
"""
from pathlib import Path
import sys,json,time
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from vectorcraft_gateway import Gateway,INIT,payload
from workflow import read,atomic,digest
from experiment import Ledger

class Session:
 def __init__(self,root):
  self.root=Path(root).resolve()
  if not self.root.is_relative_to(ROOT/'work/research32'):raise ValueError('Use a normal isolated research project root')
  self.binding=read(self.root/'binding.json');self.ledger=None
  if self.binding.get('experiment'):
   self.ledger=Ledger(ROOT,self.binding['experiment'])
   trial=self.ledger.trial(self.binding['trial'])
   if trial['condition']!=self.binding['profile']:raise ValueError('Locked condition mismatch')
  for source in self.binding.get('inputs',[]):
   p=(self.root/source['path']).resolve()
   if not p.is_relative_to(self.root) or digest(p)!=source['sha256']:raise ValueError('Locked builder input changed')
  self.budget_path=self.root/'host-budget.json'
  self.budget=read(self.budget_path) if self.budget_path.exists() else {'started':time.time(),'started_monotonic':time.monotonic(),
   'batches':0,'calls':0,'paused_seconds':0,'review_start':None,'clock_policy':'wall elapsed less explicit independent-review pauses; monotonic diagnostics only'}
  self.g=Gateway(self.root);self.g.initialize(INIT);self.g.tools()
  run=self.root/'work/vectorcraft-studio/artwork/run.json'
  if run.exists():
   self.g.call('workflow_start',{'resume':str(run.parent)})
   if self.g.workflow.state['quality_profile']!=self.binding['profile']:raise ValueError('Stored trial profile differs')
  else:
   self.g.call('workflow_start',{'mode':'full','quality_profile':self.binding['profile'],'brief_path':str(self.root/'brief.md'),'run_id':'artwork','use_width':self.binding['use_width']})
  atomic(self.budget_path,self.budget)
 def call(self,tool,args=None):
  wall,mono=time.time(),time.monotonic()
  with (self.root/'clock-diagnostics.jsonl').open('a',encoding='utf-8') as stream:
   stream.write(json.dumps({'at':wall,'monotonic':mono,'tool':tool,
    'wall_elapsed':wall-self.budget['started'],
    'monotonic_elapsed':mono-self.budget['started_monotonic'] if 'started_monotonic' in self.budget else None,
    'review_paused_seconds':self.budget['paused_seconds']})+'\n')
  if self.budget['review_start']:raise ValueError('Resume active build after independent review')
  if time.time()-self.budget['started']-self.budget['paused_seconds']>=3600:raise ValueError('Active build time exhausted')
  if self.ledger:self.ledger.before_call(self.binding['trial'],tool)
  if tool=='workflow_begin':
   if self.budget['batches']>=24:raise ValueError('24 planned batches exhausted')
   self.budget['batches']+=1
  self.budget['calls']+=1;atomic(self.budget_path,self.budget)
  try:
   result=self.g.call(tool,args or {})
   with (self.root/'host-receipts.jsonl').open('a',encoding='utf-8') as stream:stream.write(json.dumps({'at':time.time(),'monotonic':time.monotonic(),'tool':tool,'args':args,'result':payload(result),'isError':result.get('isError',False)})+'\n')
   if result.get('isError'):raise RuntimeError(json.dumps(payload(result)))
   return payload(result) or result
  except Exception as error:
   with (self.root/'host-errors.jsonl').open('a',encoding='utf-8') as stream:stream.write(json.dumps({'at':time.time(),'monotonic':time.monotonic(),'tool':tool,'error':str(error),'replayed':False})+'\n')
   raise
 def pause_review(self):
  if self.budget['review_start']:raise ValueError('Already paused')
  if self.ledger:self.ledger.pause_review(self.binding['trial'])
  self.budget['review_start']=time.time();atomic(self.budget_path,self.budget)
 def resume_build(self):
  if not self.budget['review_start']:raise ValueError('Not paused')
  if self.ledger:self.ledger.resume_build(self.binding['trial'])
  self.budget['paused_seconds']+=time.time()-self.budget['review_start'];self.budget['review_start']=None;atomic(self.budget_path,self.budget)
 def close(self):self.g.shutdown()
 def __enter__(self):return self
 def __exit__(self,*_):self.close()
