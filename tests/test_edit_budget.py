"""Edit budget boundaries only; no artwork observations or outcomes."""
import sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'benchmarks'))
from edit_host import guard
class EditBudgetTests(unittest.TestCase):
 def test_no_fifth_planned_batch(self):
  with self.assertRaisesRegex(ValueError,'Four'):guard({'started':0,'batches':4},'workflow_begin',10)
  guard({'started':0,'batches':3},'workflow_begin',10)
 def test_no_post_allowance_calls(self):
  with self.assertRaisesRegex(ValueError,'Ten-minute'):guard({'started':0,'batches':0},'doc_inspect',600)
  guard({'started':0,'batches':0},'doc_inspect',599)
if __name__=='__main__':unittest.main()
