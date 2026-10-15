"""Process contract fixtures. Observations here are synthetic, never artwork evidence."""
import copy,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
import test_designer as fixtures
import design_process as process
from workflow import Workflow,tool_definitions,nodes_from_native,read,atomic

class ProcessTests(unittest.TestCase):
 def setUp(self):
  self.fixture=fixtures.DesignerTests('test_missing_study');self.fixture.setUp();self.fixture.ready()
  self.w,self.backend,self.root=self.fixture.w,self.fixture.backend,self.fixture.root
  self.w.state['quality_profile']='layout-blockout-v1';process.initialize(self.w);self.w.persist()
  self.brief={k:'Synthetic fixture' for k in ('audience','message','response','viewing_context','medium','production_requirements','style')}
  self.brief.update(assumptions=[],locked_copy=[])
  self.layouts={'alternatives':[{'id':str(i),'concept':'Fixture '+str(i),'reading_order':'Fixture','negative_space':'Fixture','copy':[], 'bounds':{'focal':[0,0,.5,.5]}} for i in range(3)]}
 def tearDown(self):self.fixture.tearDown()
 def foundations(self):
  self.w.record(self.backend,'design_brief',self.brief);self.w.record(self.backend,'layout',self.layouts)
 def graph(self):
  return {'entities':[{'id':'label','spec_id':'title','role':'Fixture text','anchors':{'middle':[.5,.5]}}, {'id':'partner','spec_id':'title','role':'Fixture neighbor','anchors':{'middle':[.5,.5]}}],
          'relations':[{'id':'relation','a':'label','b':'partner','kind':'contact'}],'dependencies':[['label','partner']]}
 def test_profile_catalog_and_default(self):
  d={t['name']:t for t in tool_definitions()};self.assertEqual(len(d),5)
  self.assertEqual(d['workflow_start']['inputSchema']['properties']['quality_profile']['default'],'designer-v1')
  for profile in process.PROFILES:self.assertIn(profile,d['workflow_start']['inputSchema']['properties']['quality_profile']['enum'])
 def test_quick_process_denied(self):
  for profile in process.PROFILES:
   with self.assertRaisesRegex(ValueError,'full mode'):Workflow(self.root).start(self.backend,mode='quick',scope='fixture',quality_profile=profile)
 def test_old_profile_rejects_new_records(self):
  self.w.state['quality_profile']='designer-v1'
  with self.assertRaisesRegex(ValueError,'experimental'):self.w.record(self.backend,'design_brief',self.brief)
 def test_brief_required_fields(self):
  self.brief.pop('message')
  with self.assertRaisesRegex(ValueError,'message'):self.w.record(self.backend,'design_brief',self.brief)
 def test_three_layouts(self):
  self.w.record(self.backend,'design_brief',self.brief);self.layouts['alternatives'].pop()
  with self.assertRaisesRegex(ValueError,'Three'):self.w.record(self.backend,'layout',self.layouts)
 def test_layout_bounds(self):
  self.w.record(self.backend,'design_brief',self.brief);self.layouts['alternatives'][0]['bounds']['focal']=[.8,0,.5,.5]
  with self.assertRaisesRegex(ValueError,'bounds'):self.w.record(self.backend,'layout',self.layouts)
 def test_locked_copy(self):
  self.brief['locked_copy']=['Exact'];self.w.record(self.backend,'design_brief',self.brief)
  with self.assertRaisesRegex(ValueError,'locked copy'):self.w.record(self.backend,'layout',self.layouts)
 def test_studies_not_production_acceptance(self):
  self.foundations()
  with self.assertRaisesRegex(ValueError,'transition'):process.guard_begin(self.w)
  self.assertEqual(self.w.state['completed_stages'],[])
 def test_directions_require_observed_studies(self):
  self.foundations()
  with self.assertRaisesRegex(ValueError,'blockouts'):process.guard_directions(self.w)
 def observed_studies(self):
  self.foundations();p=process.state(self.w)
  for i in range(3):
   p['studies'][str(i)]={'outcome':'pass','closed':True,'layout_id':str(i),'layout_sha256':self.w.latest('layout')['artifact']['sha256'],
      'native':self.w.state['versions']['original']['native'],'images':[self.w.artifact(self.root/f'thumb{i}.png','fixture-image')],'observation':'Synthetic'}
   self.w.record(self.backend,'blockout',{'study_id':str(i)})
  native=self.w.run/self.w.state['versions']['original']['native']['path']
  text='\n'.join(''.join(run.get('text','') for run in n['kind'].get('runs',[])) for n in nodes_from_native(native).values() if n['kind'].get('type')=='text')
  return {'directions':[{'id':str(i),'thumbnail':str(self.root/f'thumb{i}.png'),'actual_copy':text} for i in range(3)]}
 def test_directions_match_layout_ids(self):
  data=self.observed_studies();data['directions'][0]['id']='unrelated'
  with self.assertRaisesRegex(ValueError,'IDs'):process.guard_directions(self.w,data)
 def test_direction_thumbnail_bound_to_matching_blockout(self):
  data=self.observed_studies();process.guard_directions(self.w,data)
  data['directions'][0]['thumbnail']=data['directions'][1]['thumbnail']
  with self.assertRaisesRegex(ValueError,'thumbnail'):process.guard_directions(self.w,data)
 def test_direction_copy_covers_actual_native_text(self):
  data=self.observed_studies();data['directions'][0]['actual_copy']='Intended fixture copy missing the native words'
  with self.assertRaisesRegex(ValueError,'live text'):process.guard_directions(self.w,data)
 def test_direction_copy_type_error_is_actionable(self):
  data=self.observed_studies();data['directions'][0]['actual_copy']=['Wrong type']
  with self.assertRaisesRegex(ValueError,'actual_copy'):process.guard_directions(self.w,data)
 def test_optional_unregistered_study_does_not_replace_direction_evidence(self):
  data=self.observed_studies();p=process.state(self.w)
  extra=copy.deepcopy(p['studies']['0']);extra['images']=p['studies']['1']['images'];p['studies']['optional']=extra
  process.guard_directions(self.w,data)
 def test_malformed_research_fact_has_actionable_v3_error(self):
  data=self.w.data('research');data['facts']=['A malformed fixture claim']
  with self.assertRaisesRegex(ValueError,'claim, source_url'):self.w.record(self.backend,'research',data)
 def test_concept_requires_use_images_for_experimental_profile(self):
  self.foundations();p=process.state(self.w)
  for i in range(3):
   native=self.w.state['versions']['original']['native']
   p['studies'][str(i)]={'outcome':'pass','closed':True,'layout_id':str(i),'layout_sha256':self.w.latest('layout')['artifact']['sha256'],'native':native,
                       'images':[self.w.artifact(self.root/f'thumb{i}.png','fixture-image'),self.w.artifact(self.root/'target.png','fixture-use')],'observation':'Synthetic'}
   self.w.record(self.backend,'blockout',{'study_id':str(i)})
  data=copy.deepcopy(self.w.data('concept_review'));data['reviewer_id']='fresh-fixture-use-check'
  with self.assertRaisesRegex(ValueError,'all supplied images'):self.w.record(self.backend,'concept_review',data)
  data['image_inspection']['paths'].append(str(self.root/'target.png'))
  self.w.record(self.backend,'concept_review',data)
 def test_missing_blockout(self):
  with self.assertRaisesRegex(ValueError,'passed native'):self.w.record(self.backend,'blockout',{'study_id':'missing'})
 def test_active_study_blocks_records(self):
  process.state(self.w)['active_study']='fixture'
  with self.assertRaisesRegex(ValueError,'Close'):self.w.record(self.backend,'design_brief',self.brief)
 def test_graph_reserved_full_process(self):
  process.state(self.w)['started']=True
  with self.assertRaisesRegex(ValueError,'designer-process-v1'):self.w.record(self.backend,'entity_graph',self.graph())
 def test_acyclic_dependencies(self):
  g=self.graph();g['dependencies'].append(['partner','label'])
  with self.assertRaisesRegex(ValueError,'acyclic'):process.validate_graph(self.w,g)
 def test_acyclic_parents(self):
  g=self.graph();g['entities'][0]['parent']='partner';g['entities'][1]['parent']='label'
  with self.assertRaisesRegex(ValueError,'acyclic'):process.validate_graph(self.w,g)
 def test_spatial_cycles_allowed(self):
  g=self.graph();g['relations'].append({'id':'return','a':'partner','b':'label','kind':'association'});process.validate_graph(self.w,g)
 def test_unknown_endpoint(self):
  g=self.graph();g['relations'][0]['b']='unknown'
  with self.assertRaisesRegex(ValueError,'endpoint'):process.validate_graph(self.w,g)
 def test_missing_anchor(self):
  g=self.graph();g['relations'][0].update(kind='anchor_distance',anchor_a='missing',anchor_b='middle',tolerance=2)
  with self.assertRaisesRegex(ValueError,'anchors'):process.validate_graph(self.w,g)
 def test_negative_tolerance(self):
  g=self.graph();g['relations'][0].update(kind='anchor_distance',anchor_a='middle',anchor_b='middle',tolerance=-1)
  with self.assertRaisesRegex(ValueError,'tolerance'):process.validate_graph(self.w,g)
 def test_real_ids_required(self):
  with self.assertRaisesRegex(ValueError,'native entity'):process.fingerprints(ROOT/'tests/fixtures/legacy-poster/finishing.vectorcraft',{'label':[999]})
 def test_process_packet(self):
  packet=self.w.status(view='working');self.assertEqual(packet['profile'],'layout-blockout-v1');self.assertNotIn('schemas',packet)
 def test_selected_seed_preview_is_not_production_acceptance(self):
  data=self.observed_studies();p=process.state(self.w);study=p['studies']['0'];p['started']=True
  p['production_seed']={**study,'revision':self.w.state['revision'],'spec_revision':self.w.state['spec_revision']}
  p['production_seed']['images']*=2
  packet=process.packet(self.w);self.assertTrue(packet['preview_current']);self.assertEqual(packet['preview_context'],'production')
  self.assertEqual(self.w.state['completed_stages'],[])
  self.w.state['revision']+=1;self.assertFalse(process.packet(self.w)['preview_current'])
 def test_active_study_packet_exposes_task_and_uncertainty(self):
  p=process.state(self.w);p['active_study']='fixture';p['studies']['fixture']={'revision':1,'capture_revision':1,
   'capture':{'images':[str(self.root/'thumb0.png'),str(self.root/'thumb1.png')]},'plan':{'purpose':'Fixture goal'},
   'checks':[{'id':'fit','description':'Fixture'}],'batch_pending':True}
  packet=process.packet(self.w);self.assertEqual(packet['active_task']['goal'],'Fixture goal');self.assertTrue(packet['preview_current'])
  self.assertEqual(packet['preview_context'],'study');p['studies']['fixture']['uncertain']=True
  packet=process.packet(self.w);self.assertFalse(packet['preview_current']);self.assertIn('never replay',packet['next_action'])
 def test_transition_required_preflight(self):
  with self.assertRaisesRegex(ValueError,'transition'):process.preflight(self.w)
 def test_stale_relations_preflight(self):
  self.w.state['quality_profile']='designer-process-v1';process.state(self.w)['started']=True
  with self.assertRaisesRegex(ValueError,'relationships'):process.preflight(self.w)

class RelationTests(unittest.TestCase):
 def setUp(self):
  import test_focused
  self.f=test_focused.FocusedTests('test_opt_in_and_default_isolation');self.f.setUp()
  self.f.begin();self.f.capture();self.f.confirm()
  self.w=self.f.w;self.w.state['quality_profile']='designer-process-v1';process.initialize(self.w);process.state(self.w)['started']=True
  self.graph={'entities':[{'id':'label','spec_id':'title','role':'Fixture label','anchors':{'middle':[.5,.5]}},{'id':'partner','spec_id':'title','role':'Fixture partner','anchors':{'middle':[.5,.5]}}],
              'relations':[{'id':'relation','kind':'contact','a':'label','b':'partner'}],'dependencies':[]}
  self.w.record(self.f.backend,'entity_graph',self.graph)
  self.data={'version':'capture','element_map':{'label':[4],'partner':[5]},'observations':{'relation':{'outcome':'pass','observation':'Synthetic relation fixture only'}},
             'image_inspection':{'performed':True,'paths':[str(self.w.run/a['path']) for a in self.w.state['versions']['capture']['images']]+[str(self.w.run/self.w.latest('target')['attachments'][0]['path'])],'observations':['Synthetic only']},'image_observation':self.f.fixture.obs}
 def tearDown(self):self.f.tearDown()
 def test_visual_checks_attested_with_no_geometry_score(self):
  self.w.record(self.f.backend,'relation_check',self.data)
  self.assertIsNone(process.state(self.w)['relations']['relation']['diagnostic'])
 def test_actual_mapping_required(self):
  self.data['element_map']['partner']=[999]
  with self.assertRaisesRegex(ValueError,'native entity'):self.w.record(self.f.backend,'relation_check',self.data)
 def test_all_graph_entities_mapped(self):
  self.data['element_map'].pop('partner')
  with self.assertRaisesRegex(ValueError,'all graph'):self.w.record(self.f.backend,'relation_check',self.data)
 def test_stale_graph_rejected(self):
  self.w.state['spec_revision']+=1;self.w.state['versions']['capture']['spec_revision']+=1
  with self.assertRaisesRegex(ValueError,'Stale entity'):self.w.record(self.f.backend,'relation_check',self.data)
 def test_failed_visual_check_queues_one_repair(self):
  self.data['observations']['relation']['outcome']='fail';self.w.record(self.f.backend,'relation_check',self.data)
  self.assertEqual(self.w.state['focused']['queue'][0]['id'],'relation-relation')
  with self.assertRaisesRegex(ValueError,'relationships'):process.preflight(self.w)
 def test_geom_pass_cannot_override_failed_distance(self):
  self.graph['relations'][0].update(kind='anchor_distance',anchor_a='middle',anchor_b='middle',tolerance=0)
  self.w.record(self.f.backend,'entity_graph',self.graph)
  with self.assertRaisesRegex(ValueError,'diagnostic failed'):self.w.record(self.f.backend,'relation_check',self.data)
 def test_inapplicable_requires_reason(self):
  self.data['observations']['relation']['outcome']='not_applicable'
  with self.assertRaisesRegex(ValueError,'reason'):self.w.record(self.f.backend,'relation_check',self.data)
 def test_unknown_change_invalidates_all(self):
  self.w.record(self.f.backend,'relation_check',self.data);process.invalidate(self.w)
  self.assertFalse(process.state(self.w)['relations']['relation']['current'])
 def test_known_native_change_invalidates_incident_relation(self):
  self.w.record(self.f.backend,'relation_check',self.data)
  snap=self.w.state['versions']['capture'];path=self.w.run/snap['native']['path'];native=read(path)
  clone=self.f.root/'modified.vectorcraft';atomic(clone,native);node=nodes_from_native(clone)['4']
  # Modify the actual selected node in the parsed document, not a separate copy.
  def modify(n):
   if isinstance(n,dict):
    if n.get('id')==4 and isinstance(n.get('kind'),dict):n['fixture_change']=1
    for v in n.values():modify(v)
   elif isinstance(n,list):
    for v in n:modify(v)
  modify(native);atomic(clone,native);process.invalidate(self.w,clone)
  self.assertFalse(process.state(self.w)['relations']['relation']['current'])
  self.assertIsNotNone(process.state(self.w)['last_invalidation']['affected_entities'])
 def test_global_document_change_invalidates_all(self):
  self.w.record(self.f.backend,'relation_check',self.data)
  native=read(self.w.run/self.w.state['versions']['capture']['native']['path'])
  native['document']['fixture_global_resource_change']=True
  clone=self.f.root/'global-modified.vectorcraft';atomic(clone,native);process.invalidate(self.w,clone)
  self.assertIsNone(process.state(self.w)['last_invalidation']['affected_entities'])
  self.assertFalse(process.state(self.w)['relations']['relation']['current'])

if __name__=='__main__':unittest.main()
