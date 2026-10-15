"""Real native edit-copy preservation with synthetic policy attestations only."""
from pathlib import Path
import shutil,sys,unittest,uuid
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'benchmarks'))
from edit_host import EditSession
from workflow import atomic,digest,native_fingerprint
class NativeEditTests(unittest.TestCase):
 def test_quick_edit_preserves_source_copy_and_captures_new_native(self):
  root=ROOT/'work/research32/editing/verification'/uuid.uuid4().hex;root.mkdir(parents=True)
  source=root/'source.vectorcraft';shutil.copy2(ROOT/'tests/fixtures/legacy-poster/finishing.vectorcraft',source)
  before=digest(source);fingerprint=native_fingerprint(source)
  atomic(root/'binding.json',{'native':{'path':source.name,'sha256':before},'scope':'Native copy-isolation fixture','use_width':450})
  with EditSession(root) as session:
   session.call('workflow_begin',{'stage':'finishing','plan':{'purpose':'Fixture','changes':'Add a native ellipse',
    'checks':'Synthetic policy check only','expected_result':'Additional native object'}})
   session.call('draw_shape',{'shape':'ellipse','x':30,'y':30,'width':20,'height':20,'fill':'#AABBCC'})
   capture=session.call('workflow_checkpoint',{'version':'edit-fixture','data':{'phase':'capture'}})
   self.assertNotEqual(native_fingerprint(capture['native']),fingerprint)
   self.assertTrue(all(Path(p).is_file() for p in capture['images']))
   session.call('workflow_checkpoint',{'version':'edit-fixture','data':{'phase':'confirm',
    'observations':'Synthetic policy fixture, not actual visual acceptance','decision':'Native structure fixture complete'}})
   self.assertEqual(session.budget['batches'],1)
  self.assertEqual(digest(source),before)
if __name__=='__main__':unittest.main()
