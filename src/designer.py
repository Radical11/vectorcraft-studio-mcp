"""Designer-v1 policy for new v3 runs. Judgments remain agent-observed evidence."""
from pathlib import Path
from workflow import nonempty,digest,read,nodes_from_native,atomic,now

GENRES=('expressive-poster','editorial-illustration','information-graphic')
COPY_KEYS=('specificity','clarity','tone','illustration_relationship','subject_substitution')
def enabled(w):return bool(w.state and w.state.get('quality_profile') in ('designer-v1','focused-execution-v1','layout-blockout-v1','designer-process-v1') and w.state['mode']=='full')
def inspection(w,data,expected):
    obs=data.get('image_inspection',{})
    if obs.get('performed') is not True:raise ValueError('Actual image inspection required')
    for k in ('tool','evidence','observation'):nonempty(data.get('image_observation',{}).get(k),'image '+k)
    nonempty(obs.get('observations'),'visible observations') if isinstance(obs.get('observations'),str) else None
    if not obs.get('observations'):raise ValueError('Visible observations required')
    paths=[w.project_file(p) for p in obs.get('paths',[])]
    if any(not any(digest(p)==digest(e) for p in paths) for e in expected):raise ValueError('Inspect all supplied images')
def current(w,kind,key,source):
    record=w.latest(kind)
    return record and w.data(kind).get(key)==source['artifact']['sha256']
def concepts_ready(w):
    directions=w.latest('directions');calibration=w.latest('calibration');review=w.latest('concept_review')
    if not calibration or not directions or not review:raise ValueError('Designer mode needs calibration and independent concept review')
    previous_research=next((r for r in reversed(w.state['records'][:w.state['records'].index(calibration)]) if r['kind']=='research'),None)
    if not previous_research or previous_research['artifact']['sha256']!=w.latest('research')['artifact']['sha256']:raise ValueError('Stale calibration: research changed; recalibrate and review concepts')
    data=w.data('concept_review')
    if data['directions_sha256']!=directions['artifact']['sha256'] or data['calibration_sha256']!=calibration['artifact']['sha256']:raise ValueError('Stale concept review')
    if data['all_weak']:
        passes=sum(r['kind']=='directions' for r in w.state['records'])
        if passes<2:raise ValueError('All concepts weak: one additional exploration pass required')
        nonempty(data.get('unresolved_limitations'),'unresolved concept limitations')
    # The directions selection is provisional. Concept review records the host's final autonomous choice.
def validate_record(w,kind,data):
    attachments=[]
    if kind=='calibration':
        if w.state['revision']:raise ValueError('Calibration cannot be retrofitted after edits')
        if not w.latest('research'):raise ValueError('Research before calibration')
        if data.get('genre') not in GENRES:raise ValueError('Unknown design genre')
        refs=data.get('references',[])
        if not 3<=len(refs)<=5:raise ValueError('Three to five inspected calibration references required')
        urls={r['url'] for r in w.data('research')['references']}
        for ref in refs:
            if ref.get('research_url') not in urls:raise ValueError('Calibration must draw from attributed research')
            for k in ('observation','principle','application'):nonempty(ref.get(k),k)
            attachments.append(w.artifact(ref['image'],'calibration-reference'))
        inspection(w,data,[w.run/a['path'] for a in attachments])
    elif kind=='concept_review':
        if w.state['revision']:raise ValueError('Concept review must precede construction')
        directions=w.latest('directions');calibration=w.latest('calibration')
        if not directions or not calibration:raise ValueError('Calibration and developed alternatives before concept review')
        if data.get('directions_sha256')!=directions['artifact']['sha256'] or data.get('calibration_sha256')!=calibration['artifact']['sha256']:raise ValueError('Stale concept review')
        nonempty(data.get('reviewer_id'),'fresh independent reviewer id')
        if any(read(w.run/r['artifact']['path']).get('reviewer_id')==data['reviewer_id'] for r in w.state['records'] if r['kind']=='concept_review'):raise ValueError('Concept reviewer must be fresh')
        expected=[w.run/a['path'] for r in (directions,calibration) for a in r['attachments'] if a['role'] in ('thumbnail','calibration-reference')]
        import design_process
        inspection(w,data,expected+design_process.concept_images(w))
        ids={d['id'] for d in w.data('directions')['directions']}
        assessments=data.get('assessments',[])
        if {a.get('id') for a in assessments}!=ids or len(assessments)!=3:raise ValueError('Assess all three directions')
        for a in assessments:
            for k in ('composition','image_treatment','copy','brief_fit'):nonempty(a.get(k),k)
        if data.get('selected') not in ids or type(data.get('all_weak'))!=bool:raise ValueError('Selection and all_weak verdict required')
        nonempty(data.get('reason'),'selection reason')
    elif kind=='construction_study':
        spec=w.latest('spec')
        if not spec or data.get('spec_sha256')!=spec['artifact']['sha256']:raise ValueError('Study must match current specification')
        if data.get('method') not in ('native','trace-rebuild'):raise ValueError('Unknown construction method')
        if data.get('method')!=w.data('spec')['construction_method']:raise ValueError('Study method differs from specification')
        native=w.project_file(data['native']);nodes=nodes_from_native(native)
        if not data.get('element_map') or any(str(i) not in nodes for ids in data['element_map'].values() for i in ids):raise ValueError('Study components must map to real native objects')
        images=data.get('images',[])
        if len(images)!=2:raise ValueError('Full/use-size study images required')
        inspection(w,data,[w.project_file(p) for p in images])
        for k in ('silhouette','spacing','proportions','gesture','contours','detail'):nonempty(data.get('checks',{}).get(k),k)
        if data.get('confirmed') is not True:raise ValueError('Construction study needs observed confirmation')
        if not isinstance(data.get('limitations'),list):raise ValueError('Study limitations required, may be empty')
        attachments=[w.artifact(native,'study-native'),*[w.artifact(p,'study-image') for p in images]]
    return attachments
def validate_directions(w,data):
    if not w.latest('calibration'):raise ValueError('Calibration before developed directions')
    if sum(r['kind']=='directions' for r in w.state['records'])>=2:raise ValueError('Two exploration passes exhausted')
    for d in data.get('directions',[]):
        for k in ('composition','image_treatment','actual_copy'):nonempty(d.get(k),k)
        for k in COPY_KEYS:nonempty(d.get('copy_evaluation',{}).get(k),'copy '+k)
def validate_spec(data):
    if data.get('construction_method') not in ('native','trace-rebuild'):raise ValueError('Choose native or trace-rebuild construction')
    for k in COPY_KEYS:nonempty(data.get('copy_evaluation',{}).get(k),'copy '+k)
def require_study(w):
    record=w.latest('construction_study')
    if not current(w,'construction_study','spec_sha256',w.latest('spec')) or record['spec_revision']!=w.state['spec_revision']:raise ValueError('Confirmed current construction study before imagery')

def review(w,data):
    s=w.state;version=data['version'];items=data.get('reviews',[])
    if len(items)!=2 or {i.get('role') for i in items}!={'communication','craft'}:raise ValueError('Separate communication and craft reviewers required')
    if len({i.get('reviewer_id') for i in items})!=2 or not all(i.get('reviewer_id') for i in items):raise ValueError('Fresh distinct reviewer identities required')
    if version not in s['ready_versions'] or any(r['version']==version for r in s['reviews']):raise ValueError('Stale, missing or already reviewed preflight')
    packet=next((p for p in reversed(s.get('packets',[])) if p['version']==version),None)
    incumbent=s['best_version'] or s.get('original_version');original=s.get('original_version')
    if not packet or packet['incumbent']!=incumbent:raise ValueError('Neutral current comparison packet required')
    versions=list(dict.fromkeys(v for v in (version,incumbent,original) if v))
    images=[w.run/a['path'] for v in versions for a in s['versions'][v]['images']]
    passes=[];votes=[];baselines={};baseline_sources={};regressions=[]
    previous_ids={i.get('reviewer_id') for r in s['reviews'] for i in read(w.run/r['artifact']['path']).get('reviews',[])}
    previous_ids.update(w.data('concept_review').get('reviewer_id') for _ in [0] if w.latest('concept_review'))
    if any(i['reviewer_id'] in previous_ids for i in items):raise ValueError('Reviewer identities must be fresh for this round')
    for item in items:
        inspection(w,{'image_inspection':item['review'].get('image_inspection',{}),'image_observation':item.get('image_observation',{})},[*images,w.run/w.latest('target')['attachments'][0]['path']])
        passes.append(w.validate_review(item['review'],images))
        verdict=item['review'].get('brief_comparison',{})
        winner=verdict.get('winner');nonempty(verdict.get('reason'),'common-brief reason')
        regression=verdict.get('regression')
        if s.get('review_contract')=='observed-comparison-v1' and regression is None:raise ValueError('Explicit observed regression verdict required')
        if regression is not None:
            if type(regression.get('present'))!=bool:raise ValueError('Regression needs an observed boolean verdict')
            nonempty(regression.get('evidence'),'regression evidence')
            regressions.append(regression['present'])
        if winner not in ('candidate','incumbent','original','equal','no_baseline'):raise ValueError('Common-brief verdict required')
        if winner in ('incumbent','equal') and not incumbent or winner=='original' and not original or winner=='no_baseline' and incumbent:raise ValueError('Verdict names unavailable baseline')
        votes.append(version if winner in ('candidate','no_baseline') else original if winner=='original' else incumbent)
        for role,v in (('incumbent_assessment',incumbent),('original_assessment',original)):
            if v and not any(r['version']==v for r in s['reviews']):
                assessment=item['review'].get(role) or (item['review'].get('incumbent_assessment') if v==incumbent else None)
                if not assessment:raise ValueError('Both reviewers must assess previously unreviewed baseline')
                okay=w.validate_review(assessment,[w.run/a['path'] for a in s['versions'][v]['images']],False)
                baselines.setdefault(v,[]).append(okay)
                baseline_sources.setdefault(v,{})[item['role']]={'role':item['role'],'reviewer_id':item['reviewer_id'],'review':assessment}
    chosen=votes[0] if votes[0]==votes[1] else incumbent
    if chosen is None:chosen=version
    accepted=chosen==version
    # Fresh reviewers may calibrate scores differently. Common-brief votes decide strength;
    # only an explicitly observed consequential regression overrides their agreed winner.
    # Missing fields on earlier designer records retain compatibility, not invented evidence.
    if accepted and incumbent and any(regressions):chosen=incumbent;accepted=False
    p=w.run/'designer-review-input.json';atomic(p,data)
    s['reviews'].append({'version':version,'artifact':w.artifact(p,'specialist-reviews'),'passed':all(passes),'accepted_as_best':accepted,'at':now()})
    for v,checks in baselines.items():
        if not any(r['version']==v for r in s['reviews']):
            atomic(p,{'reviews':list(baseline_sources[v].values())})
            s['reviews'].append({'version':v,'artifact':w.artifact(p,'baseline-reviews'),'passed':all(checks),'accepted_as_best':chosen==v,'at':now()})
    first=s['best_version'] is None;s['best_version']=chosen
    if not first:s['revision_rounds']+=1;s['no_improvement_streak']=0 if accepted else s['no_improvement_streak']+1
    best=next(r for r in reversed(s['reviews']) if r['version']==chosen)
    if best['passed']:s.update(status='review_passed',stop_reason='Best common-brief version passed both independent specialists')
    elif s['no_improvement_streak']>=2:s.update(status='stalled',stop_reason='Two non-improving corrections; preserve best')
    elif s['revision_rounds']>=3:s.update(status='budget_exhausted',stop_reason='Three correction rounds used')
    w.persist();return w.response()
