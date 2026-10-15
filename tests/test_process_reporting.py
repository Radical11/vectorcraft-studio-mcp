"""Synthetic accounting fixtures, not artwork or visual-review evidence."""
import sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'src'),str(ROOT/'benchmarks')]
import collect_process_results as report
import prepare_blind_comparisons as blind
from experiment import create,Ledger
from workflow import atomic

class ReportingTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name);self.old=report.ROOT;self.old_blind=blind.ROOT
  report.ROOT=self.root;blind.ROOT=self.root
  brief=self.root/'brief.md';brief.write_text('Synthetic fixture')
  briefs=[{'id':str(i),'genre':genre,'path':str(brief)} for i,genre in enumerate(('poster','illustration','information'))]
  self.folder=create(self.root,'fixture',briefs,[],'fixture');ledger=Ledger(self.root,self.folder)
  self.roots={}
  for trial in ledger.data['trials']:
   root=self.root/'work/research32/pilot/fixture'/trial['id'];root.mkdir(parents=True);self.roots[trial['id']]=str(root)
   for name in ('binding.json','host-budget.json'):atomic(root/name,{'fixture':True})
   (root/'host-receipts.jsonl').write_text('')
   atomic(root/'completion-report.json',{'profile':trial['condition'],'limitations':['Synthetic only']})
   ledger.start(trial['id']);ledger.finish(trial['id'],'unavailable',reason='Preserved fixture failure')
  self.roots_path=self.root/'roots.json';atomic(self.roots_path,{'roots':self.roots})
 def tearDown(self):report.ROOT=self.old;blind.ROOT=self.old_blind;self.temp.cleanup()
 def test_failed_trials_remain_in_denominator(self):
  result=report.collect(self.folder,self.roots_path,self.root/'outputs/report')
  self.assertEqual(result['count'],18)
  self.assertIn('No preference',__import__('workflow').read(self.root/'outputs/report/outcomes.json')['quality_claim'])
 def test_missing_failure_report_blocks_complete_accounting(self):
  (Path(next(iter(self.roots.values())))/'completion-report.json').unlink()
  with self.assertRaisesRegex(ValueError,'every trial'):report.collect(self.folder,self.roots_path,self.root/'outputs/report')
 def test_neutral_structure_preserves_bounds_and_omits_creator_history(self):
  data=blind.structure({'history':['creator rationale'],'layers':[{'name':'designer-process-v1 working group',
   'bounds':{'x':1,'y':2,'width':3,'height':4},'kind':'Group'}],'path':'D:/private/creator.json'})
  self.assertEqual(data['layers'][0]['bounds']['width'],3)
  self.assertNotIn('history',data);self.assertNotIn('path',data)
  self.assertNotIn('designer-process-v1',data['layers'][0]['name'])
 def test_missing_artwork_pairs_retained_and_packet_mapping_preserved(self):
  out=self.root/'work/research32/comparisons';result=blind.prepare(self.folder,self.roots_path,out)
  self.assertEqual(result['pairs'],12)
  packet=__import__('workflow').read(out/'pair-01/packet.json')
  self.assertEqual(packet['required_image_paths'],[])
  self.assertIn('No production',packet['variants']['A']['availability'])
  with self.assertRaisesRegex(ValueError,'Preserve'):blind.prepare(self.folder,self.roots_path,out)
if __name__=='__main__':unittest.main()
