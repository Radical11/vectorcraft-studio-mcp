"""Version-three design workflow. Enforces evidence/order, never invents aesthetic judgment."""
from __future__ import annotations
import base64
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import re
import shutil
import uuid

STAGES = ('composition', 'typography', 'imagery', 'finishing')
CRITERIA = ('brief','composition','alignment','typography','color','style','distinctiveness','craft')
KINDS = ('research','calibration','directions','concept_review','target','spec','construction_study','preflight','packet','review','unavailable')

INSTRUCTIONS = (
    'For substantial designs use research -> build -> independent critique. Start workflow_start '
    'full (designer-v1); record inspected research, calibration, three developed alternatives, '
    'independent concept review, a target and concrete spec. Confirm a construction study before '
    'imagery. Plan edits with workflow_begin; inspect full/use captures against the target, then '
    'confirm workflow_checkpoint. Preserve originals; quick mode is for scoped edits. Never claim '
    'unobserved images or unreviewed quality. '
    'Codex supplies research, image generation and design judgment; these tools enforce records '
    'and document revisions. Read workflow schemas from workflow_status. Preserve live typography, '
    'editable vector illustration and the best independently reviewed version. UI tools open a '
    'project-owned desktop automatically. Do not replay uncertain operations; inspect/resume. '
    'Image generation belongs to the host image tool, not this gateway. Independent reviewers '
    'must see the brief, visual target, copy and neutral previews; exclude creator scores/rationale.'
)

SCHEMAS = {
 'calibration':{'genre':'expressive-poster|editorial-illustration|information-graphic','references':'3..5 {research_url,image,observation,principle,application}','image_inspection':'{performed:true,paths,observations}','image_observation':'{tool,evidence,observation}'},
 'concept_review':{'directions_sha256':'latest directions record hash','calibration_sha256':'latest calibration record hash','reviewer_id':'fresh independent identity','assessments':'three {id,composition,image_treatment,copy,brief_fit}','selected':'direction id','all_weak':'boolean','reason':'observed selection basis','unresolved_limitations':'required when weak after second pass','image_inspection':'all alternatives + calibration images','image_observation':'{tool,evidence,observation}'},
 'construction_study':{'spec_sha256':'latest spec record hash','method':'native|trace-rebuild','native':'project native study','images':'full/use previews','element_map':'semantic component -> actual study object ids','checks':'{silhouette,spacing,proportions,gesture,contours,detail}','confirmed':True,'limitations':[],'image_inspection':'both previews','image_observation':'{tool,evidence,observation}'},
 'research': {'required':['subject_summary','audience_and_use','synthesis','facts','assumptions','gaps','references'],
   'reference_fields':['title','creator','url','accessed','source_type','observation','transformation','visual_inspection'],
   'visual_inspection':{'tool':'actual host image action','evidence':'action or screenshot reference','observation':'visible feature'},
   'notes':'15-25 relevant inspected works / 4 source roles target. Disclose shortfall; one discovery + one gap pass. image_observation is agent-attested.'},
 'directions':{'directions':'three {id, concept, metaphor, visual_language, thumbnail, copy_options: [text]}; designer-v1 also composition, image_treatment, actual_copy and copy_evaluation:{specificity,clarity,tone,illustration_relationship,subject_substitution}',
   'selected':'direction id','selection_reason':'concise decision'},
 'target':{'path':'project PNG','method':'generated|vector-study','observation':'actually viewed target',
   'features':'nonempty list of concrete visual features to preserve','prompt':'required for generated target','direction_id':'designer-v1: selected concept_review direction'},
 'spec':{'canvas':{'width':900,'height':1200,'use_width':450},'locked_copy':['verbatim supplied strings'],
   'palette':['#rrggbb'],'reading_sequence':['element-id'], 'focal_silhouette':'specific shape/relationship',
   'elements':'[{id,kind:text|illustration|background|accent,stage:composition|typography|imagery|finishing,box:[x,y,w,h],text?,font?,size?,features?:[...]}]',
   'copy_rationale':'why editable copy belongs to this subject/audience','direction_id':'designer-v1: selected target direction','construction_method':'designer-v1: native|trace-rebuild','copy_evaluation':'designer-v1: {specificity,clarity,tone,illustration_relationship,subject_substitution}'},
 'begin':{'stage':'one construction stage','plan':{'purpose':'intended change','changes':'concrete edits','checks':'how preview confirms it','expected_result':'visible outcome'}},
 'checkpoint':{'version':'unique name','data':{'phase':'capture|confirm','observations':'actual full/use-size observations',
   'target_comparison':{'silhouette':'observed','proportions':'observed','negative_space':'observed','hierarchy':'observed','copy':'observed','detail':'observed'},
   'element_map':{'spec-id':['actual object ids']},'departures':[{'element':'spec-id','reason':'intentional change'}],
   'decision':'proceed or concrete adjustment'}},
 'preflight':{'version':'confirmed current snapshot','files':['SVG','PDF','PNG absolute project paths'],
   'observations':'actual export inspection; warnings and limitations'},
 'packet':{'version':'preflighted version','other':'optional original snapshot name'},
 'review':{'version':'preflighted version','reviews':'designer-v1: two {role:communication|craft,reviewer_id,review,image_observation}. Each review has eight criteria, fidelity, copy, brief_comparison:{winner:candidate|incumbent|original|equal|no_baseline,reason,regression:{present:boolean,evidence:string}}, and baseline assessments when first seen. All packet images + target must be viewed. Regression evidence concerns a new consequential loss versus retained artwork, not a score change or a weakness shared by both.', 'review':'legacy-v3: eight-factor reviewer JSON contract + visual_fidelity:{score:1..5,reason}, copy_assessment:{score:1..5|null,reason}',
   'image_observation':{'tool':'actual reviewer image tool','evidence':'reviewer action evidence','observation':'visible observations'},
   'notes':'Image paths must match neutral packet or snapshot bytes, including target. First original comparison needs incumbent_assessment.'},
 'unavailable':{'reason':'precise missing inspection/reviewer capability'},
}

def now(): return datetime.now(timezone.utc).isoformat()
def digest(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def read(path): return json.loads(Path(path).read_text(encoding='utf-8-sig'))
def atomic(path, data):
    path = Path(path); path.parent.mkdir(parents=True,exist_ok=True)
    temp = path.with_name(path.name+'.'+uuid.uuid4().hex+'.tmp')
    temp.write_text(json.dumps(data,indent=2,ensure_ascii=False),encoding='utf-8'); os.replace(temp,path)
def nonempty(value,label):
    if not isinstance(value,str) or not value.strip(): raise ValueError(label+' must be nonempty text')
def safe_id(value):
    if not isinstance(value,str) or not re.fullmatch(r'[A-Za-z0-9_-]{1,80}',value): raise ValueError('Invalid filename-safe id')
    return value
def clean_inspection(data): return {k:data[k] for k in ('artboards','layers','objects','colorMode','units') if k in data}
def result_payload(result):
    for b in result.get('content',[]):
        if b.get('type')=='text':
            try: return json.loads(b['text'])
            except ValueError: pass
    return None
def native_fingerprint(path):
    # Native document content, ignoring envelope/file path/history/UI selection.
    value=read(path)
    if value.get('format')!='vectorcraft': raise ValueError('Not native editable VectorCraft artwork')
    return hashlib.sha256(json.dumps(value['document'],sort_keys=True,separators=(',',':')).encode()).hexdigest()
def nodes_from_native(path):
    out={}
    def visit(n):
        if isinstance(n,dict):
            if 'id' in n and isinstance(n.get('kind'),dict): out[str(n['id'])]=n
            for v in n.values(): visit(v)
        elif isinstance(n,list):
            for v in n: visit(v)
    visit(read(path)['document'].get('layers',[])); return out

class Workflow:
    def __init__(self,root):
        self.root=Path(root).resolve(); self.run=None; self.state=None

    def project_file(self,path):
        p=Path(path).resolve()
        if not p.is_relative_to(self.root) or not p.is_file(): raise ValueError('Evidence must be an existing file inside the project root')
        return p

    def persist(self): atomic(self.run/'run.json',self.state)
    def artifact(self,source,role):
        source=self.project_file(source)
        dest=self.run/'evidence'/(uuid.uuid4().hex+source.suffix)
        dest.parent.mkdir(exist_ok=True);shutil.copy2(source,dest)
        return {'path':str(dest.relative_to(self.run)),'role':role,'sha256':digest(dest)}

    def verify(self):
        def walk(value):
            if isinstance(value,dict):
                if {'path','role','sha256'}<=value.keys():
                    p=(self.run/value['path']).resolve()
                    if not p.is_relative_to(self.run) or not p.is_file() or digest(p)!=value['sha256']:
                        raise ValueError('Workflow evidence integrity failed: '+str(value['path']))
                for v in value.values(): walk(v)
            elif isinstance(value,list):
                for v in value:walk(v)
        if self.state: walk(self.state)

    def start(self,backend,mode='full',brief_path=None,scope=None,run_id=None,resume=None,use_width=None,reopen_reason=None,feedback_path=None,quality_profile='designer-v1'):
        if mode not in ('full','quick'): raise ValueError('mode must be full or quick')
        if quality_profile not in ('designer-v1','legacy-v3'):raise ValueError('Unknown quality profile')
        if use_width is not None and (type(use_width) not in (int,float) or not math.isfinite(use_width) or use_width<=0):raise ValueError('Invalid original intended viewing width')
        if self.state and self.state['status']=='active': raise ValueError('An active run is already bound; finish it or resume from a fresh session')
        if resume:
            run=Path(resume).resolve()
            if not run.is_relative_to(self.root/'work/vectorcraft-studio'): raise ValueError('Resume run must be inside this project')
            state=read(run/'run.json')
            if state.get('version')!=3 or Path(state['project_root']).resolve()!=self.root: raise ValueError('Resume requires a version-three run belonging to this project')
            self.run,self.state=run,state;self.verify()
            if state['status']!='active':
                if state['status']!='review_passed' or state['revision_rounds']>=state['max_rounds']:
                    raise ValueError('Stopped or exhausted run cannot acquire extra revision budget')
                nonempty(reopen_reason,'explicit reason for new feedback')
                if not feedback_path:raise ValueError('Reopening requires a project feedback artifact')
                feedback=self.artifact(feedback_path,'followup-feedback')
                state.update(status='active',stop_reason=None,ready_versions=[])
                state['events'].append({'event':'reopen_after_new_feedback','at':now(),'reason':reopen_reason,
                    'feedback':feedback,'remaining_rounds':state['max_rounds']-state['revision_rounds']})
                self.persist()
            snap=state['versions'].get(state.get('working_version'))
            checkpoint=state.get('recovery')
            snap=snap or state['versions'].get(state.get('original_version'))
            path=(run/checkpoint['path']) if checkpoint else (run/snap['native']['path'] if snap else None)
            if path:
                backend.checked_call('open_file',{'path':str(path)})
                self.state['uncertain']=False
                self.state['events'].append({'event':'resume','at':now(),'snapshot':str(path),'pending_batch':bool(state.get('pending'))})
                self.persist()
            return self.status()
        if mode=='quick':nonempty(scope,'quick edit scope')
        if mode=='full' and not brief_path:raise ValueError('full mode requires brief_path')
        if brief_path:self.project_file(brief_path)
        run_id=safe_id(run_id or uuid.uuid4().hex[:12]); run=self.root/'work/vectorcraft-studio'/run_id
        if run.exists():raise ValueError('Run id already exists; use resume instead')
        run.mkdir(parents=True)
        self.run=run
        self.state={'format':'vectorcraft-studio-run','version':3,'project_root':str(self.root),'mode':mode,
          'quality_profile':quality_profile,
          **({'review_contract':'observed-comparison-v1'} if quality_profile=='designer-v1' and mode=='full' else {}),
          'scope':scope,'status':'active','revision':0,'spec_revision':0,'records':[], 'events':[],
          'pending':None,'completed_stages':[],'versions':{},'working_version':None,'best_version':None,
          'ready_versions':[],'reviews':[],'revision_rounds':0,'max_rounds':3,'no_improvement_streak':0,'uncertain':False}
        if brief_path:self.state['brief']=self.artifact(brief_path,'brief')
        self.persist()
        inspection=result_payload(backend.checked_call('doc_inspect',{}))
        if inspection and inspection.get('objects',0)>1:
            self.capture(backend,'original',role='original',use_width=use_width)
            self.state['original_version']='original'
        self.persist();return self.status()

    def status(self):
        self.verify()
        vault=os.environ.get('VECTORCRAFT_BRAIN',str(Path.home()/'Documents/Design Brain'))
        if not self.state:return {'active':False,'knowledge_vault':vault,'next':'workflow_start: full for substantial designs, quick for scoped small edits','schemas':SCHEMAS}
        s=self.state
        return {'run':str(self.run),'version':3,'knowledge_vault':vault,'mode':s['mode'],'quality_profile':s.get('quality_profile','legacy-v3'),'status':s['status'],'revision':s['revision'],
          'records':[r['kind'] for r in s['records']],'pending':s['pending'],'completed_stages':s['completed_stages'],
          'working_version':s['working_version'],'best_version':s['best_version'],'ready_versions':s['ready_versions'],
          'revision_rounds':s['revision_rounds'],'stop_reason':s.get('stop_reason'),'uncertain':s['uncertain'],
          'schemas':SCHEMAS,'inspection_evidence':'Agent-observed; file hashes establish bytes, not perception or taste.'}

    def require_active(self):
        if not self.state:raise ValueError('Call workflow_start before authoring artwork')
        self.verify()
        if self.state['status']!='active':raise ValueError('Run is stopped; preserve and deliver best_version')
        if self.state['uncertain']:raise ValueError('Operation outcome uncertain: inspect document and resume/reconcile before further edits')

    def latest(self,kind):return next((r for r in reversed(self.state['records']) if r['kind']==kind),None)
    def data(self,kind):
        r=self.latest(kind);return read(self.run/r['artifact']['path']) if r else None

    def guard_edit(self):
        self.require_active()
        if self.state['mode']=='quick':return
        if not all(self.latest(k) for k in ('research','directions','target','spec')):raise ValueError('Full design needs research, directions, target and spec before artwork edits')
        if not self.state['pending']:raise ValueError('Call workflow_begin with a concrete plan before artwork edits')
        if self.state['pending'].get('captured'):raise ValueError('Inspect and confirm captured previews before more edits; then plan a new batch')

    def edited(self,name,args,result,checkpoint=None,error=None):
        s=self.state
        if not s:return
        s['revision']+=1;s['ready_versions']=[]
        s['events'].append({'event':'edit','at':now(),'tool':name,'command':args.get('id',args.get('command')),
                            'revision':s['revision'],'partial_or_error':bool(error or result.get('isError') or (result_payload(result) or {}).get('failed'))})
        if checkpoint and Path(checkpoint).is_file(): s['recovery']=self.artifact(checkpoint,'recovery')
        if error or result.get('isError') or (result_payload(result) or {}).get('failed'):s['uncertain']=True
        self.persist()

    def setup_allowed(self):
        if self.state and self.state['mode']=='quick':
            self.require_active()
            return
        if self.state and (self.state['pending'] or self.state['revision']):raise ValueError('Document switching invalidates the run; use a fresh session/run or workflow_start resume')

    def note_export(self,path):
        if not self.state or not path:return
        p=self.project_file(path)
        if not p.is_file():return
        self.state.setdefault('export_provenance',{})[str(p)]={
            'revision':self.state['revision'],'spec_revision':self.state['spec_revision'],
            'sha256':digest(p),'at':now()}
        self.persist()

    def note_render(self,tool,result,path=None):
        if not self.state or result.get('isError'):return
        if path and Path(path).is_file():
            artifact=self.artifact(path,'render')
        else:
            block=next((b for b in result.get('content',[]) if b.get('type')=='image'),None)
            if not block:return
            dest=self.run/'evidence'/(uuid.uuid4().hex+'.png');dest.parent.mkdir(exist_ok=True)
            dest.write_bytes(base64.b64decode(block['data']))
            artifact={'path':str(dest.relative_to(self.run)),'role':'render','sha256':digest(dest)}
        self.state.setdefault('renders',[]).append({'tool':tool,'revision':self.state['revision'],
            'spec_revision':self.state['spec_revision'],'at':now(),'artifact':artifact,
            'observed':False,'note':'Captured bytes only; host image inspection must be recorded separately.'})
        self.persist()

    def record(self,backend,kind,data):
        import designer
        self.require_active()
        if kind not in KINDS:raise ValueError('Unknown record kind')
        if kind=='packet':return self.packet(data['version'],data.get('other'))
        if kind=='review':return designer.review(self,data) if designer.enabled(self) else self.review(data)
        if kind=='preflight':return self.preflight(backend,data)
        if kind=='unavailable':
            nonempty(data.get('reason'),'reason');self.state.update(status='review_unavailable',stop_reason=data['reason']);self.persist();return self.status()
        if self.state['mode']!='full':raise ValueError('Research/spec records belong to full mode')
        attachments=[]
        if kind in ('calibration','concept_review','construction_study'):
            if not designer.enabled(self):raise ValueError('Designer records require designer-v1 profile')
            attachments=designer.validate_record(self,kind,data)
        if kind=='research':
            if self.state['revision']:raise ValueError('Research cannot be retrofitted after artwork edits')
            # Same research contract as v2, with an explicit agent-observation disclosure.
            import importlib.util
            spec=importlib.util.spec_from_file_location('v2_pipeline',Path(__file__).parents[1]/'skills/vectorcraft-studio/scripts/pipeline.py')
            pipeline=importlib.util.module_from_spec(spec);spec.loader.exec_module(pipeline)
            pipeline.validate_research(data,True)
        elif kind=='directions':
            if designer.enabled(self):designer.validate_directions(self,data)
            if not self.latest('research'):raise ValueError('Research must precede directions')
            if self.state['revision']:raise ValueError('Directions must precede artwork edits')
            ds=data.get('directions',[])
            if len(ds)!=3 or len({d.get('id') for d in ds})!=3:raise ValueError('Three distinct directions required')
            for d in ds:
                for k in ('id','concept','metaphor','visual_language'):nonempty(d.get(k),k)
                if not isinstance(d.get('copy_options'),list):raise ValueError('Each direction needs copy_options, empty only for locked/no copy')
                attachments.append(self.artifact(d['thumbnail'],'thumbnail'))
            if len({a['sha256'] for a in attachments})!=3:raise ValueError('Direction thumbnails must be visibly distinct files, not identical copies')
            if data.get('selected') not in {d['id'] for d in ds}:raise ValueError('Select a known direction')
            nonempty(data.get('selection_reason'),'selection_reason')
        elif kind=='target':
            if designer.enabled(self):
                designer.concepts_ready(self)
                if data.get('direction_id')!=self.data('concept_review')['selected']:raise ValueError('Target must follow the selected direction')
            if not self.latest('directions'):raise ValueError('Directions must precede target')
            if self.state['pending']:raise ValueError('Confirm pending batch before changing target')
            nonempty(data.get('observation'),'target observation')
            if data.get('method') not in ('generated','vector-study'):raise ValueError('Target method must be generated or vector-study')
            if data['method']=='generated':nonempty(data.get('prompt'),'generation prompt')
            if not data.get('features') or not all(isinstance(f,str) and f.strip() for f in data['features']):raise ValueError('Target needs concrete features')
            p=self.project_file(data['path'])
            if not p.read_bytes().startswith(b'\x89PNG\r\n\x1a\n'):raise ValueError('Target must be a PNG image')
            attachments.append(self.artifact(p,'target'))
            self.state['spec_revision']+=1
        elif kind=='spec':
            if designer.enabled(self):
                designer.concepts_ready(self);designer.validate_spec(data)
                if data.get('direction_id')!=self.data('target')['direction_id']:raise ValueError('Spec must follow selected target direction')
            if not self.latest('target'):raise ValueError('Target must precede spec')
            if self.state['pending']:raise ValueError('Confirm pending batch before changing spec')
            previous=self.data('spec')
            if previous and data.get('locked_copy')!=previous.get('locked_copy'):raise ValueError('Supplied locked_copy cannot change during revisions')
            self.validate_spec(data);self.state['spec_revision']+=1
        dest=self.run/'record-input.json';atomic(dest,data)
        self.state['records'].append({'kind':kind,'at':now(),'artifact':self.artifact(dest,kind),'attachments':attachments,
                                     'inspection':'agent-observed' if kind in ('research','directions','target','calibration','concept_review','construction_study') else None,
                                     **({'spec_revision':self.state['spec_revision']} if designer.enabled(self) else {})})
        self.state['ready_versions']=[];self.persist();return self.status()

    @staticmethod
    def validate_spec(data):
        c=data.get('canvas',{})
        for k in ('width','height','use_width'):
            if type(c.get(k)) not in (int,float) or not math.isfinite(c[k]) or c[k]<=0:raise ValueError('Invalid canvas '+k)
        if c['use_width']>c['width']:raise ValueError('Use size must not enlarge the full preview')
        for k in ('focal_silhouette','copy_rationale'):nonempty(data.get(k),k)
        if not data.get('palette') or any(not re.fullmatch(r'#[0-9a-fA-F]{6}',p) for p in data['palette']):raise ValueError('Palette needs hex colors')
        es=data.get('elements',[])
        if not es or len({e.get('id') for e in es})!=len(es):raise ValueError('Unique specification element ids required')
        for e in es:
            safe_id(e.get('id'))
            if e.get('kind') not in ('text','illustration','background','accent') or e.get('stage') not in STAGES:raise ValueError('Element kind/stage invalid')
            b=e.get('box',[])
            if len(b)!=4 or any(type(v) not in (int,float) or not math.isfinite(v) for v in b) or b[2]<=0 or b[3]<=0:raise ValueError('Element box must be [x,y,positive width,height]')
            if e['kind']=='text':
                nonempty(e.get('text'),'final copy');nonempty(e.get('font'),'font')
                if type(e.get('size')) not in (int,float) or e['size']<=0:raise ValueError('Positive text size required')
            if e['kind']=='illustration' and not e.get('features'):raise ValueError('Illustration must state features that survive translation')
        locked=data.get('locked_copy')
        if not isinstance(locked,list) or not all(isinstance(t,str) and t.strip() for t in locked):raise ValueError('locked_copy must be a text list')
        combined='\n'.join(e.get('text','') for e in es)
        if any(t not in combined for t in locked):raise ValueError('Final copy changed or omitted locked supplied text')
        if not data.get('reading_sequence') or any(x not in {e['id'] for e in es} for x in data['reading_sequence']):raise ValueError('Reading sequence must reference known elements')

    def begin(self,stage,plan):
        import designer
        self.require_active();s=self.state
        if s['pending']:raise ValueError('Finish pending batch before starting another')
        if stage not in STAGES:raise ValueError('Unknown construction stage')
        if s['mode']=='full':
            if not all(self.latest(k) for k in ('research','directions','target','spec')):raise ValueError('Complete research, directions, target and spec before building')
            if any(k not in s['completed_stages'] for k in STAGES[:STAGES.index(stage)]):raise ValueError('Inspect preceding construction stages first')
            if designer.enabled(self):
                designer.concepts_ready(self)
                if stage in ('imagery','finishing'):designer.require_study(self)
        for k in ('purpose','changes','checks','expected_result'):nonempty(plan.get(k),k)
        s['pending']={'stage':stage,'plan':plan,'at':now(),'start_revision':s['revision'],'spec_revision':s['spec_revision']}
        s['ready_versions']=[];s['events'].append({'event':'begin',**s['pending']});self.persist();return self.status()

    def capture(self,backend,version,role='working',use_width=None):
        safe_id(version);s=self.state
        if version in s['versions']:raise ValueError('Snapshot version already exists')
        dest=self.run/'versions'/version;dest.mkdir(parents=True)
        native=dest/'artwork.vectorcraft';backend.checked_call('export',{'format':'vectorcraft','path':str(native)})
        inspection=result_payload(backend.checked_call('doc_inspect',{}))
        atomic(dest/'inspection.json',clean_inspection(inspection))
        board=inspection['artboards'][0];scale=min(1,(use_width or board['width']/2)/board['width'])
        for name,ratio in (('full.png',1),('use.png',scale)):
            result=backend.checked_call('screenshot',{'path':str(dest/name),'scale':ratio})
            if not (dest/name).is_file():
                b=next((b for b in result.get('content',[]) if b.get('type')=='image'),None)
                if not b:raise ValueError('Renderer returned no image')
                (dest/name).write_bytes(base64.b64decode(b['data']))
        def art(p,role):return {'path':str(p.relative_to(self.run)),'role':role,'sha256':digest(p)}
        snap={'native':art(native,'native'),'images':[art(dest/n,'image') for n in ('full.png','use.png')],
              'inspection':art(dest/'inspection.json','inspection'),'role':role,'at':now(),'revision':s['revision'],
              'spec_revision':s['spec_revision'],'fingerprint':native_fingerprint(native),'confirmed':role=='original'}
        s['versions'][version]=snap;self.persist()
        return {'version':version,'native':str(native),'images':[str(self.run/a['path']) for a in snap['images']],
                'inspection':str(dest/'inspection.json'),'next':'Actually view both images, compare target, then workflow_checkpoint phase confirm'}

    def checkpoint(self,backend,version,data):
        self.require_active();s=self.state;pending=s['pending']
        if not pending:raise ValueError('Checkpoint requires a planned batch')
        phase=data.get('phase','capture')
        if phase=='capture':
            if pending.get('captured'):raise ValueError('Preview already captured; inspect and confirm it')
            spec=self.data('spec') or {};result=self.capture(backend,version,use_width=spec.get('canvas',{}).get('use_width'))
            pending['captured']=version;self.persist();return result
        if phase!='confirm' or pending.get('captured')!=version:raise ValueError('Confirm the captured version')
        snap=s['versions'][version]
        if snap['revision']!=s['revision'] or snap['spec_revision']!=s['spec_revision']:raise ValueError('Stale preview/spec; capture current artwork')
        self.assert_current(backend,snap)
        nonempty(data.get('observations'),'actual image observations');nonempty(data.get('decision'),'decision')
        if s['mode']=='full':
            for k in ('silhouette','proportions','negative_space','hierarchy','copy','detail'):nonempty(data.get('target_comparison',{}).get(k),'target_comparison.'+k)
            spec=self.data('spec');nodes=nodes_from_native(self.run/snap['native']['path'])
            mapping=data.get('element_map',{})
            reached=set(s['completed_stages'])|{pending['stage']}
            for e in spec['elements']:
                if e['stage'] in reached and (not mapping.get(e['id']) or any(str(i) not in nodes for i in mapping[e['id']])):
                    raise ValueError('Missing actual document objects for '+e['id'])
            for dep in data.get('departures',[]):
                if dep.get('element') not in {e['id'] for e in spec['elements']}:raise ValueError('Unknown departure element')
                nonempty(dep.get('reason'),'intentional departure rationale')
            snap['element_map']=mapping
        dest=self.run/'check-input.json';atomic(dest,data);snap['check']=self.artifact(dest,'agent-observation');snap['confirmed']=True
        s['events'].append({'event':'checkpoint','at':now(),'version':version,'stage':pending['stage'],'revision':s['revision']})
        if pending['stage'] not in s['completed_stages']:s['completed_stages'].append(pending['stage'])
        s['working_version']=version;s['pending']=None;self.persist();return self.status()

    def assert_current(self,backend,snap):
        tmp=self.run/'current-check.vectorcraft';backend.checked_call('export',{'format':'vectorcraft','path':str(tmp)})
        if native_fingerprint(tmp)!=snap['fingerprint']:raise ValueError('Document changed outside this snapshot; reconcile and capture a new batch')

    def preflight(self,backend,data):
        s=self.state;v=data['version'];snap=s['versions'].get(v)
        if s['pending'] or not snap or not snap['confirmed'] or v!=s['working_version'] or snap['revision']!=s['revision'] or snap['spec_revision']!=s['spec_revision']:
            raise ValueError('Preflight requires the confirmed current version without pending edits')
        if s['mode']=='full' and set(s['completed_stages'])!=set(STAGES):raise ValueError('Finish all four inspected construction stages')
        self.assert_current(backend,snap);nonempty(data.get('observations'),'export inspection')
        nodes=nodes_from_native(self.run/snap['native']['path']);issues=[];spec=self.data('spec')
        if s['mode']=='full':
            kinds=[n['kind'].get('type') for n in nodes.values()]
            if any(k in ('image','image_trace') for k in kinds):issues.append('Raster image or unexpanded trace remains in vector final')
            fonts=result_payload(backend.checked_call('command_run',{'id':'text.fonts','params':{}}))
            if not isinstance(fonts,list):raise ValueError('Cannot inspect actual font status')
            if any(f.get('status')!='exact' or f.get('missingGlyphs') for f in fonts):issues.append('Missing/substituted font or glyphs')
            inspection=read(self.run/snap['inspection']['path'])
            inspect_nodes={}
            def visit(n):
                if isinstance(n,dict):
                    if 'id' in n:inspect_nodes[str(n['id'])]=n
                    for k,val in n.items():
                        if k in ('children','layers'):visit(val)
                elif isinstance(n,list):
                    for val in n:visit(val)
            visit(inspection)
            for e in spec['elements']:
                ids=snap['element_map'].get(e['id'],[])
                if e['kind']=='text':
                    actual=[]
                    for i in ids:
                        n=inspect_nodes.get(str(i),{})
                        if n.get('kind')!='Type':issues.append('Text mapped to non-live-type object: '+e['id'])
                        actual.append(n.get('text',''))
                        # The native type data and text.areaOptions report overflow when area type is present.
                        if n.get('overflow') or n.get('fitScale',1)<1:issues.append('Text overflow/shrink: '+e['id'])
                        typ=nodes.get(str(i),{}).get('kind',{})
                        if typ.get('type')=='text' and typ.get('kind',{}).get('kind')=='area':
                            result=result_payload(backend.checked_call('command_run',{'id':'text.areaOptions','params':{'ids':[i]}}))
                            if isinstance(result,dict) and (result.get('overflow') or result.get('fitScale',1)<1):issues.append('Text overflow/shrink: '+e['id'])
                    if '\n'.join(actual)!=e['text']:issues.append('Rendered copy differs from spec: '+e['id'])
            for t in spec['locked_copy']:
                if t not in '\n'.join(n.get('text','') for n in inspect_nodes.values() if n.get('kind')=='Type'):issues.append('Locked text absent: '+t)
            anchors=sum(n.get('anchors',0) for n in inspect_nodes.values())
            if anchors>spec.get('anchor_budget',30000):issues.append('Excessive tracing anchors: '+str(anchors))
            canvas=spec['canvas'];boards=inspection.get('artboards',[])
            if not boards or abs(boards[0]['width']-canvas['width'])>.1 or abs(boards[0]['height']-canvas['height'])>.1:issues.append('Actual artboard differs from planned canvas')
            bleed=set(spec.get('intentional_bleed',[]))
            for e in spec['elements']:
                if e['id'] in bleed:continue
                for i in snap['element_map'].get(e['id'],[]):
                    b=inspect_nodes.get(str(i),{}).get('bounds',{})
                    if b and (b.get('x',0)<-1 or b.get('y',0)<-1 or b.get('x',0)+b.get('width',0)>canvas['width']+1 or b.get('y',0)+b.get('height',0)>canvas['height']+1):issues.append('Unintended clipping: '+e['id'])
        if issues:raise ValueError('Preflight failed: '+'; '.join(issues))
        files=data.get('files',[])
        if not files:raise ValueError('Actual exports required')
        if s['mode']=='full' and not {'.svg','.pdf','.png'} <= {Path(f).suffix.lower() for f in files}:raise ValueError('Full final requires SVG, PDF and PNG exports')
        artifacts=[]
        for f in files:
            p=self.project_file(f)
            if p.stat().st_size==0:raise ValueError('Empty export')
            provenance=s.get('export_provenance',{}).get(str(p))
            if not provenance or provenance['revision']!=s['revision'] or provenance['spec_revision']!=s['spec_revision'] or provenance['sha256']!=digest(p):raise ValueError('Stale or unbound export: '+str(p))
            if p.suffix.lower()=='.svg':
                import xml.etree.ElementTree as ET
                root=ET.parse(p).getroot()
                if s['mode']=='full' and any(n.tag.split('}')[-1]=='image' for n in root.iter()):raise ValueError('SVG contains raster image')
            artifacts.append(self.artifact(p,'export'))
        snap['exports']=artifacts;s['ready_versions']=[v]
        s['events'].append({'event':'preflight','version':v,'at':now(),'observations':data['observations']})
        self.persist();return self.status()

    def packet(self,version,other=None):
        s=self.state
        if version not in s['ready_versions']:raise ValueError('Preflight before independent review')
        incumbent=other or s['best_version'] or s.get('original_version')
        if incumbent==version:incumbent=None
        packet=self.run/'review-packets'/uuid.uuid4().hex[:12];packet.mkdir(parents=True)
        if s.get('brief'):shutil.copy2(self.run/s['brief']['path'],packet/'brief.md')
        target=self.latest('target')
        if target:shutil.copy2(self.run/target['attachments'][0]['path'],packet/'target.png')
        spec=self.data('spec')
        if spec:
            # Observable design requirements only, no selection rationale or expected verdict.
            atomic(packet/'requirements.json',{k:spec[k] for k in ('canvas','locked_copy','elements','focal_silhouette')})
        paths={}
        comparisons=[('A',version)]+([('B',incumbent)] if incumbent else [])
        if s.get('quality_profile')=='designer-v1' and s.get('original_version') not in (None,version,incumbent):comparisons.append(('C',s['original_version']))
        for label,v in comparisons:
            if v not in s['versions']:raise ValueError('Unknown comparison version')
            d=packet/label;d.mkdir();paths[label]=[];snap=s['versions'][v]
            for a in [*snap['images'],snap['inspection']]:
                dest=d/Path(a['path']).name;shutil.copy2(self.run/a['path'],dest);paths[label].append(str(dest))
        s['packets']=s.get('packets',[])+[{'path':str(packet.relative_to(self.run)),'version':version,'incumbent':incumbent}]
        self.persist();return {'packet':str(packet),'brief':str(packet/'brief.md'),'target':str(packet/'target.png') if target else None,
                               'requirements':str(packet/'requirements.json') if spec else None,'images':paths,'inspection_evidence':'Verify actual reviewer image tool use separately.'}

    def validate_review(self,review,images,include_target=True):
        obs=review.get('image_inspection',{})
        if obs.get('performed') is not True or not obs.get('observations'):raise ValueError('Review needs actual image observations')
        seen=[self.project_file(p) for p in obs.get('paths',[])]
        expected=list(images)
        if include_target and self.latest('target'):expected.append(self.run/self.latest('target')['attachments'][0]['path'])
        if any(not any(digest(p)==digest(e) for p in seen) for e in expected):raise ValueError('Reviewer must inspect full/use-size images and target')
        scores=review.get('scores',{})
        if set(scores)!=set(CRITERIA):raise ValueError('Eight criteria required')
        applicable=[]
        for k,item in [*scores.items(),('visual_fidelity',review.get('visual_fidelity',{})),('copy_assessment',review.get('copy_assessment',{}))]:
            nonempty(item.get('reason'),k+' evidence');score=item.get('score')
            if k=='visual_fidelity' and score is None and include_target:raise ValueError('Visual fidelity must be assessed')
            if score is not None:
                if type(score)!=int or score not in range(1,6):raise ValueError('Score must be 1..5 or null')
                if k!='visual_fidelity' or include_target:applicable.append(score)
        if not applicable:raise ValueError('No applicable judgments')
        if not isinstance(review.get('findings'),list):raise ValueError('Findings required')
        for f in review['findings']:
            if f.get('criterion') not in (*CRITERIA,'visual_fidelity','copy_assessment') or f.get('severity') not in ('critical','major','minor','preference'):raise ValueError('Invalid finding')
            for k in ('location','evidence','impact','fix'):nonempty(f.get(k),k)
        comp=review.get('comparison',{})
        if comp.get('winner') not in ('candidate','incumbent','equal','no_baseline'):raise ValueError('Comparison verdict required')
        nonempty(comp.get('reason'),'comparison reason');nonempty(review.get('summary'),'summary')
        return min(applicable)>=4 and not any(f['severity'] in ('critical','major') for f in review['findings'])

    def review(self,data):
        s=self.state;version=data['version'];review=data['review']
        if version not in s['ready_versions']:raise ValueError('Stale or missing preflight')
        if any(r['version']==version for r in s['reviews']):raise ValueError('Version already reviewed')
        observation=data.get('image_observation',{})
        for k in ('tool','evidence','observation'):nonempty(observation.get(k),'reviewer '+k)
        packet=next((p for p in reversed(s.get('packets',[])) if p['version']==version),None)
        if not packet:raise ValueError('Create a neutral packet before review')
        incumbent=s['best_version'] or s.get('original_version')
        if packet['incumbent']!=incumbent:raise ValueError('Review must compare against current best/original')
        versions=[version]+([incumbent] if incumbent else [])
        images=[self.run/a['path'] for v in versions for a in s['versions'][v]['images']]
        passed=self.validate_review(review,images);winner=review['comparison']['winner']
        if bool(incumbent)==(winner=='no_baseline'):raise ValueError('Comparison does not match supplied baseline')
        old=None
        if incumbent:
            previous=next((r for r in reversed(s['reviews']) if r['version']==incumbent),None)
            old=read(self.run/previous['artifact']['path']) if previous else review.get('incumbent_assessment')
            if not old:raise ValueError('First comparison needs full incumbent_assessment')
            if not previous:
                self.validate_review(old,[self.run/a['path'] for a in s['versions'][incumbent]['images']],include_target=False)
        accepted=incumbent is None or winner=='candidate'
        if old:
            for k in ('brief','typography','craft'):
                a=review['scores'][k]['score'];b=old['scores'][k]['score']
                if a is not None and b is not None and a<b:accepted=False
            old_major={(f['criterion'],f['location']) for f in old['findings'] if f['severity'] in ('critical','major')}
            if any(f['severity'] in ('critical','major') and (f['criterion'],f['location']) not in old_major for f in review['findings']):accepted=False
        p=self.run/'review-input.json';atomic(p,review)
        s['reviews'].append({'version':version,'artifact':self.artifact(p,'review'),'accepted_as_best':accepted,
                            'passed':passed,'image_observation':observation,'at':now()})
        if incumbent and old and not any(r['version']==incumbent for r in s['reviews']):
            atomic(p,old);s['reviews'].append({'version':incumbent,'artifact':self.artifact(p,'review'),
              'accepted_as_best':not accepted,'passed':self.validate_review(old,[self.run/a['path'] for a in s['versions'][incumbent]['images']],False),'image_observation':observation,'at':now()})
        first=s['best_version'] is None
        if accepted:s['best_version']=version
        elif not s['best_version']:s['best_version']=incumbent
        if not first:
            s['revision_rounds']+=1;s['no_improvement_streak']=0 if accepted else s['no_improvement_streak']+1
        best_review=next(r for r in reversed(s['reviews']) if r['version']==s['best_version'])
        if best_review['passed']:s.update(status='review_passed',stop_reason='Best version passed applicable independent criteria')
        elif s['no_improvement_streak']>=2:s.update(status='stalled',stop_reason='Two non-improving corrections; preserve best')
        elif s['revision_rounds']>=s['max_rounds']:s.update(status='budget_exhausted',stop_reason='Three correction rounds used; preserve best and disclose weaknesses')
        self.persist();return self.status()

def tool_definitions():
    defs=[('workflow_start','Start or resume design workflow',{'mode':{'enum':['full','quick'],'default':'full'},'quality_profile':{'enum':['designer-v1','legacy-v3'],'default':'designer-v1','description':'Legacy profile for explicit compatibility/evaluation; historical resumes keep their stored contract.'},'brief_path':{'type':'string'},'scope':{'type':'string'},'run_id':{'type':'string'},'resume':{'type':'string'},'use_width':{'type':'number','exclusiveMinimum':0},'reopen_reason':{'type':'string'},'feedback_path':{'type':'string'}},[]),
      ('workflow_record','Record research, directions, target, spec, preflight, packet or independent review',{'kind':{'enum':list(KINDS)},'data':{'type':'object'}},['kind','data']),
      ('workflow_begin','Plan an authoring batch',{'stage':{'enum':list(STAGES)},'plan':{'type':'object'}},['stage','plan']),
      ('workflow_checkpoint','Capture then confirm full/use-size previews against the target',{'version':{'type':'string'},'data':{'type':'object'}},['version','data']),
      ('workflow_status','Inspect workflow state, integrity and schemas',{},[])]
    return [{'name':name,'title':title,'description':title+'. See workflow_status schemas. Agent judgments are observed/attested, not proven by file hashes.',
      'inputSchema':{'type':'object','properties':props,'required':required,'additionalProperties':False},
      'annotations':{'readOnlyHint':name=='workflow_status','destructiveHint':False,'idempotentHint':name=='workflow_status','openWorldHint':False}} for name,title,props,required in defs]
