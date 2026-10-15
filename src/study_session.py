"""Connection-owned native study routing. No production edits or uncertain replay."""
from pathlib import Path
import uuid
import designer
import design_process as process
from workflow import read, safe_id, nonempty

class Studies:
    def __init__(self,gateway):
        self.parent=gateway;self.child=None
    def active(self):
        w=self.parent.workflow
        return process.enabled(w) and process.state(w)['active_study'] is not None
    def restore(self):
        w=self.parent.workflow;p=process.state(w);identifier=p['active_study']
        if not identifier:return
        self.open_child()
        self.child.call('workflow_start',{'resume':p['studies'][identifier]['run']})
    def open_child(self):
        from vectorcraft_gateway import Gateway
        self.child=Gateway(self.parent.root,self.parent.notify)
        self.child.initialize(self.parent.init_params);self.child.tools()
    def begin(self,stage,plan):
        w=self.parent.workflow;w.require_active()
        if not process.enabled(w):raise ValueError('Isolated studies require an experimental process profile')
        if stage!='composition' or w.state['pending'] or process.state(w)['started']:raise ValueError('Studies precede production and cannot finish its stages')
        if not all(w.latest(k) for k in ('design_brief','research','calibration','layout')):raise ValueError('Brief/research/calibration/layout before native study')
        identifier=safe_id(plan.get('study_id'));layout_id=plan.get('layout_id')
        if layout_id not in {a['id'] for a in w.data('layout')['alternatives']}:raise ValueError('Study must bind to a current layout')
        checks=plan.get('checks',[])
        if not isinstance(checks,list) or not 2<=len(checks)<=3 or len({c.get('id') for c in checks})!=len(checks):raise ValueError('Two or three unique study checks required')
        for c in checks:safe_id(c['id']);nonempty(c.get('description'),'study check')
        for key in ('purpose','changes','expected_result'):nonempty(plan.get(key),key)
        p=process.state(w)
        if p['active_study']:
            if identifier!=p['active_study']:raise ValueError('Only one active native study')
            study=p['studies'][identifier]
            if study['layout_id']!=layout_id or study['layout_sha256']!=w.latest('layout')['artifact']['sha256']:raise ValueError('Study scope/layout changed')
        else:
            if identifier in p['studies']:raise ValueError('Closed study ID cannot be reused')
            run_id='study-'+uuid.uuid4().hex[:16]+'-'+identifier[:40]
            self.open_child()
            try:self.child.call('workflow_start',{'mode':'quick','scope':'Isolated native design study: '+identifier,'run_id':run_id})
            except Exception:self.child.shutdown();self.child=None;raise
            p['studies'][identifier]={'run':str(self.child.workflow.run),'layout_id':layout_id,
                                     'layout_sha256':w.latest('layout')['artifact']['sha256'],'outcome':'pending'}
            p['active_study']=identifier
        quick_plan={k:v for k,v in plan.items() if k not in ('context','study_id','layout_id')}
        quick_plan['checks']=' / '.join(c['description'] for c in checks)
        self.child.call('workflow_begin',{'stage':stage,'plan':quick_plan})
        p['studies'][identifier].update(checks=checks,plan={k:v for k,v in plan.items() if k!='context'},batch_pending=True)
        w.persist();return w.response()
    def checkpoint(self,version,data):
        from vectorcraft_gateway import payload
        w=self.parent.workflow;p=process.state(w);study=p['studies'][p['active_study']]
        if data.get('phase','capture')=='capture':
            result=self.child.call('workflow_checkpoint',{'version':version,'data':data})
            study['capture']=payload(result)
            study['capture_revision']=self.child.workflow.state['revision']
            study['revision']=self.child.workflow.state['revision']
            w.persist();return result
        child=self.child.workflow;snap=child.state['versions'].get(version)
        if not snap:raise ValueError('Capture the actual study before confirmation')
        designer.inspection(w,data,[child.run/a['path'] for a in snap['images']])
        outcome=data.get('outcome');results=data.get('check_results',[])
        if outcome not in ('pass','revise','blocked'):raise ValueError('Explicit study outcome required')
        if len(results)!=len(study['checks']) or {r.get('id') for r in results}!={c['id'] for c in study['checks']}:raise ValueError('Assess exactly the planned study checks')
        for r in results:
            nonempty(r.get('observation'),'study observation')
            if r.get('outcome') not in ('pass','fail','not_applicable'):raise ValueError('Invalid study check outcome')
            if r['outcome']=='not_applicable':nonempty(r.get('reason'),'inapplicable study reason')
        if outcome=='pass' and any(r['outcome']=='fail' for r in results):raise ValueError('Failed study cannot pass')
        if outcome!='pass':nonempty(data.get('reason'),'study correction/block reason')
        if type(data.get('close_study',False))!=bool:raise ValueError('close_study must be boolean')
        if data.get('close_study') and outcome=='revise':raise ValueError('Unresolved revision cannot close; correct or explicitly abandon blocked')
        confirmation={**data,'decision':data.get('decision') or outcome}
        result=self.child.call('workflow_checkpoint',{'version':version,'data':confirmation})
        if result.get('isError'):return result
        study.update(outcome=outcome,observation=data['observations'],batch_pending=False,
                     native=w.artifact(child.run/snap['native']['path'],'study-native'),
                     images=[w.artifact(child.run/a['path'],'study-image') for a in snap['images']])
        process.append(w,'study_observation',data)
        if data.get('close_study'):
            study['closed']=True;p['active_study']=None;self.child.shutdown();self.child=None
        w.persist();return {'content':[{'type':'text','text':__import__('json').dumps(w.response())}],'isError':False}
    def route(self,name,args):
        from vectorcraft_gateway import text_result
        if name=='workflow_begin':
            if args.get('plan',{}).get('context')!='study':raise ValueError('Finish the isolated study before production')
            return text_result(self.begin(**args))
        if name=='workflow_checkpoint':return self.checkpoint(**args)
        if name.startswith('workflow_'):raise ValueError('Parent records and run transitions require closed study')
        result=self.child.call(name,args)
        if name=='connection_status' and not result.get('isError'):
            from vectorcraft_gateway import payload
            result=text_result({**payload(result),'context':'study','parent_run':str(self.parent.workflow.run),'study_id':process.state(self.parent.workflow)['active_study']})
        study=process.state(self.parent.workflow)['studies'][process.state(self.parent.workflow)['active_study']]
        study['revision']=self.child.workflow.state['revision'];study['uncertain']=self.child.workflow.state.get('uncertain',False)
        study['batch_pending']=self.child.workflow.state['pending'] is not None
        self.parent.workflow.persist();return result
    def shutdown(self):
        if self.child:self.child.shutdown();self.child=None
