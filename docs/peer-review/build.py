"""Deterministic two-edition manuscript builder. Requires python-docx and bundled sharp.

Run with the Codex bundled document runtime. No engine, installer, or algorithm edits.
The Markdown manuscript and bibliography are the authoritative editable content.
"""
from pathlib import Path
import argparse, json, re, subprocess, html, hashlib, shutil
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.opc.constants import RELATIONSHIP_TYPE as RT
from PIL import Image

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
PARSER=argparse.ArgumentParser()
PARSER.add_argument('--node', required=True)
PARSER.add_argument('--node-modules', required=True)
PARSER.add_argument('--blind-output', default='outputs/peer-review')
A=PARSER.parse_args()
BLIND=(ROOT/A.blind_output).resolve(); BLIND.mkdir(parents=True,exist_ok=True)
QA=ROOT/'outputs/peer-review/build'; QA.mkdir(parents=True,exist_ok=True)
FIG=HERE/'figures';FIG.mkdir(exist_ok=True)

def svg(name,height,nodes,edges,notes=()):
    pieces=['<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="%s" viewBox="0 0 1200 %s">'%(height,height),'<rect width="1200" height="100%" fill="white"/>','<defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L0,6 L9,3 z" fill="#34495e"/></marker></defs>']
    for x1,y1,x2,y2,label,dashed in edges:
        pieces.append(f'<path d="M{x1},{y1} L{x2},{y2}" fill="none" stroke="#34495e" stroke-width="3" marker-end="url(#arrow)"'+(' stroke-dasharray="9 7"' if dashed else '')+'/>')
        if label:
            lx=(x1+x2)/2;ly=(y1+y2)/2-13;lw=len(label)*14+18
            pieces.append(f'<rect x="{lx-lw/2}" y="{ly-25}" width="{lw}" height="32" fill="white"/>')
            pieces.append(f'<text x="{lx}" y="{ly}" text-anchor="middle" font-family="Arial" font-size="25" fill="#243447">{html.escape(label)}</text>')
    for x,y,w,h,lines,color in nodes:
        pieces.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="{color}" stroke="#567086" stroke-width="2"/>')
        for i,line in enumerate(lines):
            ty=y+h/2-(len(lines)-1)*18+i*36+10
            pieces.append(f'<text x="{x+w/2}" y="{ty}" text-anchor="middle" font-family="Arial" font-size="28" fill="#162c3e">{html.escape(line)}</text>')
    for x,y,line in notes:pieces.append(f'<text x="{x}" y="{y}" text-anchor="middle" font-family="Arial" font-size="26" fill="#243447">{html.escape(line)}</text>')
    pieces.append('</svg>');(FIG/(name+'.svg')).write_text('\n'.join(pieces),encoding='utf-8')

C='#eaf1f6';P='#f6eee3';G='#edf3eb'
svg('01-timeline',460,[(20,70,260,140,['Imported helpers','gateway 1.0.0','Studio version 2'],C),(320,70,260,140,['Version 3','gates and','revision evidence'],C),(620,70,260,140,['designer-v1','concept review','native study'],C),(920,70,260,140,['Public alpha','matched review','owner selection'],G)],[(280,140,320,140,'',False),(580,140,620,140,'',False),(880,140,920,140,'',False)],[(150,45,'12 October 2026'),(450,270,'Unequal sizes corrected'),(790,320,'Score movement is not regression'),(600,405,'Originals retained and mixed outcomes disclosed')])
svg('02-architecture',540,[(35,80,330,180,['Host agent','research and copy','image observation','design judgment'],C),(435,80,330,180,['Companion gateway','workflow contracts','revision evidence','connection isolation'],G),(835,80,330,180,['Native editor','paths and live text','render and export','document inspection'],C),(35,375,330,110,['Skills','activation and routine'],P),(435,375,330,110,['Shared vault','attributed lessons'],P)],[(365,160,435,160,'',False),(765,160,835,160,'',False),(200,375,200,260,'',False),(600,375,600,260,'',True)])
svg('03-current-workflow',560,[(25,40,340,160,['Research','brief and calibration','three alternatives','fresh concept review'],C),(430,40,340,160,['Target and specification','copy and placements','meaningful features','native object mappings'],C),(835,40,340,160,['Build','construction study','four planned stages','full and use renders'],G),(835,330,340,150,['Preflight and critique','two fresh specialists','candidate best original'],C),(430,330,340,150,['Correct and retain','consequential findings','bounded revisions'],P),(25,330,340,150,['Deliver and learn','best reviewed version','disclosed weaknesses'],G)],[(365,120,430,120,'',False),(770,120,835,120,'',False),(1005,200,1005,330,'',False),(835,405,770,405,'',False),(430,405,365,405,'',False),(600,330,600,235,'new evidence',True)],[(600,530,'Quick mode records narrow scope instead of this full sequence')])
svg('04-revision',430,[(20,70,250,130,['Revision r','planned edits','pending state'],C),(320,70,250,130,['Capture','native snapshot','full and use views'],C),(620,70,250,130,['Confirm','actual observation','current mappings'],G),(920,70,260,130,['Preflight','eligible packet','review readiness'],G)],[(270,135,320,135,'',False),(570,135,620,135,'',False),(870,135,920,135,'',False),(1060,245,180,245,'subsequent edit creates revision r + 1',True)],[(600,330,'New edits clear readiness and require refreshed evidence'),(600,382,'Old snapshots survive as retained comparison artifacts')])
svg('05-proposed-pipeline',600,[(25,45,340,120,['Brief and references','three rough layouts'],P),(430,45,340,120,['Coarse vector studies','silhouette and contact'],P),(835,45,340,120,['Concept selection','target and specification'],P),(835,305,340,145,['Semantic decomposition','entities and two graphs','meaningful native parts'],P),(430,305,340,145,['Progressive assembly','focal interactions first','local and whole inspection'],P),(25,305,340,145,['Critique and retain','adaptive correction','bounded stopping'],P)],[(365,105,430,105,'',False),(770,105,835,105,'',False),(1005,165,1005,305,'',False),(835,375,770,375,'',False),(430,375,365,375,'',False)],[(600,235,'PROPOSED AND UNRUN'),(600,525,'Exact copy  /  live text  /  editable paths  /  current evidence')])
svg('06-hierarchy',410,[(450,5,300,55,['Repair scene'],P),(40,95,320,60,['Radio object'],C),(440,95,320,60,['Student object'],C),(840,95,320,60,['Tool object'],C),(40,200,320,60,['Case  grille  screw'],G),(440,200,320,60,['Arm  hand contour'],G),(840,200,320,60,['Handle  shaft  tip'],G),(40,305,320,60,['Paths and ellipses'],C),(440,305,320,60,['Bézier contours'],C),(840,305,320,60,['Paths and anchors'],C)],[(540,60,200,95,'',False),(600,60,600,95,'',False),(660,60,1000,95,'',False),(200,155,200,200,'',False),(600,155,600,200,'',False),(1000,155,1000,200,'',False),(200,260,200,305,'',False),(600,260,600,305,'',False),(1000,260,1000,305,'',False)],[(600,402,'Scene  →  objects  →  meaningful parts  →  native primitives')])
svg('07-relationships',450,[(30,70,230,65,['Hand'],C),(380,70,230,65,['Driver'],C),(30,255,230,65,['Case'],C),(380,255,230,65,['Screw'],C),(725,65,440,65,['Case and screw anchor'],P),(725,180,440,65,['Driver shaft and handle'],P),(725,295,440,65,['Grip and support contours'],P)],[(260,102,380,102,'grasp',False),(490,135,490,255,'contact',False),(145,135,145,255,'support',False),(260,287,380,287,'contains',False),(945,130,945,180,'',False),(945,245,945,295,'',False)],[(300,35,'Spatial relationships'),(945,35,'Assembly dependencies'),(300,420,'May contain cycles'),(945,420,'Directed and acyclic')])
svg('08-selection',555,[(25,50,330,150,['Current candidate','retained best','untouched original'],C),(435,50,330,150,['Two fresh specialists','common-brief votes','explicit regression'],C),(835,50,340,150,['Select best','agreed no-loss candidate','otherwise incumbent'],G),(835,325,340,135,['Stop if resolved','three corrections used','or two without gain'],P),(25,325,330,135,['Deliver retained best','original may win','disclose limitations'],G)],[(355,125,435,125,'',False),(765,125,835,125,'',False),(1005,200,1005,325,'',False),(835,392,355,392,'stop',False),(835,325,765,200,'correct and refresh',True)],[(600,525,'Maximum three correction rounds  /  scores alone do not select the winner')])
js='const sharp=require(process.argv[1]);const fs=require("fs");const path=require("path");(async()=>{for(const p of fs.readdirSync(process.argv[2]).filter(x=>x.endsWith(".svg"))){await sharp(path.join(process.argv[2],p)).png().toFile(path.join(process.argv[2],p.replace(/svg$/,"png")));}})().catch(e=>{console.error(e);process.exit(1)});'
subprocess.run([A.node,'-e',js,str(Path(A.node_modules)/'sharp'),str(FIG)],check=True)

refs=json.loads((HERE/'bibliography.json').read_text(encoding='utf-8'))
bibauthors={1:'Ximing Xing and Qian Yu and Chuang Wang and Haitao Zhou and Jing Zhang and Dong Xu',2:'Ari Seff and Yaniv Ovadia and Wenda Zhou and Ryan P. Adams',3:'Tzu-Mao Li and Michal Lukáč and Michaël Gharbi and Jonathan Ragan-Kelley',4:'Sagi Polaczek and Yuval Alaluf and Elad Richardson and Yael Vinker and Daniel Cohen-Or',5:'Bradley Camburn and Vimal Viswanathan and Julie Linsey and David Anderson and Daniel Jensen and Richard Crawford and Kevin Otto and Kristin Wood',6:'Lianmin Zheng and others',13:'Leyla Alipour and Mohsen Faizi'}
with (HERE/'bibliography.bib').open('w',encoding='utf-8') as f:
    for r in refs:f.write('@misc{'+r['key']+',\n  author = {'+bibauthors.get(r['id'],'{'+r['authors']+'}')+'},\n  title = {'+r['title']+'},\n  year = {'+r['year']+'},\n  howpublished = {'+r['venue']+'},\n  url = {'+r['url']+'},\n  note = {'+r['access']+'}\n}\n\n')

def link(p,label,url=None,anchor=None):
    h=OxmlElement('w:hyperlink')
    if url:h.set(qn('r:id'),p.part.relate_to(url,RT.HYPERLINK,is_external=True))
    else:h.set(qn('w:anchor'),anchor)
    r=OxmlElement('w:r');rp=OxmlElement('w:rPr');co=OxmlElement('w:color');co.set(qn('w:val'),'244A66');rp.append(co);r.append(rp);t=OxmlElement('w:t');t.text=label;r.append(t);h.append(r);p._p.append(h)

def text(p,s):
    for chunk in re.split(r'(\[\d+(?:[–,]\d+)*\])',s):
        if re.fullmatch(r'\[\d+(?:[–,]\d+)*\]',chunk):link(p,chunk,anchor='ref'+re.search(r'\d+',chunk)[0])
        else:p.add_run(chunk)

def bookmark(p,n):
    s=OxmlElement('w:bookmarkStart');s.set(qn('w:id'),str(n));s.set(qn('w:name'),'ref'+str(n));e=OxmlElement('w:bookmarkEnd');e.set(qn('w:id'),str(n));p._p.append(s);p._p.append(e)

def style(d):
    sec=d.sections[0];sec.page_width=Inches(8.5);sec.page_height=Inches(11)
    sec.top_margin=sec.bottom_margin=Inches(.68);sec.left_margin=sec.right_margin=Inches(.78)
    sec.header_distance=sec.footer_distance=Inches(.28)
    for name in ('Normal','Title','Subtitle','Heading 1','Heading 2','Caption'):
        st=d.styles[name];st.font.name='Times New Roman';st.font.color.rgb=RGBColor(0,0,0)
        for el in list(st.element.iter()):
            if el.tag==qn('w:pBdr'):el.getparent().remove(el)
        fonts=st.element.get_or_add_rPr().get_or_add_rFonts()
        for attr in ('asciiTheme','hAnsiTheme','eastAsiaTheme','cstheme'):
            fonts.attrib.pop(qn('w:'+attr),None)
        for attr in ('ascii','hAnsi','eastAsia','cs'):fonts.set(qn('w:'+attr),'Times New Roman')
    n=d.styles['Normal'];n.font.size=Pt(11);n.paragraph_format.line_spacing=1.12;n.paragraph_format.space_after=Pt(7)
    for name,size in [('Title',21),('Subtitle',11),('Heading 1',14),('Heading 2',12),('Caption',10)]:
        st=d.styles[name];st.font.size=Pt(size);st.paragraph_format.space_after=Pt(7);st.paragraph_format.space_before=Pt(4)
    d.styles['Title'].font.bold=True;d.styles['Heading 1'].font.bold=True;d.styles['Heading 2'].font.bold=True
    d.styles['Caption'].font.italic=True;d.styles['Caption'].font.bold=False;d.styles['Caption'].paragraph_format.line_spacing=1.05
    h=sec.header.paragraphs[0];h.add_run('Preserving design intent in agent assisted vector graphics').font.size=Pt(9)
    p=sec.footer.paragraphs[0];p.alignment=WD_ALIGN_PARAGRAPH.RIGHT
    for ins in ('PAGE',):
        fld=OxmlElement('w:fldSimple');fld.set(qn('w:instr'),ins);p._p.append(fld)
    props=d.core_properties;props.author='';props.last_modified_by='';props.title='Preserving design intent in agent assisted vector graphics';props.subject='Research style report and future algorithm proposal';props.keywords='vector graphics, workflow evidence, proposed refinement';props.comments='';props.identifier=''

def table(d,lines):
    data=[[c.strip() for c in line.strip('|').split('|')] for line in lines if not re.fullmatch(r'[|\- :]+',line)]
    t=d.add_table(rows=0,cols=len(data[0]));t.alignment=WD_TABLE_ALIGNMENT.CENTER;t.autofit=False
    widths=[2.05,4.89] if len(data[0])==2 else [3.05,.7,3.19]
    for col,width in zip(t.columns,widths):col.width=Inches(width)
    for rowindex,row in enumerate(data):
        cells=t.add_row().cells
        for i,(cell,val) in enumerate(zip(cells,row)):
            cell.width=Inches(widths[i]);cell.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
            p=cell.paragraphs[0];p.paragraph_format.line_spacing=1.05;p.paragraph_format.space_after=Pt(4);p.paragraph_format.space_before=Pt(4)
            if len(row)==3 and i==1:p.alignment=WD_ALIGN_PARAGRAPH.CENTER
            run=p.add_run(val);run.font.size=Pt(10.5);run.bold=rowindex==0
            pr=cell._tc.get_or_add_tcPr();shade=OxmlElement('w:shd');shade.set(qn('w:fill'),'EAF1F6' if rowindex==0 else ('F7F9FA' if rowindex%2==0 else 'FFFFFF'));pr.append(shade)
            borders=OxmlElement('w:tcBorders')
            for edge in ('top','left','bottom','right'):
                b=OxmlElement('w:'+edge);b.set(qn('w:val'),'single');b.set(qn('w:sz'),'4');b.set(qn('w:color'),'D9D9D9');borders.append(b)
            pr.append(borders)
        trPr=t.rows[-1]._tr.get_or_add_trPr();cant=OxmlElement('w:cantSplit');trPr.append(cant)
        if rowindex==0:repeat=OxmlElement('w:tblHeader');trPr.append(repeat)
    d.add_paragraph().paragraph_format.space_after=Pt(0)

def image(d,path,width=6.94):
    p=d.add_paragraph();p.alignment=WD_ALIGN_PARAGRAPH.CENTER;p.paragraph_format.space_after=Pt(4)
    p.paragraph_format.keep_with_next=True
    p.add_run().add_picture(str(path),width=Inches(width))

def pair(d,case):
    # Two unchanged artworks, re-encoded only to strip ancillary PNG metadata.
    imgs=[]
    for track in ('baseline','improved'):
        im=Image.open(ROOT/'examples'/case/track/'use.png').convert('RGB');imgs.append(im)
    w,h=imgs[0].size;out=Image.new('RGB',(w*2+40,h),'white');out.paste(imgs[0],(0,0));out.paste(imgs[1],(w+40,0))
    p=FIG/('comparison-'+case+'.png');out.save(p);image(d,p,6.4 if case=='campus-poster' else 6.94)

source=(HERE/'manuscript.md').read_text(encoding='utf-8')
def build(edition):
    d=Document();style(d);lines=source.splitlines();i=0
    while i<len(lines):
        line=lines[i]
        if not line:i+=1;continue
        if line=='<!-- PAGE -->':d.add_page_break()
        elif line=='!REFERENCES':
            for r in refs:
                p=d.add_paragraph();p.paragraph_format.line_spacing=1.02;p.paragraph_format.space_after=Pt(4);bookmark(p,r['id'])
                content=f"[{r['id']}] {r['authors']} ({r['year']}). {r['title']}. {r['venue']}. "
                if edition=='blind' and r['id']>=10 and r['id']<=12:
                    content={10:'[10] Anonymous project evidence dossier (2026). Sanitized records and claim index supplied as companion evidence.',11:'[11] Anonymous implementation (2026). Version three workflow designer gateway and installer contracts. Identifying source location withheld.',12:'[12] Anonymous experimental release (2026). Selected artwork and reproducibility materials. Identifying release link withheld.'}[r['id']]
                    p.add_run(content)
                else:p.add_run(content);link(p,'Source',r['url'])
                for run in p.runs:run.font.size=Pt(9.5)
        elif line=='!EDITION':
            p=d.add_paragraph()
            if edition=='blind':p.add_run('Blind review edition. Author identifiers, owned repository and release links, identifying commits, and personal metadata are withheld. Evidence is referenced through anonymous relative artifact labels.')
            else:
                p.add_run('Public edition. ')
                for label,url in [('Repository','https://github.com/Radical11/vectorcraft-studio-mcp'),('Alpha release','https://github.com/Radical11/vectorcraft-studio-mcp/releases/tag/v3.1.0-alpha.1'),('Showcase','https://radical11.github.io/vectorcraft-studio-mcp/'),('Reproducibility','https://github.com/Radical11/vectorcraft-studio-mcp/blob/main/docs/peer-review/README.md')]:link(p,label,url);p.add_run('  ')
        elif line.startswith('!FIG'):
            image(d,HERE/re.search(r'\((.+)\)',line)[1])
        elif line.startswith('!PAIR'):pair(d,re.search(r'\[(.+)\]',line)[1])
        elif line.startswith('|'):
            group=[]
            while i<len(lines) and lines[i].startswith('|'):group.append(lines[i]);i+=1
            table(d,group);continue
        elif line.startswith('```'):
            i+=1;p=d.add_paragraph();p.paragraph_format.line_spacing=1.02;p.paragraph_format.space_after=Pt(5)
            while i<len(lines) and not lines[i].startswith('```'):
                r=p.add_run(lines[i]+'\n');r.font.name='Consolas';r.font.size=Pt(9);i+=1
        elif line.startswith('# '):d.add_paragraph(line[2:],'Title')
        elif line.startswith('### '):d.add_paragraph(line[4:],'Heading 2')
        elif line.startswith('## '):d.add_paragraph(line[3:],'Heading 1')
        elif line.startswith(('Figure ','Table ')):text(d.add_paragraph(style='Caption'),line)
        else:text(d.add_paragraph(),line)
        i+=1
    out=HERE/'paper-public.docx' if edition=='public' else BLIND/'paper-blind.docx';d.save(out)
    return out

paths=[build('public'),build('blind')]
blindsource=source.replace('!EDITION','Blind edition identifying project links withheld').replace('!REFERENCES','Numbered references are resolved in the accompanying blind document; see abstract-only access statement.')
(BLIND/'manuscript-blind.md').write_text(blindsource,encoding='utf-8')
shutil.copy2(HERE/'evidence-index.json',BLIND/'anonymous-evidence-index.json')
print(json.dumps({'outputs':[str(p) for p in paths],'planned_pages':source.count('<!-- PAGE -->')+1,'words':len(source.split()),'technical_svg_figures':8}))
