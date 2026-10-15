"""Validate selected public source/assets/site; never treats tests as visual approval."""
from pathlib import Path
import argparse,json,re,sys
from html.parser import HTMLParser
parser=argparse.ArgumentParser();parser.add_argument('--root');a=parser.parse_args();ROOT=Path(a.root).resolve() if a.root else Path(__file__).resolve().parents[1]
for p in ('LICENSE-MIT','LICENSE-APACHE','NOTICE','ASSETS.md','README.md','CONTRIBUTING.md','docs/SUPPORTED.md','docs/EVALUATION.md'):
 assert (ROOT/p).is_file(),p
ledger=(ROOT/'ASSETS.md').read_text(encoding='utf-8');assets=[]
for directory in ('tests/fixtures','examples','site/assets','docs/peer-review','docs/research','public-evidence'):
 for p in (ROOT/directory).rglob('*'):
  if p.is_file() and p.suffix.lower() in ('.png','.jpg','.jpeg','.svg','.vectorcraft','.pdf','.docx'):
   rel=p.relative_to(ROOT).as_posix();assert '| '+rel+' |' in ledger,'Missing asset provenance: '+rel;assets.append(rel)
for directory in ('src','skills','tests','docs','site','examples','public-evidence','scripts','benchmarks'):
 for p in (ROOT/directory).rglob('*'):
  if p.is_file() and '__pycache__' not in p.parts and not ('legacy' in p.parts and 'result' in p.name) and p.suffix in ('.py','.md','.json','.toml','.html','.css','.vectorcraft','.svg','.js','.mjs','.ps1','.yml','.yaml'):
   text=p.read_text(encoding='utf-8-sig');assert not re.search(r'C:[/\\]+Users[/\\]+notak',text),'Private path: '+str(p)
   assert not re.search(r'D:[/\\]+vectorcraftmcp',text),'Private workspace path: '+str(p)
   assert not re.search(r'gh[pousr]_[A-Za-z0-9]{30,}|sk-[A-Za-z0-9]{35,}',text),'Potential credential: '+str(p)
class Links(HTMLParser):
 def __init__(self,p):super().__init__();self.p=p
 def handle_starttag(self,tag,attrs):
  for k,v in attrs:
   if k in ('src','href') and v and not v.startswith(('http:','https:','#','mailto:','data:')):
    destination=(self.p.parent/v.split('#')[0].split('?')[0]).resolve();assert destination.is_relative_to(ROOT),'Link escapes distribution';assert destination.is_file(),(self.p,v)
for p in (ROOT/'site').glob('*.html'):Links(p).feed(p.read_text(encoding='utf-8'))
for p in [ROOT/'README.md',*(ROOT/'docs').rglob('*.md'),*(ROOT/f/'README.md' for f in ('scripts','tests','benchmarks','public-evidence'))]:
 if not p.is_file():continue
 for link in re.findall(r'!?\[[^\]]*\]\(([^\s)]+)\)',p.read_text(encoding='utf-8')):
  if link.startswith(('http:','https:','#','mailto:','data:')):continue
  target=(p.parent/link.split('#')[0]).resolve()
  assert target.is_relative_to(ROOT) and target.exists(),('Broken Markdown link',p.relative_to(ROOT),link)
for p in (ROOT/'skills').glob('*/SKILL.md'):
 text=p.read_text(encoding='utf-8');assert text.startswith('---\n');assert re.search(r'^name: [a-z0-9-]+$',text,re.M);assert re.search(r'^description: .+',text,re.M)
if (ROOT/'public-evidence/process-stages-20261015/index.json').exists():
 from build_stage_evidence import render,SUPPLEMENT,read,sha
 from stage_public import snapshot_audit
 presentation=render(ROOT,ROOT/SUPPLEMENT,check=True)
 audit=read(ROOT/SUPPLEMENT/'publication-audit.json')
 assert audit==snapshot_audit(ROOT),'Publication audit stale'
 for row in audit['files']:
  assert sha(ROOT/row['path'])==row['published_sha256'],'Incorrect public redaction digest'
else:presentation=None
print(json.dumps({'public_assets':len(assets),'source_site_provenance_passed':True,'stage_presentation':presentation,'visual_quality_claimed':False}))
