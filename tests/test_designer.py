"""Fixture policy checks, never actual calibration or reviewer image evidence."""
import copy,sys,unittest
from pathlib import Path
import test_workflow as legacy
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from workflow import Workflow,read
import designer
class DesignerTests(unittest.TestCase):
 def setUp(self):
  self.fixture=legacy.WorkflowTests('test_full_blocks_unplanned_edits');self.fixture.setUp();self.w=self.fixture.w;self.root=self.fixture.root;self.backend=self.fixture.backend
  self.fixture.ready();self.w.state['quality_profile']='designer-v1';self.w.persist()
  self.obs={'tool':'fixture','evidence':'Not actual tool evidence','observation':'Fixture only'}
 def tearDown(self):self.fixture.tearDown()
 def calibration(self):
  urls=[r['url'] for r in self.w.data('research')['references']]
  d={'genre':'expressive-poster','references':[{'research_url':urls[i%len(urls)],'image':str(self.root/f'thumb{i}.png'),'observation':'Fixture','principle':'Fixture','application':'Fixture'} for i in range(3)],'image_inspection':{'performed':True,'paths':[str(self.root/f'thumb{i}.png') for i in range(3)],'observations':['Fixture']},'image_observation':self.obs}
  self.w.record(self.backend,'calibration',d);return d
 def directions(self):
  d=self.w.data('directions')
  for item in d['directions']:
   item.update(composition='Fixture',image_treatment='Fixture',actual_copy='Fixture locked copy',copy_evaluation={k:'Fixture' for k in designer.COPY_KEYS})
  self.w.record(self.backend,'directions',d)
 def concept(self):
  d={'directions_sha256':self.w.latest('directions')['artifact']['sha256'],'calibration_sha256':self.w.latest('calibration')['artifact']['sha256'],'reviewer_id':'fixture-concept','assessments':[{'id':str(i),**{k:'Fixture' for k in ('composition','image_treatment','copy','brief_fit')}} for i in range(3)],'selected':'0','all_weak':False,'reason':'Fixture','image_inspection':{'performed':True,'paths':[str(self.root/f'thumb{i}.png') for i in range(3)],'observations':['Fixture']},'image_observation':self.obs}
  self.w.record(self.backend,'concept_review',d);return d
 def ready(self):
  self.calibration();self.directions();self.concept();self.fixture.spec.update(direction_id='0',construction_method='native',copy_evaluation={k:'Fixture' for k in designer.COPY_KEYS})
  target=self.w.data('target');target['direction_id']='0';self.w.record(self.backend,'target',target);self.w.record(self.backend,'spec',self.fixture.spec)
 def study(self):
  images=[str(self.root/f'thumb{i}.png') for i in range(2)]
  d={'spec_sha256':self.w.latest('spec')['artifact']['sha256'],'method':'native','native':str(legacy.FIX/'finishing.vectorcraft'),'element_map':{'component':[4]},'images':images,'checks':{k:'Fixture' for k in ('silhouette','spacing','proportions','gesture','contours','detail')},'confirmed':True,'limitations':[],'image_inspection':{'performed':True,'paths':images,'observations':['Fixture']},'image_observation':self.obs}
  import shutil
  shutil.copy2(d['native'],self.root/'study.vectorcraft');d['native']=str(self.root/'study.vectorcraft');self.w.record(self.backend,'construction_study',d);return d
 def test_new_full_defaults_designer(self):
  w=Workflow(self.root);w.start(self.backend,brief_path=str(self.root/'brief.md'),run_id='new');self.assertEqual(w.state['quality_profile'],'designer-v1')
 def test_missing_field_resume_remains_legacy(self):
  self.w.state.pop('quality_profile');self.w.persist();w=Workflow(self.root);w.start(self.backend,resume=str(self.w.run));self.assertFalse(designer.enabled(w))
 def test_concept_prerequisites(self):
  with self.assertRaisesRegex(ValueError,'calibration'):self.w.record(self.backend,'target',self.w.data('target'))
 def test_calibration_requires_actual_inspection_contract(self):
  d=self.calibration();d['image_inspection']['performed']=False
  with self.assertRaisesRegex(ValueError,'inspection'):self.w.record(self.backend,'calibration',d)
 def test_calibration_source_attribution(self):
  d=self.calibration();d['references'][0]['research_url']='invented'
  with self.assertRaisesRegex(ValueError,'attributed'):self.w.record(self.backend,'calibration',d)
 def test_developed_directions_need_copy_check(self):
  self.calibration()
  with self.assertRaisesRegex(ValueError,'composition'):self.w.record(self.backend,'directions',self.w.data('directions'))
 def test_stale_concept_rejected(self):
  self.calibration();self.directions();d=self.concept();d['directions_sha256']='stale'
  with self.assertRaisesRegex(ValueError,'Stale'):self.w.record(self.backend,'concept_review',d)
 def test_stale_calibration_after_research_change(self):
  self.ready();data=self.w.data('research');data['synthesis']='Updated factual synthesis requires calibration refresh';self.w.record(self.backend,'research',data)
  with self.assertRaisesRegex(ValueError,'Stale calibration'):designer.concepts_ready(self.w)
 def test_target_must_follow_independently_selected_direction(self):
  self.ready();data=self.w.data('target');data['direction_id']='2'
  with self.assertRaisesRegex(ValueError,'selected direction'):self.w.record(self.backend,'target',data)
 def test_spec_must_follow_target_direction(self):
  self.ready();data=copy.deepcopy(self.fixture.spec);data['direction_id']='2'
  with self.assertRaisesRegex(ValueError,'target direction'):self.w.record(self.backend,'spec',data)
 def test_all_weak_requires_second_pass_and_disclosure(self):
  self.calibration();self.directions();d=self.concept();d.update(all_weak=True,reviewer_id='weak-fixture-fresh');self.w.record(self.backend,'concept_review',d)
  # Existing fixture direction record counts as first pass; the developed record is second.
  with self.assertRaisesRegex(ValueError,'limitations'):designer.concepts_ready(self.w)
 def test_missing_study(self):
  self.ready();self.w.state['completed_stages']=['composition','typography']
  with self.assertRaisesRegex(ValueError,'study'):self.fixture.begin('imagery')
 def test_stale_study_after_spec_amendment(self):
  self.ready();self.study();self.w.record(self.backend,'spec',self.fixture.spec)
  with self.assertRaisesRegex(ValueError,'study'):designer.require_study(self.w)
 def test_real_study_object_mapping_required(self):
  self.ready();d=self.study();d['element_map']={'lost':[999999]}
  with self.assertRaisesRegex(ValueError,'real native'):self.w.record(self.backend,'construction_study',d)
 def test_single_reviewer_rejected(self):
  self.ready()
  with self.assertRaisesRegex(ValueError,'Separate'):designer.review(self.w,{'version':'unused','reviews':[]})
 def complete(self):
  import shutil
  self.ready();self.study()
  for stage in ('composition','typography','imagery','finishing'):
   self.fixture.begin(stage);self.w.checkpoint(self.backend,stage,{'phase':'capture'});self.fixture.confirm(stage)
  (self.root/'out.svg').write_text('<svg><text>AFTER THE</text></svg>');(self.root/'out.pdf').write_bytes(b'%PDF-fixture');shutil.copy2(self.root/'target.png',self.root/'out.png')
  self.exports=[str(self.root/('out.'+f)) for f in ('svg','pdf','png')]
  for f in self.exports:self.w.note_export(f)
  self.w.preflight(self.backend,{'version':'finishing','files':self.exports,'observations':'Fixture'});self.w.packet('finishing')
 def review_data(self,version='finishing',winner='candidate',suffix='first'):
  r=self.fixture.review_data(version)['review'];r['incumbent_assessment']['scores']['distinctiveness']['score']=4
  r['brief_comparison']={'winner':winner,'reason':'Fixture common brief'}
  return {'version':version,'reviews':[{'role':role,'reviewer_id':role+suffix,'review':copy.deepcopy(r),'image_observation':self.obs} for role in ('communication','craft')]}
 def test_both_specialists_can_retain_original(self):
  self.complete();designer.review(self.w,self.review_data(winner='original'))
  self.assertEqual(self.w.state['best_version'],'original');self.assertEqual(self.w.state['status'],'review_passed')
 def test_disagreement_retains_incumbent(self):
  self.complete();d=self.review_data();d['reviews'][1]['review']['brief_comparison']['winner']='incumbent';designer.review(self.w,d)
  self.assertEqual(self.w.state['best_version'],'original')
 def test_production_regression_retains_original(self):
  self.complete();d=self.review_data();d['reviews'][1]['review']['scores']['craft']['score']=3;d['reviews'][1]['review']['brief_comparison']['regression']={'present':True,'evidence':'Fixture: required text was clipped in candidate but intact in original'};designer.review(self.w,d)
  self.assertEqual(self.w.state['best_version'],'original')
 def test_score_change_alone_does_not_override_common_brief_winner(self):
  self.complete();d=self.review_data();d['reviews'][1]['review']['scores']['craft']['score']=3;designer.review(self.w,d)
  self.assertEqual(self.w.state['best_version'],'finishing');self.assertEqual(self.w.state['status'],'active')
 def test_regression_verdict_requires_visible_evidence(self):
  self.complete();d=self.review_data();d['reviews'][1]['review']['brief_comparison']['regression']={'present':True,'evidence':''}
  with self.assertRaisesRegex(ValueError,'regression evidence'):designer.review(self.w,d)
 def test_new_comparison_contract_requires_regression_judgment(self):
  self.complete();self.w.state['review_contract']='observed-comparison-v1'
  with self.assertRaisesRegex(ValueError,'regression verdict'):designer.review(self.w,self.review_data())
 def test_duplicate_specialists_rejected(self):
  self.complete();d=self.review_data();d['reviews'][1]['reviewer_id']=d['reviews'][0]['reviewer_id']
  with self.assertRaisesRegex(ValueError,'distinct'):designer.review(self.w,d)
 def test_three_way_packet_and_original_selection(self):
  self.complete();designer.review(self.w,self.review_data());self.w.state.update(status='active',stop_reason=None);self.w.persist()
  self.fixture.begin('finishing');self.w.checkpoint(self.backend,'r1',{'phase':'capture'});self.fixture.confirm('r1')
  for f in self.exports:self.w.note_export(f)
  self.w.preflight(self.backend,{'version':'r1','files':self.exports,'observations':'Fixture'});packet=self.w.packet('r1');self.assertIn('C',packet['images'])
  d=self.review_data('r1','original','second')
  for item in d['reviews']:
   item['review']['image_inspection']['paths']=[str(self.w.run/a['path']) for v in ('r1','finishing','original') for a in self.w.state['versions'][v]['images']]+[str(self.w.run/self.w.latest('target')['attachments'][0]['path'])]
  designer.review(self.w,d);self.assertEqual(self.w.state['best_version'],'original');self.assertEqual(self.w.state['revision_rounds'],1)
if __name__=='__main__':unittest.main()
