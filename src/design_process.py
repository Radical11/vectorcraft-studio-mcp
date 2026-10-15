"""Opt-in native study and relationship contracts; visual judgments stay attested."""
from copy import deepcopy
import hashlib
import json
import math
from pathlib import Path
from workflow import atomic, read, now, safe_id, nonempty, nodes_from_native, digest
import designer

PROFILES=('layout-blockout-v1','designer-process-v1')
KINDS=('design_brief','layout','blockout','entity_graph','assembly','relation_check')
SCHEMA={
 'design_brief':{'required':'audience,message,response,viewing_context,medium,production_requirements,assumptions,style; locked_copy list'},
 'layout':{'alternatives':'three {id,concept,reading_order,negative_space,copy,bounds}; normalized [x,y,w,h] boxes'},
 'study_begin':{'stage':'composition','plan':'context:study, study_id, layout_id, purpose,changes,expected_result,checks (2..3 {id,description})'},
 'study_confirm':{'outcome':'pass|revise|blocked','checks':'exact check_results with observed pass|fail|not_applicable; inapplicable reason','image_inspection':'full/use images','image_observation':'actual action evidence','close_study':'true only on pass or explicitly abandoned blocked study'},
 'blockout':{'study_id':'closed passed native study bound to current layout'},
 'directions':'IDs match layout IDs; thumbnails match corresponding registered study bytes; actual_copy is a nonempty string covering its native live text',
 'assembly':{'action':'start explicitly opens selected blockout before production; progress records observation'},
 'entity_graph':{'entities':'[{id,spec_id,role,parent?,anchors:{name:[fraction_x,fraction_y]}}]','relations':'[{id,kind,a,b,anchor_a?,anchor_b?,tolerance?,axis?}]','dependencies':'[[prerequisite,dependent]]; acyclic'},
 'relation_check':{'version':'current confirmed production capture','element_map':'graph entity -> actual native IDs','observations':'relation ID -> {outcome,observation,reason?}','image_inspection':'full/use/target','image_observation':'actual action evidence'},
 'limits':'Scope and bounding-box anchors are guidance/diagnostics, never semantic or aesthetic proof.'}

def enabled(w): return bool(w.state and w.state.get('quality_profile') in PROFILES and w.state['mode']=='full')
def full(w): return enabled(w) and w.state['quality_profile']=='designer-process-v1'
def initialize(w):
    w.state['design_process']={'contract':1,'active_study':None,'studies':{},'started':False,
                               'relations':{},'mapping':{},'fingerprints':{}}
def state(w): return w.state['design_process']
def append(w,kind,data,attachments=None):
    dest=w.run/'process-record.json';atomic(dest,data)
    w.state['records'].append({'kind':kind,'at':now(),'artifact':w.artifact(dest,kind),
                              'attachments':attachments or [],'spec_revision':w.state['spec_revision']})
    w.persist()
def finite(value): return type(value) in (int,float) and math.isfinite(value)
def acyclic(ids,edges):
    outgoing={i:[] for i in ids}; visiting=set();visited=set()
    for a,b in edges:
        if a not in outgoing or b not in outgoing or a==b: raise ValueError('Invalid dependency/parent endpoint')
        outgoing[a].append(b)
    def visit(n):
        if n in visiting: raise ValueError('Construction/parent graph must be acyclic')
        if n in visited:return
        visiting.add(n)
        for child in outgoing[n]:visit(child)
        visiting.remove(n);visited.add(n)
    for i in ids:visit(i)
def validate_graph(w,data):
    entities=data.get('entities',[]);ids=[e.get('id') for e in entities]
    if not ids or len(set(ids))!=len(ids):raise ValueError('Unique meaningful entities required')
    specs={e['id'] for e in w.data('spec')['elements']}
    for e in entities:
        safe_id(e['id']); nonempty(e.get('role'),'entity role')
        if e.get('spec_id') not in specs:raise ValueError('Graph entity must bind to current spec')
        for name,point in e.get('anchors',{}).items():
            safe_id(name)
            if len(point)!=2 or any(not finite(v) or not 0<=v<=1 for v in point):raise ValueError('Normalized native-bounds anchors required')
    acyclic(ids,[(e['parent'],e['id']) for e in entities if e.get('parent')])
    acyclic(ids,data.get('dependencies',[]))
    relations=data.get('relations',[]);rids=[r.get('id') for r in relations]
    if len(set(rids))!=len(rids):raise ValueError('Unique relation IDs required')
    em={e['id']:e for e in entities}
    for r in relations:
        safe_id(r['id'])
        if r.get('a') not in em or r.get('b') not in em:raise ValueError('Unknown spatial endpoint')
        if r.get('kind') not in ('contact','grip','association','occlusion','anchor_distance','containment','alignment'):raise ValueError('Unknown relation kind')
        if r['kind'] in ('anchor_distance','alignment'):
            if any(r.get('anchor_'+suffix) not in em[r[suffix]].get('anchors',{}) for suffix in ('a','b')):raise ValueError('Named anchors required')
            if not finite(r.get('tolerance')) or r['tolerance']<0:raise ValueError('Explicit diagnostic tolerance required')
        if r['kind']=='alignment' and r.get('axis') not in ('x','y'):raise ValueError('Alignment axis required')

def fingerprints(path,mapping):
    nodes=nodes_from_native(path);out={};parents={};order={}
    def walk(value,ancestors=()):
        if isinstance(value,dict):
            chain=ancestors
            if 'id' in value and isinstance(value.get('kind'),dict):
                identifier=str(value['id']);parents[identifier]=ancestors;order[identifier]=len(order)
                chain=(*ancestors,identifier)
            for v in value.values():walk(v,chain)
        elif isinstance(value,list):
            for v in value:walk(v,ancestors)
    walk(read(path)['document'].get('layers',[]))
    def shell(n):
        # Ancestor transforms/paint/order matter; descendant data is hashed in the selected node.
        return {k:v for k,v in n.items() if k not in ('children',) and k!='kind'} | {'kind':{k:v for k,v in n.get('kind',{}).items() if k!='children'}}
    for entity,ids in mapping.items():
        if not ids or any(str(i) not in nodes for i in ids):raise ValueError('Missing native entity mapping')
        pieces=[{'node':nodes[str(i)],'order':order[str(i)],'ancestors':[shell(nodes[a]) for a in parents[str(i)]]} for i in ids]
        out[entity]=hashlib.sha256(json.dumps(pieces,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    return out
def invalidate(w,checkpoint=None):
    if not full(w):return
    p=state(w);graph=w.data('entity_graph')
    if not graph:return
    affected=None
    if checkpoint and p['mapping'] and p['fingerprints']:
        try:
            current=fingerprints(checkpoint,p['mapping'])
            affected={e for e in current if current[e]!=p['fingerprints'].get(e)}
            # Unmapped edits cannot be localized reliably: compare the entire native document.
            previous=p.get('checked_native')
            if previous:
                previous_doc=read(w.run/previous['path'])['document'];current_doc=read(checkpoint)['document']
                if {k:v for k,v in previous_doc.items() if k!='layers'}!={k:v for k,v in current_doc.items() if k!='layers'}:affected=None
                old=nodes_from_native(w.run/previous['path']);new=nodes_from_native(checkpoint)
                known={str(i) for ids in p['mapping'].values() for i in ids}
                def own(n):
                    if n is None:return None
                    return {k:v for k,v in n.items() if k not in ('children','kind')} | {'kind':{k:v for k,v in n.get('kind',{}).items() if k!='children'}}
                changed={i for i in set(old)|set(new) if own(old.get(i))!=own(new.get(i))}
                if changed-known:affected=None
        except (ValueError,KeyError,TypeError):affected=None
    for r in graph['relations']:
        if affected is None or {r['a'],r['b']} & affected:
            if r['id'] in p['relations']:p['relations'][r['id']]['current']=False
    p['last_invalidation']={'revision':w.state['revision'],'affected_entities':None if affected is None else sorted(affected)}

def record(w,backend,kind,data):
    if not enabled(w):raise ValueError('Record requires an experimental designer-process profile')
    p=state(w)
    if p['active_study']:raise ValueError('Close the active study before parent records')
    if kind=='design_brief':
        if w.state['revision'] or p['studies'] or p['started']:raise ValueError('Brief must precede studies and construction')
        for k in ('audience','message','response','viewing_context','medium','production_requirements','style'):nonempty(data.get(k),k)
        if not isinstance(data.get('assumptions'),list) or not isinstance(data.get('locked_copy'),list):raise ValueError('Explicit assumptions and locked copy lists required')
    elif kind=='layout':
        if not all(w.latest(k) for k in ('design_brief','research','calibration')):raise ValueError('Brief/research/calibration before layouts')
        if p['started'] or w.state['revision']:raise ValueError('Layouts must precede production')
        alternatives=data.get('alternatives',[])
        if len(alternatives)!=3 or len({a.get('id') for a in alternatives})!=3:raise ValueError('Three distinct concept layouts required')
        for a in alternatives:
            safe_id(a['id'])
            for k in ('concept','reading_order','negative_space'):nonempty(a.get(k),k)
            if not isinstance(a.get('copy'),list):raise ValueError('Actual copy list required')
            if any(copy not in '\n'.join(a['copy']) for copy in w.data('design_brief')['locked_copy']):raise ValueError('Layout lost locked copy')
            if not a.get('bounds'):raise ValueError('Layout bounds required')
            for box in a['bounds'].values():
                if len(box)!=4 or any(not finite(v) or not 0<=v<=1 for v in box) or box[2]<=0 or box[3]<=0 or box[0]+box[2]>1.00001 or box[1]+box[3]>1.00001:raise ValueError('Normalized in-canvas layout bounds required')
    elif kind=='blockout':
        study=p['studies'].get(data.get('study_id'))
        if not study or study['outcome']!='pass' or not study.get('closed') or study['layout_sha256']!=w.latest('layout')['artifact']['sha256']:raise ValueError('Current passed native study required')
        data={**data,'layout_id':study['layout_id'],'native':study['native'],'images':study['images'],'observation':study['observation']}
    elif kind=='assembly':
        if data.get('action')=='start':
            if p['started'] or w.state['pending'] or w.state['revision']:raise ValueError('Production transition is single-use before edits')
            designer.concepts_ready(w)
            if not w.latest('spec'):raise ValueError('Target/spec before production transition')
            selected=w.data('concept_review')['selected'];study=p['studies'].get(data.get('study_id'))
            if not study or study['outcome']!='pass' or not study.get('closed') or study['layout_id']!=selected or study['layout_sha256']!=w.latest('layout')['artifact']['sha256']:raise ValueError('Transition must use the selected current blockout')
            try:backend.checked_call('open_file',{'path':str(w.run/study['native']['path'])})
            except Exception:
                w.state['uncertain']=True;w.persist();raise
            w.state['recovery']=study['native'];p['started']=True
            p['production_seed']={'native':study['native'],'images':study['images'],'revision':w.state['revision'],
                                  'spec_revision':w.state['spec_revision']}
        elif data.get('action')=='progress':nonempty(data.get('observation'),'assembly observation')
        else:raise ValueError('Explicit assembly action required')
    elif kind=='entity_graph':
        if not full(w):raise ValueError('Relations belong to designer-process-v1 only')
        if not p['started'] or w.state['pending']:raise ValueError('Graph after transition, outside pending batch')
        validate_graph(w,data);p['relations']={};p['mapping']={};p['fingerprints']={}
    elif kind=='relation_check':
        if not full(w) or not w.latest('entity_graph'):raise ValueError('Current entity graph required')
        return check_relations(w,data)
    append(w,kind,data);return w.response()

def guard_begin(w):
    if not enabled(w):return
    if state(w)['active_study']:raise ValueError('Finish isolated study before production')
    if not state(w)['started']:raise ValueError('Explicit selected-blockout production transition required')
    if full(w) and (not w.latest('entity_graph') or w.latest('entity_graph')['spec_revision']!=w.state['spec_revision']):raise ValueError('Declare current entity graph before production batches')
def guard_directions(w,data=None):
    if not enabled(w):return
    layout=w.latest('layout')
    if not layout:raise ValueError('Native layouts/blockouts before directions')
    expected={a['id'] for a in w.data('layout')['alternatives']}
    registrations=[read(w.run/r['artifact']['path']) for r in w.state['records'] if r['kind']=='blockout']
    registered={r['study_id'] for r in registrations}
    studies={s['layout_id']:s for identifier,s in state(w)['studies'].items() if identifier in registered
             and s.get('outcome')=='pass' and s.get('closed') and s['layout_sha256']==layout['artifact']['sha256']}
    records={r['layout_id'] for r in registrations}
    if expected-set(studies) or expected-records:raise ValueError('Three actually observed native blockouts required')
    if data is not None:
        directions=data.get('directions',[])
        if {d.get('id') for d in directions}!=expected:raise ValueError('Direction IDs must match the current layout IDs')
        for direction in directions:
            image=Path(direction.get('thumbnail',''))
            study=studies[direction['id']]
            if not image.is_file() or digest(image) not in {a['sha256'] for a in study['images']}:
                raise ValueError('Direction thumbnail must match its observed native blockout image')
            nonempty(direction.get('actual_copy'),'direction actual_copy')
            actual_copy=' '.join(direction['actual_copy'].split())
            nodes=nodes_from_native(w.run/study['native']['path'])
            for node in nodes.values():
                kind=node['kind']
                if kind.get('type')=='text':
                    text=' '.join(''.join(run.get('text','') for run in kind.get('runs',[])).split())
                    if text and text not in actual_copy:raise ValueError('Direction actual_copy must cover its native blockout live text')

def concept_images(w):
    if not enabled(w):return []
    layout=w.latest('layout')
    expected={a['id'] for a in w.data('layout')['alternatives']}
    registered={read(w.run/r['artifact']['path'])['study_id'] for r in w.state['records'] if r['kind']=='blockout'}
    return [w.run/a['path'] for identifier,study in state(w)['studies'].items() if identifier in registered
            if study['layout_id'] in expected and study.get('outcome')=='pass' and study.get('closed')
            and study['layout_sha256']==layout['artifact']['sha256'] for a in study['images']]

def check_relations(w,data):
    p=state(w);s=w.state;snap=s['versions'].get(data.get('version'));graph=w.data('entity_graph')
    if s['pending'] or not snap or not snap['confirmed'] or snap['revision']!=s['revision'] or snap['spec_revision']!=s['spec_revision']:raise ValueError('Current confirmed production image required')
    if w.latest('entity_graph')['spec_revision']!=s['spec_revision']:raise ValueError('Stale entity graph; reconcile amended specification')
    validate_graph(w,graph)
    paths=[w.run/a['path'] for a in snap['images']]+[w.run/w.latest('target')['attachments'][0]['path']]
    designer.inspection(w,data,paths)
    mapping=data.get('element_map',{});em={e['id']:e for e in graph['entities']}
    if set(mapping)!=set(em):raise ValueError('Map all graph entities to actual native objects')
    fp=fingerprints(w.run/snap['native']['path'],mapping)
    inspection=read(w.run/snap['inspection']['path']);bounds={}
    def collect(n):
        if isinstance(n,dict):
            if 'id' in n and 'bounds' in n:bounds[str(n['id'])]=n['bounds']
            for v in n.values():collect(v)
        elif isinstance(n,list):
            for v in n:collect(v)
    collect(inspection)
    def box(e):
        bs=[bounds.get(str(i)) for i in mapping[e]]
        if any(not b or any(not finite(b.get(k)) for k in ('x','y','width','height')) for b in bs):raise ValueError('Native inspector bounds required')
        return [min(b['x'] for b in bs),min(b['y'] for b in bs),max(b['x']+b['width'] for b in bs),max(b['y']+b['height'] for b in bs)]
    def anchor(e,name):
        x,y,r,b=box(e);fx,fy=em[e]['anchors'][name];return (x+(r-x)*fx,y+(b-y)*fy)
    observations=data.get('observations',{})
    if set(observations)!={r['id'] for r in graph['relations']}:raise ValueError('Observe every declared relationship')
    checks={}
    for r in graph['relations']:
        observation=observations[r['id']];outcome=observation.get('outcome')
        if outcome not in ('pass','fail','not_applicable'):raise ValueError('Explicit relation outcome required')
        nonempty(observation.get('observation'),'visible relation observation')
        if outcome=='not_applicable':nonempty(observation.get('reason'),'inapplicable relation reason')
        diagnostic=None
        if r['kind'] in ('anchor_distance','alignment'):
            a=anchor(r['a'],r['anchor_a']);b=anchor(r['b'],r['anchor_b'])
            diagnostic=math.dist(a,b) if r['kind']=='anchor_distance' else abs(a[0 if r['axis']=='x' else 1]-b[0 if r['axis']=='x' else 1])
            if diagnostic>r['tolerance'] and outcome=='pass':raise ValueError('Geometric diagnostic failed; cannot attest a pass')
        elif r['kind']=='containment':
            a=box(r['a']);b=box(r['b']);diagnostic=a[0]<=b[0] and a[1]<=b[1] and a[2]>=b[2] and a[3]>=b[3]
            if not diagnostic and outcome=='pass':raise ValueError('Containment diagnostic failed')
        checks[r['id']]={**observation,'diagnostic':diagnostic,'current':True,'spec_revision':s['spec_revision'],
                         'entity_fingerprints':{e:fp[e] for e in (r['a'],r['b'])}}
    p.update(relations=checks,mapping=deepcopy(mapping),fingerprints=fp,checked_native=snap['native'])
    # Visual failed relationships become consequential tasks; the builder still chooses the repair.
    f=s['focused'];f['queue']=[q for q in f['queue'] if not q['id'].startswith('relation-')]
    for r in graph['relations']:
        if checks[r['id']]['outcome']=='fail':
            f['queue'].append({'id':'relation-'+r['id'],'stage':'imagery','entities':list(dict.fromkeys(em[e]['spec_id'] for e in (r['a'],r['b']))),
                              'reason':checks[r['id']]['observation'],'severity':'major','revision':s['revision'],'spec_revision':s['spec_revision']})
    append(w,'relation_check',data);return w.response()
def preflight(w):
    if not enabled(w):return
    if state(w)['active_study'] or not state(w)['started']:raise ValueError('Production transition and closed studies required')
    if full(w):
        graph=w.data('entity_graph');checks=state(w)['relations']
        if not graph or any(not checks.get(r['id'],{}).get('current') or checks[r['id']]['outcome']=='fail' for r in graph['relations']):raise ValueError('Unresolved or stale relationships block preflight')
def packet(w):
    import focused
    p=state(w);s=w.state
    result=focused.packet(w) if full(w) else {'profile':s['quality_profile'],'run':str(w.run),'revision':s['revision'],'status':s['status'],'stage':(s.get('pending') or {}).get('stage')}
    result['profile']=s['quality_profile'];result['active_study']=p['active_study']
    version=(s['pending'] or {}).get('captured') or s['working_version']
    preview=s['versions'].get(version) or p.get('production_seed')
    if preview:
        result.update(full_preview=str(w.run/preview['images'][0]['path']),use_preview=str(w.run/preview['images'][1]['path']),
                      preview_revision=preview['revision'],preview_context='production',
                      preview_current=preview['revision']==s['revision'] and preview['spec_revision']==s['spec_revision'] and not s['uncertain'])
    if p['active_study']:result['study_evidence']=p['studies'][p['active_study']].get('capture')
    if p['active_study']:
        study=p['studies'][p['active_study']]
        result['study_revision']=study.get('revision')
        result['study_uncertain']=study.get('uncertain',False)
        capture=study.get('capture');images=capture.get('images',[]) if capture else []
        result['study_preview_current']=study.get('capture_revision')==study.get('revision') and capture is not None and not study.get('uncertain',False)
        result.update(full_preview=images[0] if images else None,use_preview=images[1] if len(images)>1 else None,
                      preview_context='study',preview_revision=study.get('capture_revision'),preview_current=result['study_preview_current'],
                      active_task={'task_id':p['active_study'],'goal':study.get('plan',{}).get('purpose'),
                                   'checks':study.get('checks',[]),'context':'study'},relevant_object_ids={},mapping_current=False,detail_images=[])
    result['studies']={i:{k:v for k,v in study.items() if k in ('layout_id','outcome','native','images','layout_sha256')} for i,study in p['studies'].items()}
    graph=w.data('entity_graph') or {'entities':[],'relations':[]}
    task=result.get('active_task') or {};scope=set(task.get('entities',[]))
    if not scope and full(w) and s['focused']['queue']:scope=set(s['focused']['queue'][0].get('entities',[]))
    entities={e['id']:e for e in graph['entities'] if e['spec_id'] in scope}
    applicable=[r for r in graph['relations'] if {r['a'],r['b']} & set(entities)]
    touched={e for r in applicable for e in (r['a'],r['b'])}|set(entities)
    result['graph_entities']=[{**e,'native_ids':p['mapping'].get(e['id'],[])} for e in graph['entities'] if e['id'] in touched]
    result['applicable_relationships']=[{**r,'check':p['relations'].get(r['id'])} for r in applicable]
    result['relationship_summary']={'declared':len(graph['relations']),'unresolved_or_stale':sum(not p['relations'].get(r['id'],{}).get('current') or p['relations'][r['id']]['outcome']=='fail' for r in graph['relations'])}
    result.setdefault('references',{})
    if w.latest('entity_graph'):result['references']['entity_graph']=str(w.run/w.latest('entity_graph')['artifact']['path'])
    result['global_style']=(w.data('design_brief') or {}).get('style')
    if p['active_study']:
        study=p['studies'][p['active_study']]
        if study.get('uncertain'):result['next_action']='Inspect isolated study recovery in a fresh connection; never replay uncertain edits'
        elif not study.get('batch_pending',True):result['next_action']='Plan the next study correction/batch; close only on its accepted or abandoned confirmation'
        elif study.get('capture') and result['study_preview_current']:result['next_action']='Inspect the current study full/use images, then confirm or revise its checks'
        else:result['next_action']='Execute the current study task, then capture current full/use images'
    elif not w.latest('design_brief'):result['next_action']='Record audience/message/use requirements and shared style'
    elif not w.latest('layout'):result['next_action']='Record research/calibration and three meaningful layouts'
    elif not w.latest('directions'):result['next_action']='Build, inspect and record all three native blockouts, then directions'
    elif not p['started']:result['next_action']='Complete independent concept selection/target/spec, then explicit assembly start'
    elif full(w) and not w.latest('entity_graph'):result['next_action']='Declare meaningful entities, spatial relationships and construction dependencies'
    elif full(w) and s['status']=='active' and len(s['completed_stages'])==4 and not s['focused']['queue'] and result['relationship_summary']['unresolved_or_stale']:
        result['next_action']='Inspect current full/use/target and record relation_check before preflight'
    elif not full(w):result['next_action']='Follow designer production stages and independent review'
    return result
