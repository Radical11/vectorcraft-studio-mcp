"""Synthetic execution checks, not artwork or image-review evidence."""
import copy
import json
from pathlib import Path
import sys
import tempfile
import time
import types
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
import efficient
from workflow import Workflow,read
from vectorcraft_gateway import Gateway,text_result
from telemetry import Metrics
import test_focused


class EfficientTests(unittest.TestCase):
    def setUp(self):
        self.fixture=test_focused.FocusedTests('test_intermediate_pass_does_not_complete_stage')
        self.fixture.setUp()
        self.w=self.fixture.w;self.backend=self.fixture.backend;self.root=self.fixture.root
        self.identity={'version':'fixture','binary_sha256':'a'*64}
        self.w.engine_identity=self.identity
        self.w.state.update(execution_profile=efficient.PROFILE,engine_identity=self.identity)
        self.w.persist()
    def tearDown(self):self.fixture.tearDown()
    def gateway(self):
        return types.SimpleNamespace(workflow=self.w,engine_capabilities={'draw_batch':True},tool_catalog={
            'draw_shape':{'inputSchema':{'properties':{'shape':{'enum':['rectangle']},'x':{},'y':{},'width':{},'height':{},'fill':{}},'required':['shape','x','y','width','height']}}})
    def batch(self):
        return {'steps':[{'id':'draw_shape','params':{'shape':'rectangle','x':1,'y':2,'width':3,'height':4}},
                         {'id':'object.setProps','params':{'id':'$0.id','name':'Fixture'}}]}
    def test_profile_isolation(self):
        for profile in ('designer-v1','legacy-v3','layout-blockout-v1'):
            with self.assertRaisesRegex(ValueError,'Focused build'):
                Workflow(self.root).start(self.backend,brief_path=str(self.root/'brief.md'),quality_profile=profile,execution_profile=efficient.PROFILE)
        with self.assertRaises(ValueError):Workflow(self.root).start(self.backend,mode='quick',scope='fixture',execution_profile=efficient.PROFILE)
        with self.assertRaises(ValueError):Workflow(self.root).start(self.backend,execution_profile='unknown')
    def test_new_profile_requires_identity(self):
        with self.assertRaisesRegex(ValueError,'identity'):
            Workflow(self.root).start(self.backend,brief_path=str(self.root/'brief.md'),quality_profile='focused-execution-v1',execution_profile=efficient.PROFILE)
    def test_packet_reduces_text_keeps_safety(self):
        old=__import__('focused').packet(self.w);new=self.w.status('working')
        self.assertNotIn('contract',new)
        self.assertLess(len(json.dumps(new)),len(json.dumps(old))*.7)
        self.assertEqual(new['revision'],old['revision'])
        self.assertEqual(new['unresolved_findings'],old['unresolved_findings'])
        self.assertIn('schemas',self.w.status('full'))
        self.assertEqual(new['state_reference']['sha256'],__import__('workflow').digest(self.w.run/'run.json'))
    def test_large_packet_has_explicit_reference_gate(self):
        original=__import__('focused').packet(self.w);original['unresolved_findings']=['long fixture'*1000]*10
        packet=efficient.packet(self.w,original)
        self.assertFalse(packet['context_complete'])
        self.assertEqual(packet['blocking_finding_count'],10)
        self.assertTrue(packet['omitted_fields']['unresolved_findings']['retrieve_before_dependent_edits'])
        self.assertTrue(packet['within_packet_target'])
    def test_batch_defaults_and_previous_references(self):
        a=efficient.batch(self.gateway(),self.batch())
        self.assertTrue(a['atomic']);self.assertTrue(a['stop_on_error']);self.assertTrue(a['label'])
    def test_missing_capability_fails_before_dispatch(self):
        g=self.gateway();g.engine_capabilities={}
        with self.assertRaisesRegex(ValueError,'before editing'):efficient.batch(g,self.batch())
    def test_malformed_batch_and_reference_rejected(self):
        for a in ({'steps':[]},{'steps':[{}]*33},{'steps':[{'id':5}]},{'steps':[{'id':'x','params':[]}]},
                  {'steps':[{'id':'x','params':{'id':'$0.id'}}]},
                  {'steps':[{'id':'x'},{'id':'y','params':{'id':'$2.id'}}]}):
            with self.assertRaises(ValueError):efficient.batch(self.gateway(),a)
    def test_drawing_keys_validated(self):
        for key,value in (('shape','invented'),('unknown',1)):
            a=self.batch();a['steps'][0]['params'][key]=value
            with self.assertRaises(ValueError):efficient.batch(self.gateway(),a)
    def test_batch_safety_cannot_be_disabled(self):
        for key,value in (('atomic',False),('stop_on_error',False),('label','')):
            with self.assertRaises(ValueError):efficient.batch(self.gateway(),{**self.batch(),key:value})
    def test_standard_batch_contract_unchanged(self):
        self.w.state['execution_profile']='standard';a={'steps':[],'atomic':False}
        self.assertIs(efficient.batch(self.gateway(),a),a)
    def test_saved_and_unknown_selections_are_edits(self):
        for command in ('select.save','select.editSaved','select.deleteSaved','select.unknown'):
            self.assertEqual(Gateway.operation('command_run',{'id':command}),'edit')
        self.assertEqual(Gateway.operation('command_run',{'id':'select.set','params':{'ids':[1]}}),'read')
    def test_every_batch_member_classified(self):
        with self.assertRaises(ValueError):Gateway.operation('command_batch',{'steps':[{'id':'file.new'},{'id':'select.save'}]})
    def test_stop_preserves_pending_and_acceptance(self):
        self.fixture.begin();pending=copy.deepcopy(self.w.state['pending']);rounds=self.w.state['revision_rounds']
        self.w.state['uncertain']=True
        self.w.record(self.backend,'stop',{'reason':'Fixture failure','unresolved_findings':['Fixture uncertain edit']})
        self.assertEqual(self.w.state['status'],'stopped_unresolved');self.assertEqual(self.w.state['pending'],pending)
        self.assertEqual(self.w.state['revision_rounds'],rounds);self.assertTrue(self.w.state['uncertain'])
        with self.assertRaises(ValueError):self.w.guard_edit()
    def test_stop_requires_disclosure(self):
        with self.assertRaises(ValueError):self.w.record(self.backend,'stop',{'reason':'fixture'})
    def test_stop_resume_requires_feedback_and_preserves_profile(self):
        self.w.record(self.backend,'stop',{'reason':'Fixture','unresolved_findings':['Fixture']})
        new=Workflow(self.root);new.engine_identity=self.identity
        with self.assertRaises(ValueError):new.start(self.backend,resume=str(self.w.run))
        feedback=self.root/'feedback.md';feedback.write_text('Fixture explicit new feedback')
        new=Workflow(self.root);new.engine_identity=self.identity
        new.start(self.backend,resume=str(self.w.run),reopen_reason='Fixture',feedback_path=str(feedback))
        self.assertEqual(new.state['status'],'active');self.assertEqual(new.state['execution_profile'],efficient.PROFILE)
    def test_resume_engine_mismatch_rejected_before_open(self):
        new=Workflow(self.root);new.engine_identity={**self.identity,'version':'different'}
        with self.assertRaisesRegex(ValueError,'engine identity'):new.start(self.backend,resume=str(self.w.run))
    def test_failed_recovery_stays_uncertain(self):
        new=Workflow(self.root);new.engine_identity=self.identity
        call=self.backend.checked_call
        def corrupt(name,args):
            result=call(name,args)
            if name=='open_file':self.backend.native['document']['title']='Fixture corruption'
            return result
        with patch.object(self.backend,'checked_call',side_effect=corrupt):
            with self.assertRaisesRegex(ValueError,'Reopened recovery'):new.start(self.backend,resume=str(self.w.run))
        self.assertTrue(read(new.run/'run.json')['uncertain'])
    def test_partial_batch_marks_uncertainty(self):
        self.fixture.begin();self.w.edited('command_batch',self.batch(),text_result({'failed':1}))
        self.assertTrue(self.w.state['uncertain']);self.assertEqual(self.w.state['revision'],1)
        with self.assertRaises(ValueError):self.w.guard_edit()
    def test_cache_invalidated_on_native_notification(self):
        g=object.__new__(Gateway);g.static_native_tools={'tools':[]};g.tool_catalog={};g.engine_capabilities={'draw_batch':True};g.notify=lambda message:None
        g.native_notify({'method':'notifications/tools/list_changed'})
        self.assertIsNone(g.static_native_tools);self.assertIsNone(g.tool_catalog)
        self.assertEqual(g.engine_capabilities,{})
    def test_capability_does_not_cache_enablement(self):
        self.assertFalse(efficient.capabilities({'tools':[]})['draw_batch'])
        self.assertTrue(efficient.capabilities({'tools':[{'name':'command_batch','description':'draw_path and draw_shape'}]})['draw_batch'])
    def test_area_query_rejects_unverifiable_data(self):
        for value in ({},[],{'overflow':False,'fitScale':float('nan')}):
            with patch.object(self.backend,'checked_call',return_value=text_result(value)):
                with self.assertRaises(ValueError):efficient.area_options(self.backend,4)
    def test_area_query_restores_selection_on_query_error(self):
        calls=[]
        def call(name,args):
            calls.append((name,args))
            if name=='doc_inspect':return text_result({'selection':[7,9]})
            if args['id']=='text.areaOptions':raise RuntimeError('disabled')
            return text_result({})
        with patch.object(self.backend,'checked_call',side_effect=call):
            with self.assertRaises(RuntimeError):efficient.area_options(self.backend,4)
        self.assertEqual(calls[-1][1]['params']['ids'],[7,9])
    def test_unknown_area_error_not_retried(self):
        with patch.object(self.backend,'checked_call',side_effect=RuntimeError('selection transport failed')) as call:
            with self.assertRaises(RuntimeError):efficient.area_options(self.backend,4)
            self.assertEqual(call.call_count,1)
    def test_telemetry_omits_arguments_and_tokens(self):
        m=Metrics(self.root,'fixture');m.record('host','fixture',{'secret':'never log me'},text_result({'a':1}),time.perf_counter())
        row=read_line=m.path.read_text();self.assertNotIn('secret',row);self.assertNotIn('never log',row)
        row=json.loads(row);self.assertIsNone(row['actual_model_tokens']);self.assertGreater(row['request_json_bytes'],0)
        m.close();self.assertIsNone(m.stream)
    def test_telemetry_failure_never_replays(self):
        m=Metrics(self.root,'../escape');m.path=self.root.parent/'escape.jsonl'
        m.record('host','fixture',{},None,time.perf_counter());self.assertEqual(m.error,'ValueError')
    def test_telemetry_marks_partial_batch_failure(self):
        m=Metrics(self.root,'partial');m.record('native','command_batch',{},text_result({'completed':2,'failed':1}),time.perf_counter())
        row=json.loads(m.path.read_text());m.close()
        self.assertTrue(row['failed']);self.assertEqual(row['completed_steps'],2);self.assertEqual(row['failed_steps'],1)
    def test_initial_empty_document_has_verified_recovery(self):
        self.backend.inspect['objects']=0
        w=Workflow(self.root);w.start(self.backend,mode='quick',scope='Fixture empty document',run_id='empty')
        self.assertNotIn('original_version',w.state)
        self.assertTrue((w.run/w.state['recovery']['path']).is_file());w.verify()
    def test_initial_snapshot_failure_blocks_editing(self):
        self.backend.inspect['objects']=0;original=self.backend.checked_call
        def fail(name,args):
            if name=='export':raise RuntimeError('Fixture failed export')
            return original(name,args)
        w=Workflow(self.root)
        with patch.object(self.backend,'checked_call',side_effect=fail):
            with self.assertRaises(RuntimeError):w.start(self.backend,mode='quick',scope='Fixture',run_id='failed-initial')
        self.assertTrue(read(w.run/'run.json')['uncertain'])
        with self.assertRaises(ValueError):w.guard_edit()

if __name__=='__main__':unittest.main()
