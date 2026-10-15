"""Serialized production-gateway enforcement and recovery tests; no aesthetic claims."""
from pathlib import Path
import json,sys,unittest,uuid,struct
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from vectorcraft_gateway import NativeMcp,payload

class LiveGatewayTests(unittest.TestCase):
 def setUp(self):
  self.root=ROOT/'work/tests/live-workflow'/uuid.uuid4().hex;self.root.mkdir(parents=True)
  (self.root/'brief.md').write_text('Engine enforcement fixture: no aesthetic review claimed.')
  self.c=self.client()
 def client(self):return NativeMcp([sys.executable,str(ROOT/'src/launch_mcp.py'),'vectorcraft'],self.root)
 def tearDown(self):self.c.close()
 def test_full_prerequisite_batch_ui_and_setup_resume(self):
  self.assertIn('independent critique',self.c.initialize_result['instructions'][:512])
  self.c.checked_call('workflow_start',{'mode':'full','brief_path':str(self.root/'brief.md'),'run_id':'full'})
  self.c.checked_call('command_run',{'id':'file.new','params':{'width':973,'height':541}})
  for tool,args in [('draw_shape',{'shape':'rectangle','x':0,'y':0,'width':20,'height':20}),('command_run',{'id':'object.move','params':{'dx':10,'dy':0}}),('command_batch',{'steps':[{'id':'text.fontList'},{'id':'object.move','params':{'dx':10,'dy':0}}]}),('pointer_gesture',{'events':[{'kind':'down','x':10,'y':10}]})]:
   self.assertTrue(self.c.call(tool,args).get('isError'),(tool,args))
  mixed=self.c.call('command_batch',{'steps':[{'id':'file.new','params':{'width':20,'height':20}},{'id':'object.move','params':{'dx':10,'dy':0}}]})
  self.assertTrue(mixed.get('isError'));self.assertIn('mix',str(mixed))
  self.assertEqual(payload(self.c.checked_call('connection_status',{}))['mode'],'headless')
  self.c.close();self.c=self.client();self.c.checked_call('workflow_start',{'resume':str(self.root/'work/vectorcraft-studio/full')})
  d=payload(self.c.checked_call('doc_inspect',{}));self.assertEqual(d['artboards'][0]['width'],973);self.assertEqual(d['artboards'][0]['height'],541);self.assertEqual(d['objects'],1)
 def test_partial_batch_is_not_replayed(self):
  status=payload(self.c.checked_call('workflow_start',{'mode':'quick','scope':'Isolated partial-failure recovery fixture','run_id':'partial'}))
  shape=payload(self.c.checked_call('draw_shape',{'shape':'ellipse','x':40,'y':40,'width':100,'height':100,'fill':'#173D3A'}))
  self.c.checked_call('command_run',{'id':'select.set','params':{'ids':[shape['id']]}})
  result=self.c.call('command_batch',{'steps':[{'id':'object.move','params':{'dx':20,'dy':0}},{'id':'fixture.nonexistentCommand'},{'id':'object.move','params':{'dx':900,'dy':0}}]})
  self.assertTrue(result.get('isError'));state=payload(self.c.checked_call('workflow_status',{}));self.assertTrue(state['uncertain'])
  denied=self.c.call('command_run',{'id':'object.move','params':{'dx':20,'dy':0}});self.assertTrue(denied.get('isError'))
  self.c.close();self.c=self.client();self.c.checked_call('workflow_start',{'resume':status['run']})
  doc=payload(self.c.checked_call('doc_inspect',{}));shape=doc['layers'][0]['children'][0]
  self.assertEqual(shape['bounds']['x'],60);self.assertFalse(payload(self.c.checked_call('workflow_status',{}))['uncertain'])
 def test_original_preview_uses_intended_width(self):
  self.c.checked_call('open_file',{'path':str(self.copy_fixture())})
  self.c.checked_call('workflow_start',{'mode':'full','brief_path':str(self.root/'brief.md'),'run_id':'view-size','use_width':450})
  p=self.root/'work/vectorcraft-studio/view-size/versions/original/use.png';self.assertEqual(struct.unpack('>II',p.read_bytes()[16:24]),(450,600))
 def test_focused_catalog_compact_packet_and_resume(self):
  catalog=self.c.request('tools/list')['tools'];definitions={t['name']:t for t in catalog}
  profiles=definitions['workflow_start']['inputSchema']['properties']['quality_profile']
  self.assertEqual(profiles['default'],'designer-v1');self.assertIn('focused-execution-v1',profiles['enum'])
  status=payload(self.c.checked_call('workflow_start',{'mode':'full','quality_profile':'focused-execution-v1','brief_path':str(self.root/'brief.md'),'run_id':'focused'}))
  self.c.checked_call('command_run',{'id':'file.new','params':{'width':640,'height':480}})
  packet=payload(self.c.checked_call('workflow_status',{'view':'working'}))
  self.assertEqual(packet['profile'],'focused-execution-v1');self.assertNotIn('schemas',packet)
  self.assertTrue(self.c.call('draw_shape',{'shape':'rectangle','x':0,'y':0,'width':30,'height':30}).get('isError'))
  self.c.close();self.c=self.client();self.c.checked_call('workflow_start',{'resume':status['run']})
  resumed=payload(self.c.checked_call('workflow_status',{'view':'working'}));self.assertEqual(resumed['profile'],'focused-execution-v1')
  doc=payload(self.c.checked_call('doc_inspect',{}));self.assertEqual(doc['artboards'][0]['width'],640)
 def copy_fixture(self):
  import shutil
  p=self.root/'original.vectorcraft';shutil.copy2(ROOT/'tests/fixtures/legacy-poster/finishing.vectorcraft',p);return p

if __name__=='__main__':unittest.main(verbosity=2)
