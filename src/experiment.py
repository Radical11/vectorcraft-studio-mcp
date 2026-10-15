"""Locked paired pilot ledger. Scheduling and receipts are not image judgments."""
from pathlib import Path
import hashlib
import json
import random
import time
from datetime import datetime, timezone
from workflow import atomic, digest, read, safe_id

CONDITIONS = ('designer-v1', 'layout-blockout-v1', 'designer-process-v1')

def timestamp():
    return datetime.now(timezone.utc).timestamp()

def create(root, name, briefs, references, model, seed=131026, locked_files=()):
    root = Path(root).resolve(); safe_id(name)
    dest = root/'work/experiments'/name
    if dest.exists():
        raise ValueError('Preserve the locked experiment; use a new identifier')
    if len(briefs) != 3 or len({b['genre'] for b in briefs}) != 3 or len({b['id'] for b in briefs})!=3:
        raise ValueError('Three distinct genre briefs required')
    def source(path):
        p=Path(path).resolve()
        if not p.is_relative_to(root) or not p.is_file():
            raise ValueError('Inputs must be existing project files')
        return {'path':str(p.relative_to(root)), 'sha256':digest(p)}
    inputs=[]
    for brief in briefs:
        safe_id(brief['id']); inputs.append({**brief, 'source':source(brief['path'])})
    refs=[source(p) for p in references]
    if not model.strip(): raise ValueError('Record the configured host model')
    schedule=[{'id':f'{b["id"]}-{c}-{repeat}', 'brief':b['id'], 'condition':c,
               'repeat':repeat, 'status':'pending'} for b in briefs for c in CONDITIONS for repeat in (1,2)]
    random.Random(seed).shuffle(schedule)
    protocol={'contract':1, 'name':name, 'seed':seed, 'model':model, 'conditions':list(CONDITIONS),
              'inputs':inputs, 'references':refs, 'locked_files':[source(p) for p in locked_files],
              'limits':{'active_seconds':3600,'batches':24,'correction_rounds':3},
              'primary':'Common-brief preference and consequential defects; no universal aesthetic score',
              'gate':'Both specialists and owner agree on improvement in >=4/6 default pairs, >=2 genres, no consequential regression',
              'independent_unit':'brief; repeats and reviewer ratings are correlated',
              'token_telemetry':'unavailable unless supplied by host receipts'}
    dest.mkdir(parents=True)
    atomic(dest/'protocol.json',protocol)
    atomic(dest/'ledger.json',{'protocol_sha256':digest(dest/'protocol.json'),'trials':schedule,'events':[]})
    return dest

class Ledger:
    def __init__(self, root, folder):
        self.root=Path(root).resolve(); self.folder=Path(folder).resolve()
        if not self.folder.is_relative_to(self.root/'work/experiments'): raise ValueError('Experiment escapes project')
        self.protocol=read(self.folder/'protocol.json'); self.data=read(self.folder/'ledger.json')
        self.verify()
    def verify(self):
        if digest(self.folder/'protocol.json')!=self.data['protocol_sha256']: raise ValueError('Locked protocol changed')
        for s in [b['source'] for b in self.protocol['inputs']]+self.protocol['references']+self.protocol.get('locked_files',[]):
            p=(self.root/s['path']).resolve()
            if not p.is_relative_to(self.root) or not p.is_file() or digest(p)!=s['sha256']:
                raise ValueError('Locked input changed')
    def persist(self): atomic(self.folder/'ledger.json',self.data)
    def trial(self, identifier):
        return next(t for t in self.data['trials'] if t['id']==identifier)
    def event(self, identifier, event, **detail):
        self.data['events'].append({'trial':identifier,'event':event,'at':timestamp(),'monotonic':time.monotonic(),**detail}); self.persist()
    def start(self, identifier):
        self.verify(); t=self.trial(identifier)
        if any(x['status']=='building' for x in self.data['trials']): raise ValueError('Only one active builder')
        if t['status']!='pending': raise ValueError('Trials cannot be silently rebuilt or replayed')
        t.update(status='building',active_started=timestamp(),active_seconds=0,batches=0,tool_calls=0,review_seconds=0)
        self.event(identifier,'start')
    def elapsed(self, t):
        return t['active_seconds']+(timestamp()-t['active_started'] if t.get('active_started') else 0)
    def pause_review(self, identifier):
        t=self.trial(identifier)
        if t['status']!='building' or not t.get('active_started'): raise ValueError('Active build required')
        t['active_seconds']=self.elapsed(t); t['active_started']=None; t['review_started']=timestamp()
        self.event(identifier,'review_pause')
    def resume_build(self, identifier):
        self.verify();t=self.trial(identifier)
        if t['status']!='building' or t.get('active_started') or not t.get('review_started'): raise ValueError('Paused review required')
        t['review_seconds']+=timestamp()-t.pop('review_started'); t['active_started']=timestamp()
        self.event(identifier,'review_resume')
    def before_call(self, identifier, tool):
        self.verify(); t=self.trial(identifier)
        if t['status']!='building' or not t.get('active_started'): raise ValueError('Active builder required')
        limit=self.protocol['limits']
        if self.elapsed(t)>=limit['active_seconds']: raise ValueError('Build time exhausted; settle in-flight operations, preserve result')
        if tool=='workflow_begin':
            if t['batches']>=limit['batches']: raise ValueError('Batch allowance exhausted')
            t['batches']+=1
        t['tool_calls']+=1; self.event(identifier,'call',tool=tool)
    def finish(self, identifier, status, evidence=None, reason=None):
        t=self.trial(identifier)
        if t['status']!='building': raise ValueError('Active trial required')
        if status not in ('completed','failed','budget_exhausted','unavailable'): raise ValueError('Explicit trial outcome required')
        if status=='completed':
            p=Path(evidence).resolve()
            if not p.is_relative_to(self.root) or not p.is_file(): raise ValueError('Actual run evidence required')
            run=read(p)
            if run.get('format')!='vectorcraft-studio-run' or run.get('version')!=3 or run.get('quality_profile')!=t['condition'] or run.get('status')=='active':
                raise ValueError('Completed trial requires a stopped matching-profile actual run')
            t['evidence']={'path':str(p.relative_to(self.root)),'sha256':digest(p)}
        elif not reason: raise ValueError('Record the failure, never discard it')
        t['active_seconds']=self.elapsed(t);t['active_started']=None
        if t.get('review_started'): t['review_seconds']+=timestamp()-t.pop('review_started')
        t.update(status=status,reason=reason);self.event(identifier,'finish',status=status)
    def blind_schedule(self):
        path=self.folder/'blind-map-private.json'
        if path.exists(): return read(path)
        if any(t['status'] in ('pending','building') for t in self.data['trials']): raise ValueError('Finish or account for every trial')
        rng=random.Random(self.protocol['seed']+1);pairs=[]
        positions={(b['id'],baseline):rng.randint(0,1) for b in self.protocol['inputs'] for baseline in CONDITIONS[:2]}
        for b in self.protocol['inputs']:
            for repeat in (1,2):
                for baseline in CONDITIONS[:2]:
                    ids=[f'{b["id"]}-{baseline}-{repeat}',f'{b["id"]}-{CONDITIONS[2]}-{repeat}']
                    if (positions[(b['id'],baseline)]+repeat-1)%2==0:ids.reverse()
                    pairs.append({'brief':b['id'],'repeat':repeat,'baseline':baseline,'A':ids[0],'B':ids[1]})
        rng.shuffle(pairs);atomic(path,pairs);return pairs
