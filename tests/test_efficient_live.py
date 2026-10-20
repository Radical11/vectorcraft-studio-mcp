"""Real native transport checks. Fixtures do not establish visual quality."""
from pathlib import Path
import sys,unittest,uuid
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from vectorcraft_gateway import Gateway,INIT,payload
from workflow import native_fingerprint
import efficient

class NativeExecutionTests(unittest.TestCase):
    def setUp(self):
        self.root=ROOT/'work/tests/efficient'/uuid.uuid4().hex;self.root.mkdir(parents=True)
        self.g=Gateway(self.root);self.g.initialize(INIT);self.g.tools()
        self.g.call('workflow_start',{'mode':'quick','scope':'Native transport check','run_id':'fixture'})
    def tearDown(self):self.g.shutdown()
    def call(self,name,args):
        r=self.g.call(name,args)
        if r.get('isError'):raise RuntimeError(r)
        return payload(r)
    def test_area_query_targets_without_selection(self):
        t=self.call('add_text',{'text':'Editable repair copy','x':20,'y':20,'width':400,'height':80,'size':22,'font':'Arial','fit':'none'})
        self.call('command_run',{'id':'select.none'})
        result=efficient.area_options(self.g.backend,t['id'])
        self.assertFalse(result['overflow']);self.assertEqual(result['fitScale'],1)
        native=self.root/'area.vectorcraft';self.call('export',{'format':'vectorcraft','path':str(native)})
        self.call('open_file',{'path':str(native)})
        out=self.root/'reopened.vectorcraft';self.call('export',{'format':'vectorcraft','path':str(out)})
        self.assertEqual(native_fingerprint(native),native_fingerprint(out))
    def test_empty_custom_document_survives_new_connection(self):
        root=self.root/'empty';root.mkdir()
        first=Gateway(root);first.initialize(INIT)
        try:
            result=first.call('command_run',{'id':'file.new','params':{'width':937,'height':1181}})
            self.assertFalse(result.get('isError'))
            first.call('workflow_start',{'mode':'quick','scope':'Empty custom document recovery','run_id':'empty'})
            run=first.workflow.run
            self.assertIn('recovery',first.workflow.state)
        finally:first.shutdown()
        second=Gateway(root);second.initialize(INIT)
        try:
            result=second.call('workflow_start',{'resume':str(run)})
            self.assertFalse(result.get('isError'))
            board=payload(second.call('doc_inspect',{}))['artboards'][0]
            self.assertEqual((board['width'],board['height']),(937,1181))
            self.assertFalse(second.workflow.state['uncertain'])
        finally:second.shutdown()
    def test_saved_selection_is_persistent_edit(self):
        t=self.call('draw_shape',{'shape':'rectangle','x':20,'y':20,'width':30,'height':40,'fill':'#112233','stroke':'none'})
        self.call('command_run',{'id':'select.set','params':{'ids':[t['id']]}})
        before=self.g.workflow.state['revision'];self.call('command_run',{'id':'select.save','params':{'name':'Owned fixture'}})
        self.assertEqual(self.g.workflow.state['revision'],before+1)
        self.assertIn('Owned fixture',self.call('command_run',{'id':'select.savedList'}))
    def test_drawing_references_and_partial_failure_not_replayed(self):
        if not self.g.engine_capabilities['draw_batch']:self.skipTest('0.11 uses individually verified drawing path')
        a={'atomic':True,'label':'Fixture component','stop_on_error':True,'steps':[
            {'id':'draw_path','params':{'d':'M20 20 L80 20 L50 70 Z','fill':'#d55638','stroke':'none','name':'Owned triangle'}},
            {'id':'object.setProps','params':{'id':'$0.id','opacity':80}},
            {'id':'definitely.not.a.command'},
            {'id':'draw_shape','params':{'shape':'ellipse','x':0,'y':0,'width':9,'height':9}}]}
        result=self.g.call('command_batch',a);data=payload(result)
        self.assertEqual(data['completed'],2);self.assertTrue(data['failed'])
        self.assertTrue(self.g.workflow.state['uncertain']);self.assertTrue(self.g.last_checkpoint.is_file())
        ids=data['created'];self.assertEqual(len(ids),1)
        node=self.call('command_run',{'id':'document.node','params':{'id':ids[0],'summary':True,'depth':0,'childLimit':0}})
        self.assertEqual(node['name'],'Owned triangle')
        with self.assertRaises(ValueError):self.g.call('draw_shape',{'shape':'rectangle','x':0,'y':0,'width':5,'height':5})

if __name__=='__main__':unittest.main()
