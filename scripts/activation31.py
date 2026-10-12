"""Run a fresh read-only Codex routing probe; no whole-design quality claim."""
from pathlib import Path
import argparse,subprocess,shutil,json
ROOT=Path(__file__).resolve().parents[1];parser=argparse.ArgumentParser();parser.add_argument('--model');a=parser.parse_args();folder=ROOT/'work/activation31/full';folder.mkdir(parents=True,exist_ok=True)
prompt='For this read-only installation routing test, a user asks: Create a substantial campus event poster in VectorCraft. Determine which installed skill/workflow would activate automatically. Actually read both installed VectorCraft skills and call workflow_status; explain the default quality profile and research/calibration/concept/construction-study prerequisites. Do not start a run, edit artwork or write files. Do not use a separate API/model. Return concise evidence. This is a routing probe, not a completed design.'
(folder/'prompt.txt').write_text(prompt);cmd=[shutil.which('codex.cmd') or shutil.which('codex'),'exec','--ephemeral','--json','--skip-git-repo-check','--cd',str(ROOT),'--sandbox','read-only','-o',str(folder/'result.md')]
if a.model:cmd+=['--model',a.model]
with (folder/'session.jsonl').open('w',encoding='utf-8') as out,(folder/'stderr.log').open('w',encoding='utf-8') as err:
 r=subprocess.run([*cmd,prompt],cwd=ROOT,stdout=out,stderr=err)
print(json.dumps({'exit_code':r.returncode,'scope':'read-only fresh-session routing probe','logs':str(folder)}));raise SystemExit(r.returncode)
