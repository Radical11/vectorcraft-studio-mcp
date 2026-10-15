/* Build the new editable research manuscript only. Historical editions untouched.
   Run with the bundled Node runtime and --modules <bundled node_modules>.
   Render the resulting DOCX and inspect every page before delivery. */
import fs from 'node:fs';
import path from 'node:path';
import {createRequire} from 'node:module';
import {fileURLToPath} from 'node:url';
const here=path.dirname(fileURLToPath(import.meta.url));
const args=process.argv.slice(2);
const option=name=>{const i=args.indexOf(name);if(i<0||!args[i+1])throw Error(`Required ${name}`);return args[i+1];};
const modules=path.resolve(option('--modules'));
const out=path.resolve(option('--out'));
const require=createRequire(path.join(modules,'package.json'));
const d=require('docx');
const {Document,Packer,Paragraph,TextRun,HeadingLevel,ExternalHyperlink,Table,TableRow,TableCell,
 WidthType,BorderStyle,VerticalAlign,AlignmentType,Footer,PageNumber,ImageRun}=d;
function runs(text){
 const items=[];const expression=/\[([^\]]+)\]\(([^)]+)\)|`([^`]+)`/g;let position=0,match;
 while((match=expression.exec(text))){
  if(match.index>position)items.push(new TextRun(text.slice(position,match.index)));
  if(match[1])items.push(new ExternalHyperlink({link:match[2],children:[new TextRun({text:match[1],style:'Hyperlink'})]}));
  else items.push(new TextRun({text:match[3],font:'Consolas',size:20}));
  position=expression.lastIndex;
 }
 if(position<text.length)items.push(new TextRun(text.slice(position)));
 return items.length?items:[new TextRun('')];
}
const border={style:BorderStyle.SINGLE,size:4,color:'D9D9D9'};
function table(lines){
 const cells=lines.filter(line=>!/^\|[\s:|-]+\|$/.test(line)).map(line=>line.trim().slice(1,-1).split('|').map(s=>s.trim()));
 const widths=cells[0].length===5?[1800,1740,1740,2040,2040]:Array(cells[0].length).fill(Math.floor(9360/cells[0].length));
 return new Table({width:{size:9360,type:WidthType.DXA},columnWidths:widths,
  borders:{top:border,bottom:border,left:border,right:border,insideHorizontal:border,insideVertical:border},
  rows:cells.map((row,index)=>new TableRow({tableHeader:index===0,children:row.map((text,i)=>new TableCell({
   width:{size:widths[i],type:WidthType.DXA},verticalAlign:VerticalAlign.CENTER,
   shading:{fill:index===0?'E8EDF1':index%2===0?'F6F8FA':'FFFFFF'},
   margins:{top:100,bottom:100,left:105,right:105},children:[new Paragraph({
    spacing:{before:0,after:0,line:245},keepNext:index<cells.length-1,alignment:i===0?AlignmentType.LEFT:AlignmentType.CENTER,
    children:[new TextRun({text,bold:index===0,size:19,color:'000000'})]})]}))}))});
}
const blocks=[];const lines=fs.readFileSync(path.join(here,'manuscript.md'),'utf8').split(/\r?\n/);
for(let i=0;i<lines.length;){
 const line=lines[i].trim();if(!line){i++;continue;}
 const figure=line.match(/^!\[([^\]]+)\]\(([^)]+)\)$/);
 if(figure){const image=path.resolve(here,figure[2]);if(!image.startsWith(here+path.sep))throw Error('Figure escapes manuscript directory');
  blocks.push(new Paragraph({keepNext:true,children:[new ImageRun({data:fs.readFileSync(image),type:'png',
   transformation:{width:624,height:354},altText:{title:figure[1],description:figure[1],name:figure[1]}})]}));i++;continue;}
 if(line.startsWith('|')){const group=[];while(i<lines.length&&lines[i].trim().startsWith('|'))group.push(lines[i++]);blocks.push(table(group));blocks.push(new Paragraph({text:'',spacing:{after:80}}));continue;}
 const heading=line.match(/^(#{1,3})\s+(.+)$/);
 if(heading){blocks.push(new Paragraph({text:heading[2],heading:heading[1].length===1?HeadingLevel.TITLE:heading[1].length===2?HeadingLevel.HEADING_1:HeadingLevel.HEADING_2}));i++;continue;}
 const paragraph=[];while(i<lines.length&&lines[i].trim()&&!/^(#|\||!\[)/.test(lines[i]))paragraph.push(lines[i++].trim());
 blocks.push(new Paragraph({children:runs(paragraph.join(' '))}));
}
blocks.push(new Paragraph({text:'References',heading:HeadingLevel.HEADING_1}));
const bibliography=fs.readFileSync(path.join(here,'bibliography.bib'),'utf8');
for(const entry of bibliography.split(/(?=@misc\{)/).filter(s=>s.startsWith('@misc'))){
 const field=name=>{const match=entry.match(new RegExp(`^\\s*${name} = \\{(.+)\\},?\\s*$`,'m'));return match?match[1].replace(/[{}]/g,''):'';};
 const title=field('title'),author=field('author'),year=field('year'),url=field('url'),note=field('note');
 blocks.push(new Paragraph({spacing:{before:0,after:120},children:[
  new TextRun({text:[author,year].filter(Boolean).join(' ')+'. ',size:20}),
  new ExternalHyperlink({link:url,children:[new TextRun({text:title,style:'Hyperlink',size:20})]}),
  new TextRun({text:note?'. '+note+'.':'.',size:20})]}));
}
const document=new Document({creator:'',lastModifiedBy:'',title:'Evaluating a designer process for native vector authoring agents',
 description:'Experimental control policy calibration and controlled pilot protocol',
 styles:{default:{document:{run:{font:'Cambria',size:22,color:'000000'},paragraph:{spacing:{after:125,line:280}}}},
  paragraphStyles:[
   {id:'Title',name:'Title',basedOn:'Normal',next:'Normal',run:{font:'Cambria',size:40,bold:true,color:'000000'},paragraph:{spacing:{before:0,after:220},keepNext:true}},
   {id:'Heading1',name:'Heading 1',basedOn:'Normal',next:'Normal',run:{font:'Cambria',size:28,bold:true,color:'000000'},paragraph:{spacing:{before:240,after:120},keepNext:true}},
   {id:'Heading2',name:'Heading 2',basedOn:'Normal',next:'Normal',run:{font:'Cambria',size:24,bold:true,color:'000000'},paragraph:{spacing:{before:180,after:100},keepNext:true}}]},
 sections:[{properties:{page:{size:{width:12240,height:15840},margin:{top:1080,bottom:1080,left:1440,right:1440}}},
  footers:{default:new Footer({children:[new Paragraph({alignment:AlignmentType.CENTER,
   children:[new TextRun({children:[PageNumber.CURRENT],size:18,color:'000000'})]})]})},children:blocks}]});
fs.mkdirSync(path.dirname(out),{recursive:true});fs.writeFileSync(out,await Packer.toBuffer(document));
process.stdout.write(JSON.stringify({docx:out,source:path.join(here,'manuscript.md'),renderRequired:true})+'\n');
