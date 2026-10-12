"""Standard-library public manuscript/package checks; not visual or native evidence."""
from pathlib import Path
import json,re,zipfile,hashlib,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve().parent
assert '*.docx binary' in (ROOT/'.gitattributes').read_text()
source=(HERE/'manuscript.md').read_text(encoding='utf-8')
assert source.count('<!-- PAGE -->')==19
assert '54 outputs' in source and 'This protocol is unrun' in source
assert len(list((HERE/'figures').glob('*.svg')))==8
assert len(list((HERE/'figures').glob('comparison-*.png')))==3
refs=json.loads((HERE/'bibliography.json').read_text(encoding='utf-8'))
assert [r['id'] for r in refs]==list(range(1,14))
assert all(r['access'] and r['url'].startswith('https://') for r in refs)
assert 'None is implemented' in source
with zipfile.ZipFile(HERE/'paper-public.docx') as z:
    assert z.testzip() is None
    core=ET.fromstring(z.read('docProps/core.xml'))
    for element in core:
        if element.tag.endswith(('creator','lastModifiedBy')):assert not element.text
    n={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
    xml=ET.fromstring(z.read('word/document.xml'))
    marks={p.attrib.get('{'+n['w']+'}name') for p in xml.findall('.//w:bookmarkStart',n)}
    assert all(h.attrib.get('{'+n['w']+'}anchor') in marks for h in xml.findall('.//w:hyperlink',n) if '{'+n['w']+'}anchor' in h.attrib)
    assert len(xml.findall('.//w:drawing',n))==11
    styles=ET.fromstring(z.read('word/styles.xml'))
    title=next(s for s in styles.findall('w:style',n) if s.attrib.get('{'+n['w']+'}styleId')=='Title')
    assert title.find('.//w:pBdr',n) is None
for suffix in ('docx','pdf'):
    a=HERE/('paper-public.'+suffix);b=ROOT/'site/assets/peer-review'/a.name
    assert a.read_bytes()==b.read_bytes(),'Showcase download must match manuscript bytes'
    if suffix=='pdf':assert a.read_bytes().startswith(b'%PDF-')
    line=hashlib.sha256(a.read_bytes()).hexdigest()+'  '+a.name
    assert line in (HERE/'SHA256SUMS.txt').read_text(encoding='utf-8')
for claim in json.loads((HERE/'evidence-index.json').read_text(encoding='utf-8'))['claims']:
    for p in claim['files']:assert (ROOT/p).exists(),p
print(json.dumps({'manuscript_and_download_structure':'passed','technical_figures':8,'comparison_figures':3,'binary_docx':'passed','visual_inspection_inferred':False}))
