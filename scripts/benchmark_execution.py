"""Deterministic transport fixture. No artwork-quality or model-token claims.

Run with Python 3.13. Baseline source is read-only; all engines run in new roots.
The fixture uses quick mode for transport and exercises efficient batch preparation
separately; full-profile acceptance remains covered by policy and forward tests.
"""
import argparse
import ctypes
import hashlib
import json
import math
import os
from pathlib import Path
import statistics
import subprocess
import sys
import time
import uuid

ROOT=Path(__file__).resolve().parents[1]


def memory(process):
    if os.name!='nt':return None
    class Counters(ctypes.Structure):
        _fields_=[('cb',ctypes.c_ulong),('PageFaultCount',ctypes.c_ulong)]+[(k,ctypes.c_size_t) for k in
            ('PeakWorkingSetSize','WorkingSetSize','QuotaPeakPagedPoolUsage','QuotaPagedPoolUsage','QuotaPeakNonPagedPoolUsage','QuotaNonPagedPoolUsage','PagefileUsage','PeakPagefileUsage')]
    row=Counters();row.cb=ctypes.sizeof(row)
    if ctypes.windll.psapi.GetProcessMemoryInfo(ctypes.c_void_p(int(process._handle)),ctypes.byref(row),row.cb):
        return {'working_set_bytes':row.WorkingSetSize,'peak_working_set_bytes':row.PeakWorkingSetSize}
    return None


def worker(a):
    sys.path.insert(0,str(a.source/'src'))
    from vectorcraft_gateway import Gateway,INIT,payload
    from workflow import native_fingerprint
    a.project.mkdir(parents=True,exist_ok=False)
    os.environ['VECTORCRAFT_CLI']=str(a.engine/'vectorcraft-cli.exe')
    os.environ['VECTORCRAFT_DESKTOP']=str(a.engine/'vectorcraft.exe')
    g=Gateway(a.project);g.initialize(INIT)
    rows=[];host_calls=0;editing_calls=0
    def call(name,args):
        nonlocal host_calls,editing_calls
        started=time.perf_counter();result=g.call(name,args)
        host_calls+=1;editing_calls+=g.operation(name,args)=='edit'
        rows.append({'tool':name,'duration_ms':(time.perf_counter()-started)*1000,
                     'request_bytes':len(json.dumps(args,ensure_ascii=False).encode()),
                     'response_text_bytes':sum(len(c.get('text','').encode()) for c in result.get('content',[]) if c.get('type')=='text')})
        if result.get('isError'):raise RuntimeError(result)
        return payload(result)
    try:
        cold=time.perf_counter();g.tools();discovery_cold=(time.perf_counter()-cold)*1000
        discovery=[]
        for _ in range(5):
            started=time.perf_counter();g.tools();discovery.append((time.perf_counter()-started)*1000)
        call('workflow_start',{'mode':'quick','scope':'Deterministic transport benchmark only','run_id':'fixture'})
        draw_batch='draw_path' in g.tool_catalog['command_batch']['description']
        samples=[]
        for iteration in range(a.iterations+1):
            before=len(rows);before_edits=editing_calls;started=time.perf_counter()
            call('command_run',{'id':'artboard.setProps','params':{'index':0,'width':500,'height':500}})
            steps=[];ids=[]
            for index in range(8):
                params={'shape':'rectangle','x':20+index*50,'y':30+iteration*30,'width':35,'height':20,'fill':'#d55638','stroke':'none'}
                if a.upgraded and draw_batch:
                    steps.append({'id':'draw_shape','params':{**params,'name':'Fixture '+str(index)}})
                else:
                    result=call('draw_shape',params);ids.append(result['id'])
                    call('command_run',{'id':'object.setProps','params':{'id':result['id'],'name':'Fixture '+str(index)}})
            if steps:
                import efficient
                from types import SimpleNamespace
                owner=SimpleNamespace(state={'execution_profile':'efficient-v1'})
                prepared=efficient.batch(SimpleNamespace(workflow=owner,engine_capabilities=g.engine_capabilities,tool_catalog=g.tool_catalog),{'steps':steps,'label':'Eight fixture tabs'})
                result=call('command_batch',prepared);ids=result['created']
                if result['failed']:raise RuntimeError('Fixture partially failed; no replay')
            for object_id in ids:
                node=call('command_run',{'id':'document.node','params':{'id':object_id,'summary':True,'depth':0,'childLimit':0}})
                if not node:raise ValueError('Missing fixture object')
            elapsed=(time.perf_counter()-started)*1000
            if iteration:samples.append({'component_ms':elapsed,'host_editing_calls':editing_calls-before_edits-1,
                                         'component_host_calls':len(rows)-before-1})
        text=call('add_text',{'x':20,'y':300,'width':400,'height':60,'text':'Repair together','font':'Arial','size':24,'color':'#102d36','fit':'none'})
        call('command_run',{'id':'select.none','params':{}})
        explicit=True
        try:
            result=g.backend.checked_call('command_run',{'id':'text.areaOptions','params':{'ids':[text['id']]}})
            options=payload(result)
        except RuntimeError:
            explicit=False
            if not a.upgraded:
                call('command_run',{'id':'select.set','params':{'ids':[text['id']]}})
                options=call('command_run',{'id':'text.areaOptions','params':{'ids':[text['id']]}})
                call('command_run',{'id':'select.none','params':{}})
            else:
                import efficient
                options=efficient.area_options(g.backend,text['id'])
        if options.get('overflow') or options.get('fitScale')!=1:raise ValueError('Invalid live text fit')
        call('command_run',{'id':'select.set','params':{'ids':[text['id']]}})
        call('command_run',{'id':'select.save','params':{'name':'Fixture type'}})
        call('command_run',{'id':'select.none','params':{}})
        saved_selection_classification=g.operation('command_run',{'id':'select.save'})
        native=a.project/'fixture.vectorcraft';call('export',{'format':'vectorcraft','path':str(native)})
        fingerprint=native_fingerprint(native)
        call('open_file',{'path':str(native)})
        reopened=a.project/'reopened.vectorcraft';call('export',{'format':'vectorcraft','path':str(reopened)})
        if native_fingerprint(reopened)!=fingerprint:raise ValueError('Native reopening changed content')
        exports={}
        for fmt in ('svg','pdf','png'):
            path=a.project/('fixture.'+fmt);started=time.perf_counter();call('export',{'format':fmt,'path':str(path)})
            exports[fmt]={'ms':(time.perf_counter()-started)*1000,'bytes':path.stat().st_size}
        call('render_preview',{'max_side':450})
        live_memory=memory(g.backend.process)
        recovery=g.last_checkpoint is not None and g.last_checkpoint.is_file()
        native_version=json.loads(native.read_text())['version']
        # Packet fixture imports never author or inspect real artwork.
        sys.path.insert(0,str(a.source/'tests'));import test_focused
        fixture=test_focused.FocusedTests('test_intermediate_pass_does_not_complete_stage');fixture.setUp()
        try:
            if a.upgraded:
                fixture.w.state.update(execution_profile='efficient-v1',engine_identity=g.workflow.engine_identity);fixture.w.persist()
            working=fixture.w.status('working');packet_bytes=len(json.dumps(working,ensure_ascii=False).encode())
        finally:fixture.tearDown()
        return {'engine_version':subprocess.check_output([str(a.engine/'vectorcraft-cli.exe'),'--version'],text=True).strip(),
                'engine_sha256':hashlib.sha256((a.engine/'vectorcraft-cli.exe').read_bytes()).hexdigest(),
                'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=a.source,text=True).strip(),
                'source_files_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((a.source/'src').glob('*.py'))},
                'workload_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                'upgraded':a.upgraded,'native_version':native_version,'draw_batch':draw_batch,
                'explicit_id_area_query':explicit,'saved_selection_classification':saved_selection_classification,
                'samples':samples,'discovery_cold_ms':discovery_cold,'discovery_warm_ms':discovery,'packet_bytes':packet_bytes,
                'host_calls':host_calls,'host_editing_calls':editing_calls,'exports':exports,'memory':live_memory,
                'native_reopen_match':True,'recovery_checkpoint':recovery,'calls':rows,
                'actual_model_tokens':None,'token_source':'unavailable; no run-scoped host token receipts',
                'scope':'Deterministic transport fixture; no image judgment or design quality claim'}
    finally:g.shutdown()


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for key in ('source','engine','project','baseline','engine11','engine12','output'):p.add_argument('--'+key,type=Path)
    p.add_argument('--worker',action='store_true');p.add_argument('--upgraded',action='store_true');p.add_argument('--iterations',type=int,default=7)
    a=p.parse_args()
    if not 3<=a.iterations<=20:p.error('Use 3..20 warm repetitions')
    if a.worker:
        result=worker(a);a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(result,indent=2));return
    folder=a.output or ROOT/'outputs/efficient-v1/benchmark';folder.mkdir(parents=True,exist_ok=True)
    results={}
    for label,source,engine,upgraded in [('baseline-11',a.baseline,a.engine11,False),('gateway-11',ROOT,a.engine11,True),('gateway-12',ROOT,a.engine12,True)]:
        output=folder/(label+'.json');project=ROOT/'work/efficient/benchmark'/uuid.uuid4().hex
        command=[sys.executable,__file__,'--worker','--source',str(source),'--engine',str(engine),'--project',str(project),'--output',str(output),'--iterations',str(a.iterations)]
        if upgraded:command.append('--upgraded')
        subprocess.run(command,check=True);row=json.loads(output.read_text())
        timings=sorted(s['component_ms'] for s in row['samples'])
        row['summary']={'warm_median_ms':statistics.median(timings),'warm_p95_ms':timings[math.ceil(.95*len(timings))-1],
                        'routine_packet_bytes':row['packet_bytes'],'editing_calls_per_component':row['samples'][0]['host_editing_calls']}
        results[label]=row;print(label,json.dumps(row['summary']),flush=True)
    (folder/'results.json').write_text(json.dumps({'format':'efficient-execution-benchmark-v1','results':results},indent=2))

if __name__=='__main__':main()
