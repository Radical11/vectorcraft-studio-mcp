"""Real native isolation/recovery, with synthetic policy attestations only."""
from pathlib import Path
import sys,uuid,unittest,shutil
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from vectorcraft_gateway import Gateway,INIT,payload
from workflow import read,native_fingerprint

class NativeStudyTests(unittest.TestCase):
 def setUp(self):
  self.root=ROOT/'work/tests/process-live'/uuid.uuid4().hex;self.root.mkdir(parents=True)
  (self.root/'brief.md').write_text('Native isolation fixture. No aesthetic or actual host image judgment is claimed.')
  self.g=Gateway(self.root);self.g.initialize(INIT);self.g.tools()
  self.g.call('command_run',{'id':'file.new','params':{'width':320,'height':200}})
  self.g.backend.checked_call('draw_shape',{'shape':'rectangle','x':20,'y':20,'width':50,'height':40,'fill':'#123456'})
  self.g.call('workflow_start',{'mode':'full','quality_profile':'layout-blockout-v1','brief_path':str(self.root/'brief.md'),'run_id':'parent'})
  brief={k:'Synthetic policy fixture' for k in ('audience','message','response','viewing_context','medium','production_requirements','style')};brief.update(assumptions=[],locked_copy=[])
  self.g.call('workflow_record',{'kind':'design_brief','data':brief})
  research=read(ROOT/'tests/fixtures/legacy-poster/research.json');research['gaps'].append('Reused unit fixture, no fresh source observation')
  self.g.call('workflow_record',{'kind':'research','data':research})
  paths=[]
  for i in range(3):
   dest=self.root/f'thumb{i}.png';shutil.copy2(ROOT/f'tests/fixtures/legacy-poster/thumb-{i+1}.png',dest);paths.append(str(dest))
  urls=[r['url'] for r in research['references']]
  self.obs={'tool':'fixture','evidence':'Synthetic attestations, not visual evidence','observation':'Native integration policy fixture only'}
  calibration={'genre':'expressive-poster','references':[{'research_url':urls[i],'image':paths[i],'observation':'Fixture','principle':'Fixture','application':'Fixture'} for i in range(3)],'image_inspection':{'performed':True,'paths':paths,'observations':['Fixture']},'image_observation':self.obs}
  self.g.call('workflow_record',{'kind':'calibration','data':calibration})
  self.g.call('workflow_record',{'kind':'layout','data':{'alternatives':[{'id':str(i),'concept':f'Fixture {i}','reading_order':'Fixture','negative_space':'Fixture','copy':[],'bounds':{'scene':[0,0,1,1]}} for i in range(3)]}})
  self.plan={'context':'study','study_id':'one','layout_id':'0','purpose':'Fixture','changes':'Fixture','expected_result':'Fixture','checks':[{'id':'fit','description':'Fixture placement'},{'id':'shape','description':'Fixture shape'}]}
 def tearDown(self):self.g.shutdown()
 def begin(self):self.g.call('workflow_begin',{'stage':'composition','plan':self.plan})
 def test_native_study_preserves_parent_and_closes(self):
  w=self.g.workflow;original=w.run/w.state['versions']['original']['native']['path'];fp=native_fingerprint(original)
  self.begin();self.g.call('command_run',{'id':'file.new','params':{'width':120,'height':80}})
  self.g.call('draw_shape',{'shape':'ellipse','x':20,'y':10,'width':40,'height':40,'fill':'#AABBCC'})
  main=payload(self.g.backend.checked_call('doc_inspect',{}));self.assertEqual(main['artboards'][0]['width'],320)
  study=payload(self.g.call('doc_inspect',{}));self.assertEqual(study['artboards'][0]['width'],120)
  capture=payload(self.g.call('workflow_checkpoint',{'version':'draft','data':{'phase':'capture'}}))
  packet=payload(self.g.call('workflow_status',{'view':'working'}));self.assertTrue(packet['study_preview_current'])
  self.assertEqual(packet['full_preview'],capture['images'][0]);self.assertEqual(packet['preview_context'],'study')
  self.assertEqual(packet['active_task']['goal'],'Fixture')
  self.assertGreater(packet['study_revision'],packet['revision'])
  confirmation={'phase':'confirm','outcome':'pass','close_study':True,'observations':'Synthetic check only','check_results':[{'id':c['id'],'outcome':'pass','observation':'Synthetic'} for c in self.plan['checks']], 'image_inspection':{'performed':True,'paths':capture['images'],'observations':['Synthetic']},'image_observation':self.obs}
  self.g.call('workflow_checkpoint',{'version':'draft','data':confirmation})
  self.assertEqual(w.state['revision'],0);self.assertEqual(w.state['completed_stages'],[]);self.assertEqual(fp,native_fingerprint(original))
  self.assertIsNone(self.g.studies.child);self.g.call('workflow_record',{'kind':'blockout','data':{'study_id':'one'}})
 def test_setup_and_active_study_resume(self):
  self.begin();self.g.call('command_run',{'id':'file.new','params':{'width':240,'height':160}})
  self.g.call('draw_shape',{'shape':'rectangle','x':20,'y':20,'width':40,'height':40})
  run=self.g.workflow.run;self.g.shutdown();self.g=Gateway(self.root);self.g.initialize(INIT)
  self.g.call('workflow_start',{'resume':str(run)})
  self.assertEqual(payload(self.g.call('doc_inspect',{}))['artboards'][0]['width'],240)
  self.assertEqual(payload(self.g.backend.checked_call('doc_inspect',{}))['artboards'][0]['width'],320)
  with self.assertRaisesRegex(ValueError,'Parent records'):self.g.call('workflow_record',{'kind':'layout','data':{}})
 def test_missing_study_checks_before_side_effect(self):
  self.plan['checks']=[]
  with self.assertRaisesRegex(ValueError,'checks'):self.begin()
  self.assertIsNone(self.g.studies.child)
 def test_study_failure_is_not_replayed(self):
  self.begin();self.g.call('draw_shape',{'shape':'ellipse','x':20,'y':20,'width':40,'height':40})
  result=self.g.call('command_batch',{'steps':[{'id':'fixture.notReal'},{'id':'object.move','params':{'dx':900,'dy':0}}]})
  self.assertTrue(result.get('isError'))
  with self.assertRaisesRegex(ValueError,'uncertain'):self.g.call('draw_shape',{'shape':'ellipse','x':1,'y':1,'width':5,'height':5})
  self.assertFalse(self.g.workflow.state['uncertain']);self.assertEqual(self.g.workflow.state['revision'],0)

if __name__=='__main__':unittest.main()
