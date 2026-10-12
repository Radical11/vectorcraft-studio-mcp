"""Behavioral fixtures: test enforcement and integrity, not real aesthetic or viewing claims."""
import copy
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from workflow import Workflow,atomic,read,nodes_from_native
from vectorcraft_gateway import Gateway,text_result
FIX=ROOT/'tests/fixtures/legacy-poster'

class Backend:
    def __init__(self):
        self.native=read(FIX/'finishing.vectorcraft');self.inspect=read(FIX/'finishing-inspection.json');self.fonts=[{'status':'exact','missingGlyphs':[]}];self.overflow=False
    def checked_call(self,name,args):
        if name=='export':atomic(args['path'],self.native);return text_result({})
        if name=='screenshot':shutil.copy2(FIX/'finishing-use.png',args['path']);return text_result({})
        if name=='doc_inspect':return text_result(self.inspect)
        if name=='open_file':self.native=read(args['path']);return text_result({})
        if name=='command_run':
            if args['id']=='text.fonts':return text_result(self.fonts)
            if args['id']=='text.areaOptions':return text_result({'overflow':self.overflow,'fitScale':1})
        raise ValueError('Unsupported fixture tool '+name)

class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name);self.backend=Backend();self.w=Workflow(self.root)
        (self.root/'brief.md').write_text('Behavioral fixture, not a real image inspection claim.',encoding='utf-8')
        for i in range(3):shutil.copy2(FIX/('thumb-'+str(i+1)+'.png'),self.root/('thumb'+str(i)+'.png'))
        shutil.copy2(FIX/'finishing-full.png',self.root/'target.png')
        self.w.start(self.backend,brief_path=str(self.root/'brief.md'),run_id='test',quality_profile='legacy-v3')
    def tearDown(self):self.temp.cleanup()
    def ready(self):
        r=read(FIX/'research.json');r['gaps'].append('Reused historical fixture evidence; no live source inspection performed by unit tests.')
        self.w.record(self.backend,'research',r)
        ds={'directions':[{'id':str(i),'concept':'Fixture '+str(i),'metaphor':'Fixture','visual_language':'Fixture','thumbnail':str(self.root/('thumb'+str(i)+'.png')),'copy_options':[]} for i in range(3)],'selected':'0','selection_reason':'Fixture'}
        self.w.record(self.backend,'directions',ds)
        self.w.record(self.backend,'target',{'path':str(self.root/'target.png'),'method':'vector-study','observation':'Fixture assertion only','features':['Fixture silhouette']})
        self.spec={'canvas':{'width':900,'height':1200,'use_width':450},'locked_copy':['AFTER THE'], 'palette':['#101C2D'],
          'reading_sequence':['title'],'focal_silhouette':'Fixture harp','copy_rationale':'Fixture supplied text',
          'elements':[{'id':'title','kind':'text','stage':'typography','box':[66,40,760,110],'text':'AFTER THE','font':'Georgia','size':110}]}
        self.w.record(self.backend,'spec',self.spec)
    def begin(self,stage):self.w.begin(stage,{k:'Fixture' for k in ('purpose','changes','checks','expected_result')})
    def confirm(self,v):
        self.w.checkpoint(self.backend,v,{'phase':'confirm','observations':'Fixture image assertion only','decision':'Fixture proceed',
           'target_comparison':{k:'Fixture observed' for k in ('silhouette','proportions','negative_space','hierarchy','copy','detail')},'element_map':{'title':[4]}})
    def complete(self):
        self.ready()
        for stage in ('composition','typography','imagery','finishing'):
            self.begin(stage);self.w.checkpoint(self.backend,stage,{'phase':'capture'});self.confirm(stage)
        (self.root/'out.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg"><text>AFTER THE</text></svg>')
        (self.root/'out.pdf').write_bytes(b'%PDF-fixture');shutil.copy2(FIX/'finishing-use.png',self.root/'out.png')
        files=[str(self.root/('out.'+f)) for f in ('svg','pdf','png')]
        for f in files:self.w.note_export(f)
        return {'version':'finishing','files':files,'observations':'Fixture export assertion'}
    def review_data(self,version='finishing',score=4,winner='candidate'):
        s=self.w.state;images=[str(self.w.run/a['path']) for v in (version,'original') for a in s['versions'][v]['images']]
        images.append(str(self.w.run/self.w.latest('target')['attachments'][0]['path']))
        r={'image_inspection':{'performed':True,'paths':images,'observations':['Fixture only']},'scores':{k:{'score':score,'reason':'Fixture'} for k in ('brief','composition','alignment','typography','color','style','distinctiveness','craft')},
          'visual_fidelity':{'score':score,'reason':'Fixture'},'copy_assessment':{'score':score,'reason':'Fixture'},'findings':[],
          'comparison':{'winner':winner,'reason':'Fixture'},'summary':'Fixture'}
        old=copy.deepcopy(r);old['comparison']['winner']='no_baseline';old['scores']['distinctiveness']['score']=3
        r['incumbent_assessment']=old
        return {'version':version,'review':r,'image_observation':{'tool':'fixture','evidence':'No real reviewer in unit tests','observation':'Fixture'}}
    def test_full_blocks_unplanned_edits(self):
        with self.assertRaises(ValueError):self.w.guard_edit()
        self.ready()
        with self.assertRaises(ValueError):self.w.guard_edit()
        self.begin('composition');self.w.guard_edit()
    def test_quick_needs_scope_and_has_no_research(self):
        w=Workflow(self.root)
        with self.assertRaises(ValueError):w.start(self.backend,mode='quick')
        w.start(self.backend,mode='quick',scope='Change title color',run_id='quick');w.guard_edit()
        self.assertEqual(w.state['records'],[])
    def test_stages_cannot_be_skipped(self):
        self.ready()
        with self.assertRaises(ValueError):self.begin('imagery')
    def test_capture_is_not_inspection(self):
        self.ready();self.begin('composition');self.w.checkpoint(self.backend,'c',{'phase':'capture'})
        with self.assertRaises(ValueError):self.w.guard_edit()
        with self.assertRaises(ValueError):self.w.begin('typography',{})
        self.confirm('c');self.assertIn('composition',self.w.state['completed_stages'])
    def test_external_document_change_rejects_checkpoint(self):
        self.ready();self.begin('composition');self.w.checkpoint(self.backend,'c',{'phase':'capture'})
        self.backend.native['document']['title']='changed elsewhere'
        with self.assertRaisesRegex(ValueError,'outside'):self.confirm('c')
    def test_missing_object_mapping_rejected(self):
        self.ready();self.begin('composition');self.w.checkpoint(self.backend,'c',{'phase':'capture'});self.confirm('c')
        self.begin('typography');self.w.checkpoint(self.backend,'t',{'phase':'capture'})
        data={'phase':'confirm','observations':'Fixture','decision':'proceed','element_map':{'title':[9999]},'target_comparison':{k:'Fixture' for k in ('silhouette','proportions','negative_space','hierarchy','copy','detail')}}
        with self.assertRaisesRegex(ValueError,'Missing'):self.w.checkpoint(self.backend,'t',data)
    def test_locked_copy_cannot_change(self):
        self.ready();s=copy.deepcopy(self.spec);s['elements'][0]['text']='GENERIC TITLE'
        with self.assertRaisesRegex(ValueError,'locked'):self.w.record(self.backend,'spec',s)
    def test_locked_copy_list_cannot_be_redefined(self):
        self.ready();s=copy.deepcopy(self.spec);s['locked_copy']=[];s['elements'][0]['text']='GENERIC TITLE'
        with self.assertRaisesRegex(ValueError,'locked_copy'):self.w.record(self.backend,'spec',s)
    def test_identical_thumbnails_rejected(self):
        self.ready();d=self.w.data('directions')
        for x in d['directions']:x['thumbnail']=str(self.root/'thumb0.png')
        with self.assertRaisesRegex(ValueError,'identical'):self.w.record(self.backend,'directions',d)
    def test_preflight_font_substitution(self):
        p=self.complete();self.backend.fonts=[{'status':'substitute'}]
        with self.assertRaisesRegex(ValueError,'font'):self.w.preflight(self.backend,p)
    def test_preflight_actual_copy(self):
        p=self.complete()
        def alter(n):
            if isinstance(n,dict):
                if n.get('id')==4:n['text']='wrong'
                for v in n.values():alter(v)
            elif isinstance(n,list):
                for v in n:alter(v)
        inspection=self.w.run/self.w.state['versions']['finishing']['inspection']['path'];d=read(inspection);alter(d);atomic(inspection,d)
        # Update fixture hash to exercise copy validation separately from integrity validation.
        from workflow import digest
        self.w.state['versions']['finishing']['inspection']['sha256']=digest(inspection)
        with self.assertRaisesRegex(ValueError,'copy|Locked'):self.w.preflight(self.backend,p)
    def test_svg_raster_rejected(self):
        p=self.complete();(self.root/'out.svg').write_text('<svg><image href="data:image/png;base64,eA=="/></svg>')
        self.w.note_export(self.root/'out.svg')
        with self.assertRaisesRegex(ValueError,'raster'):self.w.preflight(self.backend,p)
    def test_excessive_anchor_budget(self):
        self.ready();self.spec['anchor_budget']=1;self.w.record(self.backend,'spec',self.spec)
        for stage in ('composition','typography','imagery','finishing'):
            self.begin(stage);self.w.checkpoint(self.backend,stage,{'phase':'capture'});self.confirm(stage)
        (self.root/'out.svg').write_text('<svg/>')
        with self.assertRaisesRegex(ValueError,'anchors'):self.w.preflight(self.backend,{'version':'finishing','files':[str(self.root/'out.svg')],'observations':'Fixture'})
    def test_review_requires_preflight_and_packet(self):
        self.complete()
        with self.assertRaisesRegex(ValueError,'preflight'):self.w.review(self.review_data())
    def test_review_target_and_copy_can_block_pass(self):
        p=self.complete();self.w.preflight(self.backend,p);self.w.packet('finishing');d=self.review_data();d['review']['copy_assessment']['score']=3
        self.w.review(d);self.assertEqual(self.w.state['status'],'active')
    def test_review_missing_target_rejected(self):
        p=self.complete();self.w.preflight(self.backend,p);self.w.packet('finishing');d=self.review_data();d['review']['image_inspection']['paths'].pop()
        with self.assertRaisesRegex(ValueError,'target'):self.w.review(d)
    def test_amended_spec_invalidates_preflight(self):
        p=self.complete();self.w.preflight(self.backend,p);self.w.record(self.backend,'spec',self.spec)
        with self.assertRaises(ValueError):self.w.packet('finishing')
    def test_switching_document_midrun_blocked(self):
        self.ready();self.begin('composition')
        with self.assertRaises(ValueError):self.w.setup_allowed()
    def test_resume_restores_immutable_checkpoint(self):
        self.ready();self.begin('composition');self.w.checkpoint(self.backend,'c',{'phase':'capture'});self.confirm('c')
        w=Workflow(self.root);w.start(self.backend,resume=str(self.w.run));self.assertEqual(w.state['working_version'],'c')
    def test_tampered_evidence_rejected(self):
        self.ready();p=self.w.run/self.w.latest('target')['attachments'][0]['path'];p.write_bytes(b'wrong')
        with self.assertRaisesRegex(ValueError,'integrity'):self.w.status()
    def test_external_evidence_blocked(self):
        with self.assertRaisesRegex(ValueError,'project'):self.w.project_file(FIX/'finishing-full.png')
    def test_authoring_aliases_and_ui_are_classified(self):
        for name,args in [('run_command',{'command':'shape.rectangle'}),('command_run',{'id':'text.create'}),('type_text',{}),('pointer_gesture',{}),('draw_shape',{}),('invoke_menu',{'id':'edit.paste'})]:
            self.assertEqual(Gateway.operation(name,args),'edit')
        self.assertEqual(Gateway.operation('command_batch',{'steps':[{'id':'text.fontList'},{'id':'shape.rectangle'}]}),'edit')
        with self.assertRaises(ValueError):Gateway.operation('command_batch',{'steps':[{'id':'file.new'},{'id':'shape.rectangle'}]})
    def test_query_vs_setter(self):
        self.assertEqual(Gateway.operation('command_run',{'id':'text.areaOptions','params':{'ids':[4]}}),'read')
        self.assertEqual(Gateway.operation('command_run',{'id':'text.areaOptions','params':{'width':40}}),'edit')
        self.assertEqual(Gateway.operation('command_run',{'id':'imageTrace.setView'}),'edit')

    def test_stale_export_bytes_rejected(self):
        p=self.complete();(self.root/'out.png').write_bytes(b'changed')
        with self.assertRaisesRegex(ValueError,'Stale'):self.w.preflight(self.backend,p)
    def test_exports_from_previous_revision_rejected(self):
        p=self.complete();self.w.state['export_provenance'][str(self.root/'out.svg')]['revision']=-1
        with self.assertRaisesRegex(ValueError,'Stale'):self.w.preflight(self.backend,p)
    def test_render_records_revision_without_claiming_inspection(self):
        self.ready();self.w.note_render('screenshot',text_result({}),self.root/'target.png')
        r=self.w.state['renders'][-1];self.assertEqual(r['revision'],0);self.assertFalse(r['observed']);self.assertEqual(r['spec_revision'],2)
    def test_missing_export_format_rejected(self):
        p=self.complete();p['files']=p['files'][:1]
        with self.assertRaisesRegex(ValueError,'SVG, PDF and PNG'):self.w.preflight(self.backend,p)
    def test_partial_batch_requires_reconciliation(self):
        self.ready();self.begin('composition');self.w.edited('command_batch',{},text_result({'failed':1}))
        self.assertTrue(self.w.state['uncertain']);self.assertEqual(self.w.state['revision'],1)
        with self.assertRaisesRegex(ValueError,'uncertain'):self.w.guard_edit()
    def test_resume_original_before_first_edit(self):
        w=Workflow(self.root);w.start(self.backend,resume=str(self.w.run))
        self.assertFalse(w.state['uncertain']);self.assertEqual(w.state['events'][-1]['event'],'resume')
    def test_overflowing_area_copy_rejected(self):
        self.ready()
        def area(n):
            if isinstance(n,dict):
                if n.get('id')==4 and isinstance(n.get('kind'),dict):n['kind']['kind']={'kind':'area'}
                for v in n.values():area(v)
            elif isinstance(n,list):
                for v in n:area(v)
        area(self.backend.native);self.backend.overflow=True
        for stage in ('composition','typography','imagery','finishing'):
            self.begin(stage);self.w.checkpoint(self.backend,stage,{'phase':'capture'});self.confirm(stage)
        with self.assertRaisesRegex(ValueError,'overflow'):self.w.preflight(self.backend,{'version':'finishing','files':[],'observations':'Fixture'})
    def test_native_raster_rejected(self):
        self.ready();self.backend.native['document']['layers'].append({'id':999,'kind':{'type':'image'}})
        for stage in ('composition','typography','imagery','finishing'):
            self.begin(stage);self.w.checkpoint(self.backend,stage,{'phase':'capture'});self.confirm(stage)
        with self.assertRaisesRegex(ValueError,'Raster'):self.w.preflight(self.backend,{'version':'finishing','files':[],'observations':'Fixture'})
    def fixture_review_round(self,version,winner='candidate'):
        self.begin('finishing');self.w.checkpoint(self.backend,version,{'phase':'capture'});self.confirm(version)
        files=[str(self.root/('out.'+f)) for f in ('svg','pdf','png')]
        for f in files:self.w.note_export(f)
        self.w.preflight(self.backend,{'version':version,'files':files,'observations':'Fixture'})
        self.w.packet(version)
        incumbent=self.w.state['best_version'];d=self.review_data(version);d['review']['copy_assessment']['score']=3;d['review']['comparison']['winner']=winner
        d['review']['image_inspection']['paths']=[str(self.w.run/a['path']) for v in (version,incumbent) for a in self.w.state['versions'][v]['images']]+[str(self.w.run/self.w.latest('target')['attachments'][0]['path'])]
        self.w.review(d)
    def test_three_correction_round_budget(self):
        p=self.complete();self.w.preflight(self.backend,p);self.w.packet('finishing');d=self.review_data();d['review']['copy_assessment']['score']=3;self.w.review(d)
        for i in range(3):self.fixture_review_round('r'+str(i))
        self.assertEqual(self.w.state['status'],'budget_exhausted');self.assertEqual(self.w.state['revision_rounds'],3)
        with self.assertRaisesRegex(ValueError,'stopped'):self.w.guard_edit()
    def test_two_non_improving_rounds_retain_best(self):
        p=self.complete();self.w.preflight(self.backend,p);self.w.packet('finishing');d=self.review_data();d['review']['copy_assessment']['score']=3;self.w.review(d)
        self.fixture_review_round('r1','equal');self.fixture_review_round('r2','equal')
        self.assertEqual(self.w.state['status'],'stalled');self.assertEqual(self.w.state['best_version'],'finishing')
    def test_passed_run_reopen_requires_explicit_feedback_without_reset(self):
        p=self.complete();self.w.preflight(self.backend,p);self.w.packet('finishing');self.w.review(self.review_data())
        with self.assertRaisesRegex(ValueError,'reason'):Workflow(self.root).start(self.backend,resume=str(self.w.run))
        feedback=self.root/'feedback.json';atomic(feedback,{'finding':'Fixture: explain arrows'})
        w=Workflow(self.root);w.start(self.backend,resume=str(self.w.run),reopen_reason='New observed feedback',feedback_path=str(feedback))
        self.assertEqual(w.state['status'],'active');self.assertEqual(w.state['max_rounds'],3)
        self.assertEqual(w.state['revision_rounds'],0);self.assertEqual(w.state['best_version'],'finishing')
        self.assertEqual(w.state['ready_versions'],[])
    def test_exhausted_or_stalled_runs_cannot_reopen(self):
        feedback=self.root/'feedback.json';atomic(feedback,{'finding':'Fixture'})
        for status,rounds in [('budget_exhausted',3),('stalled',2),('review_passed',3)]:
            self.w.state.update(status=status,revision_rounds=rounds);self.w.persist()
            with self.assertRaisesRegex(ValueError,'extra revision budget'):
                Workflow(self.root).start(self.backend,resume=str(self.w.run),reopen_reason='Feedback',feedback_path=str(feedback))
    def test_foreign_target_does_not_penalize_original_intent(self):
        p=self.complete();review=self.review_data()['review'];review['visual_fidelity']={'score':None,'reason':'Original target unknown'}
        images=[self.w.run/a['path'] for a in self.w.state['versions']['finishing']['images']]
        self.assertTrue(self.w.validate_review(review,images,include_target=False))
        review['visual_fidelity']['score']=2
        self.assertTrue(self.w.validate_review(review,images,include_target=False))
        self.assertFalse(self.w.validate_review(review,images,include_target=True))
    def test_edit_invalidates_completed_review_readiness(self):
        p=self.complete();self.w.preflight(self.backend,p);self.begin('finishing');self.w.edited('add_text',{},text_result({'id':5}))
        self.assertEqual(self.w.state['ready_versions'],[])
        with self.assertRaisesRegex(ValueError,'Preflight'):self.w.packet('finishing')

if __name__=='__main__':unittest.main(verbosity=2)
