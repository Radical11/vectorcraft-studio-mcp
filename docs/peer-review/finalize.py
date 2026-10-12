"""Sanitize rendered PDFs and audit editions; visual page inspection remains separate.

Run after build.py and render_docx.py. Uses pypdf and Pillow in document runtime.
"""
from pathlib import Path
import json,re,zipfile,hashlib,shutil,io
from lxml import etree
from pypdf import PdfReader,PdfWriter
from PIL import Image

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
OUT=ROOT/'outputs/peer-review'
TOKENS=re.compile(r'Radical11|notak|Vihaan|25BYB|98827734|C:[/\\]+Users|D:[/\\]+vectorcraftmcp|3db96ca|efbb6e6',re.I)
N={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
results={}
for edition in ('public','blind'):
    doc=HERE/'paper-public.docx' if edition=='public' else OUT/'paper-blind.docx'
    src=OUT/('final-'+edition)/('paper-'+edition+'.pdf')
    dest=HERE/'paper-public.pdf' if edition=='public' else OUT/'paper-blind.pdf'
    reader=PdfReader(src);assert len(reader.pages)==20
    writer=PdfWriter();writer.clone_document_from_reader(reader)
    writer.add_metadata({'/Title':'Preserving design intent in agent assisted vector graphics','/Author':'','/Creator':'','/Producer':'LibreOffice verified render','/Subject':'Research style report and future algorithm proposal','/Keywords':'vector graphics, proposed algorithm'})
    writer._root_object.pop('/Metadata',None)
    with dest.open('wb') as f:writer.write(f)
    cleaned=PdfReader(dest);pdftext='\n'.join(p.extract_text() for p in cleaned.pages)
    citations=set(map(int,re.findall(r'\[(\d+)\]',pdftext)));assert set(range(1,14)).issubset(citations)
    with zipfile.ZipFile(doc) as z:
        assert z.testzip() is None
        xml='\n'.join(z.read(n).decode('utf-8') for n in z.namelist() if n.endswith(('.xml','.rels')))
        for n in ('dc:creator','cp:lastModifiedBy'):
            props=etree.fromstring(z.read('docProps/core.xml'))
            ns={'dc':'http://purl.org/dc/elements/1.1/','cp':'http://schemas.openxmlformats.org/package/2006/metadata/core-properties'}
            assert not ''.join(props.xpath('//'+n+'/text()',namespaces=ns))
        document=etree.fromstring(z.read('word/document.xml'))
        anchors=document.xpath('//w:hyperlink/@w:anchor',namespaces=N)
        marks=document.xpath('//w:bookmarkStart/@w:name',namespaces=N)
        assert all(a in marks for a in anchors)
        assert len(document.xpath('//w:drawing',namespaces=N))==11
        media=[]
        for n in z.namelist():
            if n.startswith('word/media/'):
                im=Image.open(io.BytesIO(z.read(n)));assert not TOKENS.search(str(im.info));media.append(n)
        if edition=='blind':
            assert not TOKENS.search(xml)
            assert not re.search(r'[0-9a-f]{40}',xml)
            assert not TOKENS.search(pdftext+str(cleaned.metadata))
            for page in cleaned.pages:
                for ref in page.get('/Annots',[]):
                    annotation=ref.get_object();action=annotation.get('/A',{})
                    assert not TOKENS.search(str(action))
    results[edition]={'pages':len(cleaned.pages),'docx_zip_valid':True,'author_properties_blank':True,'citation_bookmarks_valid':True,'embedded_figures':len(media),'pdf_sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'docx_sha256':hashlib.sha256(doc.read_bytes()).hexdigest(),'blind_text_links_metadata_media_audit':'passed' if edition=='blind' else 'not applicable'}
site=ROOT/'site/assets/peer-review';site.mkdir(parents=True,exist_ok=True)
for suffix in ('pdf','docx'):shutil.copy2(HERE/('paper-public.'+suffix),site/('paper-public.'+suffix))
(OUT/'audit.json').write_text(json.dumps({'editions':results,'automated_scope':'structure metadata links and text; cannot establish visual quality','gateway_changed':False},indent=2),encoding='utf-8')
print(json.dumps(results))
