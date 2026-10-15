"""Synthetic publication safeguards, not native artwork or visual evidence."""
from pathlib import Path
import importlib.util,tempfile,unittest,json
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('exporter',ROOT/'scripts/export_interim_study.py')
exporter=importlib.util.module_from_spec(spec);spec.loader.exec_module(exporter)
from workflow import atomic,digest,read

class InterimExportTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name);self.oldroot=exporter.ROOT;self.oldledger=exporter.Ledger
  exporter.ROOT=self.root;self.folder=self.root/'work/experiment';self.folder.mkdir(parents=True)
  atomic(self.folder/'protocol.json',{'fixture':True});atomic(self.folder/'ledger.json',{'fixture':True})
  self.trials=[{'id':f't{i}','status':'pending','condition':'designer-v1','brief':'fixture','repeat':1} for i in range(18)]
  self.trials[0].update(status='budget_exhausted',active_seconds=3601,review_seconds=0,batches=1,tool_calls=1,reason='Synthetic partial')
  self.trialroot=self.root/'work/research32/pilot/t0';self.trialroot.mkdir(parents=True)
  atomic(self.trialroot/'completion-report.json',{'profile':'designer-v1','note':str(self.trialroot),'limitations':['SYNTHETIC ONLY']})
  runpath=self.trialroot/'work/vectorcraft-studio/artwork/run.json';runpath.parent.mkdir(parents=True)
  self.native=runpath.parent/'versions/imagery/artwork.vectorcraft';atomic(self.native,{'fixture':'not real artwork'})
  self.run={'format':'vectorcraft-studio-run','version':3,'status':'active','quality_profile':'designer-v1',
   'working_version':'imagery','best_version':None,'completed_stages':['composition','typography','imagery'],
   'pending':{'captured':'unconfirmed-final'},'versions':{'imagery':{'confirmed':True,
    'native':{'path':str(self.native.relative_to(runpath.parent)),'sha256':digest(self.native)},'images':[]}}}
  self.runpath=runpath;atomic(runpath,self.run)
  self.roots=self.root/'roots.json';atomic(self.roots,{'roots':{'t0':str(self.trialroot)}})
  test=self
  class FixtureLedger:
   def __init__(self,*args):self.data={'trials':test.trials};self.folder=test.folder;self.protocol={'model':'SYNTHETIC','limits':{},'locked_files':[]}
  exporter.Ledger=FixtureLedger;self.out=self.root/'public-evidence/fixture'
 def tearDown(self):exporter.ROOT=self.oldroot;exporter.Ledger=self.oldledger;self.tmp.cleanup()
 def export(self):return exporter.export(self.folder,self.roots,self.out)
 def test_all_pending_and_failed_units_retained(self):
  result=self.export();self.assertEqual(result['accounted'],1);self.assertEqual(result['pending'],17)
  d=read(self.out/'checkpoint.json');self.assertEqual(len(d['results']),18);self.assertEqual(d['comparisons'],'Not collected')
 def test_partial_not_promoted_to_pass(self):
  self.export();row=read(self.out/'checkpoint.json')['results'][0]
  self.assertEqual(row['run_status'],'active');self.assertEqual(row['status'],'budget_exhausted')
  d=read(self.out/'attempts/t0/run-summary.json');self.assertEqual(d['pending']['captured'],'unconfirmed-final')
 def test_reference_asset_excluded_and_native_unchanged(self):
  (self.trialroot/'cached-reference.png').write_bytes(b'not redistributable fixture')
  before=self.native.read_bytes();self.export()
  self.assertFalse(list(self.out.rglob('cached-reference.png')))
  self.assertEqual((self.out/'attempts/t0/versions/imagery/artwork.vectorcraft').read_bytes(),before)
 def test_private_report_paths_redacted(self):
  self.export();text=(self.out/'attempts/t0/creator-report.json').read_text(encoding='utf-8')
  self.assertNotIn(str(self.root).replace('\\','\\\\'),text);self.assertIn('<project>',text)
 def test_native_with_private_path_omitted_without_rewrite(self):
  atomic(self.native,{'path':'[private user path withheld]/private/file'});self.run['versions']['imagery']['native']['sha256']=digest(self.native);atomic(self.runpath,self.run)
  self.export();self.assertFalse(read(self.out/'checkpoint.json')['results'][0]['production_capture'])
  self.assertEqual(len(read(self.out/'artifact-manifest.json')['omissions']),1)
 def test_private_paths_in_json_keys_are_redacted(self):
  atomic(self.trialroot/'completion-report.json',{'artifacts':{str(self.trialroot/'owned.png'):'SYNTHETIC HASH'}})
  self.export();report=read(self.out/'attempts/t0/creator-report.json')
  self.assertTrue(next(iter(report['artifacts'])).startswith('<project>'))
 def test_changed_capture_reported_missing_not_replaced(self):
  atomic(self.native,{'changed':'fixture'});self.export()
  self.assertFalse((self.out/'attempts/t0/versions/imagery/artwork.vectorcraft').exists())
  self.assertEqual(len(read(self.out/'artifact-manifest.json')['omissions']),1)
 def test_active_builder_blocks_export(self):
  self.trials[0]['status']='building';self.assertRaises(ValueError,self.export);self.assertFalse(self.out.exists())
 def test_existing_checkpoint_cannot_be_overwritten(self):
  self.export();self.assertRaises(ValueError,self.export)

if __name__=='__main__':unittest.main(verbosity=2)
