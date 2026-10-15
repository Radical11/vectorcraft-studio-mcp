/* Deterministic system diagram. No experimental artwork or preference data. */
import fs from 'node:fs';import path from 'node:path';import {fileURLToPath} from 'node:url';import {createRequire} from 'node:module';
const here=path.dirname(fileURLToPath(import.meta.url));const arg=process.argv.indexOf('--modules');
if(arg<0)throw Error('Pass the bundled --modules directory');
const require=createRequire(path.join(path.resolve(process.argv[arg+1]),'package.json'));const sharp=require('sharp');
const escape=s=>s.replace(/[&<>]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;'}[c]));
const pieces=['<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="680" viewBox="0 0 1200 680">',
 '<rect width="1200" height="680" fill="white"/>',
 '<defs><marker id="arrow" markerWidth="9" markerHeight="9" refX="8" refY="4" orient="auto"><path d="M0 0 L8 4 L0 8 Z" fill="#273D46"/></marker><marker id="repair" markerWidth="9" markerHeight="9" refX="8" refY="4" orient="auto"><path d="M0 0 L8 4 L0 8 Z" fill="#9A533C"/></marker></defs>',
 '<text x="30" y="38" font-family="Arial" font-size="28" fill="#000000">Designer process with separate evidence and acceptance</text>'];
const nodes=[
 [30,70,['Brief and references','Audience use and style']],
 [325,70,['Three native studies','Isolated full and use']],
 [620,70,['Fresh concept review','Select a useful rough']],
 [915,70,['Target and specification','Explicit assembly start']],
 [915,265,['Plan one component','Goal preserve and checks']],
 [620,265,['Edit and capture','Native plus full and use']],
 [325,265,['Actually inspect','Task and scene evidence']],
 [30,265,['Task pass or revise','Passing is not a stage']],
 [30,515,['Explicit stage acceptance','Coverage and findings']],
 [325,515,['Mapped relations current','Geometry plus observations']],
 [620,515,['Fresh final specialists','Select retained best']],
 [915,515,['Reopen and inspect','Editable native and exports']]];
const edges=['M290 125 H325','M585 125 H620','M880 125 H915','M1045 180 V265',
 'M915 320 H880','M620 320 H585','M325 320 H290','M160 375 V515','M290 570 H325','M585 570 H620','M880 570 H915'];
for(const edge of edges)pieces.push(`<path d="${edge}" fill="none" stroke="#273D46" stroke-width="2.5" marker-end="url(#arrow)"/>`);
for(const edge of ['M115 375 V435 H1045 V375','M455 515 V435','M750 515 V435'])pieces.push(`<path d="${edge}" fill="none" stroke="#9A533C" stroke-width="2.5" stroke-dasharray="8 5" marker-end="url(#repair)"/>`);
pieces.push(
 '<rect x="357" y="400" width="543" height="29" fill="white"/><text x="625" y="421" text-anchor="middle" font-family="Arial" font-size="22" fill="#75412E">Revise or blocking finding enters a planned correction</text>');
for(const [x,y,lines] of nodes){pieces.push(`<rect x="${x}" y="${y}" width="260" height="110" rx="7" fill="#F0F4F5" stroke="#526A73" stroke-width="1.5"/>`);
 lines.forEach((line,i)=>pieces.push(`<text x="${x+130}" y="${y+46+i*31}" text-anchor="middle" font-family="Arial" font-size="${i?20:22}" fill="#000000">${escape(line)}</text>`));}
pieces.push('<text x="30" y="660" font-family="Arial" font-size="21" fill="#273D46">Host judgments remain attested. Current files and graphs do not establish visual quality.</text></svg>');
const folder=path.join(here,'figures');fs.mkdirSync(folder,{recursive:true});const svg=path.join(folder,'process-control.svg');
fs.writeFileSync(svg,pieces.join('\n'));await sharp(svg).png().toFile(path.join(folder,'process-control.png'));
process.stdout.write(JSON.stringify({svg,png:path.join(folder,'process-control.png'),scope:'System diagram only'})+'\n');
