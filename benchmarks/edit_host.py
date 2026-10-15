"""Equal scoped-edit allowance on separate native evaluation copies.

No construction records, graph, creator scripts or reviewer history are given
to edit contexts. Captured observations are host-attested, never synthesized.
"""
from pathlib import Path
import json,sys,time
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from vectorcraft_gateway import Gateway,INIT,payload
from workflow import atomic,digest,read

def guard(budget,tool,wall=None):
 wall=time.time() if wall is None else wall
 if wall-budget['started']>=600:raise ValueError('Ten-minute edit allowance exhausted')
 if tool=='workflow_begin' and budget['batches']>=4:raise ValueError('Four planned edit batches exhausted')

class EditSession:
 def __init__(self,root):
  self.root=Path(root).resolve()
  if not self.root.is_relative_to(ROOT/'work/research32/editing'):raise ValueError('Use a separate project-contained editing root')
  self.binding=read(self.root/'binding.json');source=(self.root/self.binding['native']['path']).resolve()
  if not source.is_relative_to(self.root) or digest(source)!=self.binding['native']['sha256']:raise ValueError('Original evaluation source changed')
  self.budget_path=self.root/'host-budget.json'
  self.budget=read(self.budget_path) if self.budget_path.exists() else {'started':time.time(),'started_monotonic':time.monotonic(),'batches':0,'calls':0}
  self.g=Gateway(self.root);self.g.initialize(INIT);self.g.tools()
  run=self.root/'work/vectorcraft-studio/edit-task/run.json'
  if run.exists():self.g.call('workflow_start',{'resume':str(run.parent)})
  else:
   self.g.call('open_file',{'path':str(source)})
   self.g.call('workflow_start',{'mode':'quick','scope':self.binding['scope'],'run_id':'edit-task','use_width':self.binding['use_width']})
  atomic(self.budget_path,self.budget)
 def call(self,tool,args=None):
  wall,mono=time.time(),time.monotonic()
  with (self.root/'clock-diagnostics.jsonl').open('a',encoding='utf-8') as stream:
   stream.write(json.dumps({'at':wall,'monotonic':mono,'tool':tool,'wall_elapsed':wall-self.budget['started'],
    'monotonic_elapsed':mono-self.budget['started_monotonic']})+'\n')
  guard(self.budget,tool,wall)
  if tool=='workflow_begin':self.budget['batches']+=1
  self.budget['calls']+=1;atomic(self.budget_path,self.budget)
  try:
   result=self.g.call(tool,args or {})
   with (self.root/'host-receipts.jsonl').open('a',encoding='utf-8') as stream:
    stream.write(json.dumps({'at':time.time(),'monotonic':time.monotonic(),'tool':tool,'args':args,'result':payload(result),'isError':result.get('isError',False)})+'\n')
   if result.get('isError'):raise RuntimeError(json.dumps(payload(result)))
   return payload(result) or result
  except Exception as error:
   with (self.root/'host-errors.jsonl').open('a',encoding='utf-8') as stream:
    stream.write(json.dumps({'at':time.time(),'tool':tool,'error':str(error),'replayed':False})+'\n')
   raise
 def close(self):self.g.shutdown()
 def __enter__(self):return self
 def __exit__(self,*_):self.close()
