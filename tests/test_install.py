"""Portable transaction tests using temporary homes; never alter user configuration."""
from pathlib import Path
import json,sys,tempfile,unittest
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'));sys.path.insert(0,str(ROOT/'src'))
import install
from discovery import executables
class InstallTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)/'project with spaces';self.home=Path(self.temp.name)/'home';self.root.mkdir();self.home.mkdir()
  for n in install.OWNED:
   p=self.root/'skills'/n;p.mkdir(parents=True);(p/'SKILL.md').write_text('new '+n)
  self.cli=self.root/'vectorcraft-cli.exe';self.desktop=self.root/'vectorcraft.exe';self.cli.write_bytes(b'fixture');self.desktop.write_bytes(b'fixture')
 def tearDown(self):self.temp.cleanup()
 def do(self,dry=False):return install.install(self.home,self.cli,self.desktop,self.root/'vault',dry,self.root)
 def test_fresh_install_and_rollback(self):
  self.do();self.assertEqual(install.owned((self.home/'config.toml').read_text())['command'],sys.executable)
  install.rollback(self.root);self.assertFalse((self.home/'config.toml').exists());self.assertFalse((self.home/'skills/vectorcraft/SKILL.md').exists())
 def test_preserves_unrelated_tables_and_existing_env(self):
  original='model = "example"\n[mcp_servers.other]\ncommand="other"\n[mcp_servers.vectorcraft]\ncommand="old"\n[mcp_servers.vectorcraft.env]\nKEEP="value"\n[mcp_servers.third]\ncommand="third"\n'
  (self.home/'config.toml').write_text(original);self.do();new=(self.home/'config.toml').read_text()
  self.assertEqual(install.others(original),install.others(new));self.assertEqual(install.owned(new)['env']['KEEP'],'value')
  install.rollback(self.root);self.assertEqual(install.parse(original),install.parse((self.home/'config.toml').read_text()))
 def test_quoted_tables(self):
  s='[mcp_servers."vectorcraft"]\ncommand="old"\n[mcp_servers."vectorcraft".env]\nX="kept"\n'
  self.assertEqual(install.owned(install.replace_owned(s,{'command':'new'})),{'command':'new'})
 def test_dry_run_does_not_write(self):
  self.do(True);self.assertFalse((self.home/'config.toml').exists());self.assertFalse((self.root/'.local').exists())
 def test_skill_conflict_blocks_all_rollback_mutations(self):
  self.do();p=self.home/'skills/vectorcraft/SKILL.md';p.write_text('user edit');before=(self.home/'config.toml').read_bytes()
  with self.assertRaisesRegex(ValueError,'conflict'):install.rollback(self.root)
  self.assertEqual(before,(self.home/'config.toml').read_bytes());self.assertEqual(p.read_text(),'user edit')
 def test_config_conflict(self):
  self.do();p=self.home/'config.toml';p.write_text(p.read_text().replace('vectorcraft-cli.exe','different.exe'))
  with self.assertRaisesRegex(ValueError,'conflict'):install.rollback(self.root)
 def test_unrelated_changes_survive_rollback(self):
  self.do();p=self.home/'config.toml';p.write_text(p.read_text()+'\n[mcp_servers.new_other]\ncommand="later"\n')
  install.rollback(self.root);self.assertEqual(install.parse(p.read_text())['mcp_servers']['new_other']['command'],'later')
 def test_snapshot_tamper(self):
  p=self.home/'skills/vectorcraft/SKILL.md';p.parent.mkdir(parents=True);p.write_text('old');r=self.do()
  (self.root/'.local/install-snapshots'/r['snapshot']/'files/skills/vectorcraft/SKILL.md').write_text('tampered')
  with self.assertRaisesRegex(ValueError,'integrity'):install.rollback(self.root)
 def test_existing_extra_owned_files_are_snapshotted_and_conflict_checked(self):
  p=self.home/'skills/vectorcraft/references/older.md';p.parent.mkdir(parents=True);p.write_text('old preserved')
  result=self.do();manifest=json.loads((self.root/'.local/install-snapshots'/result['snapshot']/'manifest.json').read_text())
  self.assertIn('skills/vectorcraft/references/older.md',manifest['before']);p.write_text('later edit')
  with self.assertRaisesRegex(ValueError,'conflict'):install.rollback(self.root)
 def test_snapshot_traversal(self):
  with self.assertRaisesRegex(ValueError,'escapes'):install.rollback(self.root,'../../../outside')
 def test_partial_install_restores_written_skills(self):
  original=install.atomic;calls=0
  def fail(p,content):
   nonlocal calls
   calls+=1
   if calls==3:raise OSError('fixture failure')
   return original(p,content)
  with patch.object(install,'atomic',side_effect=fail):
   with self.assertRaises(OSError):self.do()
  self.assertFalse((self.home/'skills/vectorcraft/SKILL.md').exists());self.assertFalse((self.home/'config.toml').exists())
 def test_explicit_discovery_and_paths_with_spaces(self):self.assertEqual(executables(self.cli,self.desktop),(self.cli.resolve(),self.desktop.resolve()))
 def test_missing_explicit_path_is_not_silently_substituted(self):
  with self.assertRaises(FileNotFoundError):executables(self.root/'missing.exe',self.desktop)
 def test_manifest_and_environment(self):
  m=self.root/'apps.json';m.write_text(json.dumps([{'App':'VectorCraft','Executable':str(self.desktop)}]))
  self.assertEqual(executables(manifest=m,environ={})[0],self.cli.resolve());self.assertEqual(executables(environ={'VECTORCRAFT_CLI':str(self.cli)})[1],self.desktop.resolve())
if __name__=='__main__':unittest.main()
