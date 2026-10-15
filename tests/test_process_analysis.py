"""Synthetic analysis checks: never artwork or human-preference evidence."""
import importlib.util,json,tempfile,unittest
from pathlib import Path

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('gate',HERE.parent/'benchmarks/assess_process_pilot.py')
gate=importlib.util.module_from_spec(spec);spec.loader.exec_module(gate)

def write(path,data):
 path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(data),encoding='utf-8')

class GateTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
  self.folder=self.root/'experiment';self.packets=self.root/'packets';self.owner=self.root/'owner.json'
  self.trials=[];self.pairs=[];index=[];responses=[]
  self.protocol={'name':'SYNTHETIC-ONLY','inputs':[{'id':b,'genre':b} for b in ('poster','illustration','information')]}
  for b in ('poster','illustration','information'):
   for repeat in (1,2):
    for c in ('designer-v1','layout-blockout-v1','designer-process-v1'):
     self.trials.append({'id':f'{b}-{c}-{repeat}','brief':b,'repeat':repeat,'condition':c,'status':'completed'})
    for baseline in ('designer-v1','layout-blockout-v1'):
     n=len(self.pairs)+1;identifier=f'pair-{n:02d}'
     mapping={'brief':b,'repeat':repeat,'baseline':baseline,'A':f'{b}-{baseline}-{repeat}',
              'B':f'{b}-designer-process-v1-{repeat}'}
     self.pairs.append(mapping);dest=self.packets/identifier;packet_path=dest/'packet.json'
     variants={label:{'images':[str(dest/label/'full.png'),str(dest/label/'use.png')]} for label in ('A','B')}
     paths=[p for v in variants.values() for p in v['images']]
     for p in paths:Path(p).parent.mkdir(parents=True,exist_ok=True);Path(p).write_bytes(b'fixture-not-an-image')
     write(packet_path,{'id':identifier,'variants':variants,'required_image_paths':paths})
     index.append({'id':identifier,'packet':str(packet_path)})
     for role in ('communication','craft'):
      write(dest/f'{role}-review.json',{'pair':identifier,'role':role,'winner':'B',
       'visible_reason':'SYNTHETIC fixture observation, not an actual image.',
       'consequential_regression':{'present':False,'variant':'neither','evidence':'SYNTHETIC'},
       'image_actions':[{'paths':paths}],'limitations':['Fixture only']})
     responses.append({'pair':identifier,'winner':'B','answered':True,'regression':'neither'})
  write(self.folder/'blind-map-private.json',self.pairs);write(self.packets/'index.json',index)
  gate.freeze_inputs(self.packets,self.folder/'blind-map-private.json')
  write(self.owner,{'study':'SYNTHETIC-ONLY','responses':responses})
  test=self
  class FixtureLedger:
   def __init__(self,*args):self.folder=test.folder;self.protocol=test.protocol;self.data={'trials':test.trials}
   def trial(self,identifier):return next(t for t in test.trials if t['id']==identifier)
  self.original=gate.Ledger;gate.Ledger=FixtureLedger
 def tearDown(self):gate.Ledger=self.original;self.tmp.cleanup()
 def run_gate(self,owner=True):return gate.assess(self.folder,self.packets,self.owner if owner else None,self.root/'result.json')
 def mutate(self,path,fn):
  data=json.loads(path.read_text());fn(data);write(path,data)
  if path.name in ('packet.json','blind-map-private.json'):
   (self.packets/'input-manifest.json').unlink();gate.freeze_inputs(self.packets,self.folder/'blind-map-private.json')
 def test_complete_synthetic_agreement(self):
  result=self.run_gate();self.assertEqual(result['gate'],'promising');self.assertEqual(result['agreement_pairs_over_default'],6)
 def test_missing_owner_is_not_agreement(self):
  result=self.run_gate(False);self.assertEqual(result['gate'],'not_established');self.assertEqual(result['agreement_pairs_over_default'],0)
 def test_false_answered_never_counts(self):
  self.mutate(self.owner,lambda d:[v.update(answered=False) for v in d['responses']]);self.assertEqual(self.run_gate()['agreement_pairs_over_default'],0)
 def test_full_regression_blocks_gate_despite_six_preferences(self):
  self.mutate(self.packets/'pair-01/craft-review.json',lambda d:d.update(consequential_regression={'present':True,'variant':'B','evidence':'SYNTHETIC loss'}))
  result=self.run_gate();self.assertEqual(result['agreement_pairs_over_default'],6);self.assertEqual(result['gate'],'not_established')
 def test_missing_artwork_stays_in_denominator(self):
  def remove(d):d['variants']['B']['images']=[];d['required_image_paths']=d['variants']['A']['images']
  self.mutate(self.packets/'pair-01/packet.json',remove)
  result=self.run_gate();self.assertEqual(result['expected_default_pairs'],6);self.assertEqual(result['gate'],'not_established')
 def test_missing_specialist_blocks_gate(self):
  (self.packets/'pair-01/communication-review.json').unlink();self.assertEqual(self.run_gate()['gate'],'not_established')
 def test_incomplete_image_coverage_blocks_gate(self):
  self.mutate(self.packets/'pair-01/craft-review.json',lambda d:d.update(image_actions=[]))
  self.assertEqual(self.run_gate()['gate'],'not_established')
 def test_inconsistent_regression_blocks_gate(self):
  self.mutate(self.packets/'pair-01/craft-review.json',lambda d:d.update(consequential_regression={'present':False,'variant':'B','evidence':'SYNTHETIC inconsistency'}))
  self.assertEqual(self.run_gate()['gate'],'not_established')
 def test_duplicate_owner_pair_rejected(self):
  self.mutate(self.owner,lambda d:d['responses'].append(d['responses'][0]));self.assertRaises(ValueError,self.run_gate)
 def test_wrong_study_rejected(self):
  self.mutate(self.owner,lambda d:d.update(study='wrong'));self.assertRaises(ValueError,self.run_gate)
 def test_wrong_mapped_repeat_rejected(self):
  self.mutate(self.folder/'blind-map-private.json',lambda d:d[0].update(B='poster-designer-process-v1-2'))
  self.assertRaises(ValueError,self.run_gate)
 def test_duplicate_units_rejected(self):
  self.mutate(self.folder/'blind-map-private.json',lambda d:d.__setitem__(1,d[0]));self.assertRaises(ValueError,self.run_gate)
 def test_incomplete_trials_rejected(self):
  self.trials[0]['status']='pending';self.assertRaises(ValueError,self.run_gate)
 def test_packet_identity_rejected(self):
  self.mutate(self.packets/'pair-01/packet.json',lambda d:d.update(id='pair-02'));self.assertRaises(ValueError,self.run_gate)
 def test_unavailable_regression_answer_blocks_gate(self):
  self.mutate(self.owner,lambda d:d['responses'][0].update(regression='cannot_assess'))
  self.assertEqual(self.run_gate()['gate'],'not_established')
 def test_missing_actual_observations_never_counts(self):
  self.mutate(self.packets/'pair-01/craft-review.json',lambda d:d.pop('visible_reason'))
  self.assertEqual(self.run_gate()['gate'],'not_established')
 def test_changed_image_after_freeze_rejected(self):
  (self.packets/'pair-01/A/use.png').write_bytes(b'changed synthetic image')
  self.assertRaises(ValueError,self.run_gate)
 def test_missing_image_after_freeze_rejected(self):
  (self.packets/'pair-01/A/use.png').unlink();self.assertRaises(ValueError,self.run_gate)
 def test_changed_packet_after_freeze_rejected(self):
  p=self.packets/'pair-01/packet.json';d=json.loads(p.read_text());d['new_note']='changed';write(p,d)
  self.assertRaises(ValueError,self.run_gate)
 def test_binding_cannot_be_overwritten(self):
  self.assertRaises(ValueError,gate.freeze_inputs,self.packets,self.folder/'blind-map-private.json')
 def test_absent_binding_blocks_evaluation(self):
  (self.packets/'input-manifest.json').unlink();self.assertRaises(ValueError,self.run_gate)
 def test_escaped_packet_rejected_before_read(self):
  p=self.packets/'index.json';d=json.loads(p.read_text());d[0]['packet']=str(self.root/'absent-outside.json');write(p,d)
  self.assertRaises(ValueError,self.run_gate)

if __name__=='__main__':unittest.main(verbosity=2)
