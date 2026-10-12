"""Run the official skill validator with an isolated optional validation dependency."""
import runpy,sys,os,argparse
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'.local/validation-deps'))
parser=argparse.ArgumentParser();parser.add_argument('--validator');a=parser.parse_args()
validator=Path(a.validator or Path(os.environ.get('CODEX_HOME',Path.home()/'.codex'))/'skills/.system/skill-creator/scripts/quick_validate.py')
if not validator.is_file():raise SystemExit('Official validator unavailable; provide --validator. Public self-contained checks do not require this optional tool.')
for name in ('vectorcraft','vectorcraft-studio'):
 sys.argv=[str(validator),str(ROOT/'skills'/name)]
 try:runpy.run_path(str(validator),run_name='__main__')
 except SystemExit as e:
  if e.code not in (0,None):raise
