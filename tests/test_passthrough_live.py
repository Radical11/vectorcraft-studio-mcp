"""Read-only native protocol passthrough evidence, not artwork quality."""
from pathlib import Path
import sys,tempfile,unittest
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from vectorcraft_gateway import NativeMcp
from discovery import executables
class PassthroughTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory(dir=ROOT/'work');root=Path(self.temp.name);cli,_=executables()
  self.native=NativeMcp([str(cli),'mcp','--headless','--automation-read-root',str(root),'--automation-write-root',str(root)],root)
  self.companion=NativeMcp([sys.executable,str(ROOT/'src/launch_mcp.py'),'vectorcraft'],root)
 def tearDown(self):self.companion.close();self.native.close();self.temp.cleanup()
 def test_resource_and_prompt_catalogs_preserved(self):
  for method in ('resources/list','resources/templates/list','prompts/list'):
   self.assertEqual(self.native.request(method,{}),self.companion.request(method,{}))
 def test_prompt_and_resource_reads_preserved(self):
  for method,args in [('prompts/get',{'name':'poster','arguments':{'brief':'Read-only fixture','palette':'green','text':'fixture'}}),('resources/read',{'uri':'vectorcraft://document'})]:
   self.assertEqual(self.native.request(method,args),self.companion.request(method,args))
 def test_companion_identity_and_native_guidance(self):
  result=self.companion.initialize_result;self.assertEqual(result['serverInfo']['name'],'vectorcraft-studio')
  self.assertIn(self.native.initialize_result.get('instructions',''),result['instructions']);self.assertIn('Native VectorCraft guidance:',result['instructions'])
if __name__=='__main__':unittest.main()
