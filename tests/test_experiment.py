"""Ledger fixtures; no generated art, human rating, or model review evidence."""
import sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from experiment import create,Ledger,CONDITIONS

class ExperimentTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
  (self.root/'brief.md').write_text('Locked fixture')
  self.briefs=[{'id':str(i),'genre':g,'path':str(self.root/'brief.md')} for i,g in enumerate(('poster','illustration','information'))]
  self.folder=create(self.root,'fixture',self.briefs,[],model='fixture')
  self.ledger=Ledger(self.root,self.folder);self.identifier=self.ledger.data['trials'][0]['id']
 def tearDown(self):self.temp.cleanup()
 def test_paired_schedule(self):
  self.assertEqual(len(self.ledger.data['trials']),18)
  for condition in CONDITIONS:self.assertEqual(sum(t['condition']==condition for t in self.ledger.data['trials']),6)
 def test_no_overwrite(self):
  with self.assertRaisesRegex(ValueError,'Preserve'):create(self.root,'fixture',self.briefs,[],'fixture')
 def test_changed_input(self):
  (self.root/'brief.md').write_text('Changed')
  with self.assertRaisesRegex(ValueError,'Locked input'):self.ledger.start(self.identifier)
 def test_changed_protocol(self):
  with (self.folder/'protocol.json').open('a') as f:f.write(' ')
  with self.assertRaisesRegex(ValueError,'protocol'):Ledger(self.root,self.folder)
 def test_changed_frozen_code(self):
  code=self.root/'policy.py';code.write_text('original')
  folder=create(self.root,'code-fixture',self.briefs,[],'fixture',locked_files=[code])
  code.write_text('changed')
  with self.assertRaisesRegex(ValueError,'Locked input'):Ledger(self.root,folder)
 def test_one_builder(self):
  self.ledger.start(self.identifier)
  with self.assertRaisesRegex(ValueError,'one active'):self.ledger.start(self.ledger.data['trials'][1]['id'])
 def test_no_rebuild(self):
  self.ledger.start(self.identifier);self.ledger.finish(self.identifier,'failed',reason='Explicit fixture failure')
  with self.assertRaisesRegex(ValueError,'replayed'):self.ledger.start(self.identifier)
 def test_paused_reviews_cannot_edit(self):
  self.ledger.start(self.identifier);self.ledger.pause_review(self.identifier)
  with self.assertRaisesRegex(ValueError,'Active builder'):self.ledger.before_call(self.identifier,'workflow_begin')
  self.ledger.resume_build(self.identifier);self.ledger.before_call(self.identifier,'workflow_begin')
 def test_batch_limit(self):
  self.ledger.start(self.identifier)
  for _ in range(24):self.ledger.before_call(self.identifier,'workflow_begin')
  with self.assertRaisesRegex(ValueError,'Batch'):self.ledger.before_call(self.identifier,'workflow_begin')
 def test_wall_limit(self):
  self.ledger.start(self.identifier);self.ledger.trial(self.identifier)['active_seconds']=3601
  with self.assertRaisesRegex(ValueError,'time exhausted'):self.ledger.before_call(self.identifier,'draw_shape')
 def test_failures_and_blind_mapping_preserved(self):
  for t in self.ledger.data['trials']:
   self.ledger.start(t['id']);self.ledger.finish(t['id'],'unavailable',reason='Fixture only')
  pairs=self.ledger.blind_schedule();self.assertEqual(len(pairs),12);self.assertEqual(pairs,Ledger(self.root,self.folder).blind_schedule())
  for baseline in CONDITIONS[:2]:
   self.assertEqual(sum(CONDITIONS[2] in pair['A'] for pair in pairs if pair['baseline']==baseline),3)
 def test_blind_before_completion_rejected(self):
  with self.assertRaisesRegex(ValueError,'every trial'):self.ledger.blind_schedule()
 def test_completed_requires_actual_record(self):
  self.ledger.start(self.identifier)
  with self.assertRaisesRegex(ValueError,'evidence'):self.ledger.finish(self.identifier,'completed',self.root/'missing.json')
if __name__=='__main__':unittest.main()
