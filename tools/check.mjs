import fs from 'node:fs/promises';
import path from 'node:path';
import assert from 'node:assert/strict';
import {projects} from '../data/projects.mjs';
const root=path.resolve(import.meta.dirname,'..');
const manifest=JSON.parse(await fs.readFile(path.join(root,'output/pdf/manifest.json'),'utf8'));
assert.equal(projects.length,20);assert.equal(Object.keys(manifest).length,projects.length);
const pages=['index.html','404.html',...projects.map(p=>`projects/${p.id}/index.html`)];let checked=0;
for(const page of pages){const html=await fs.readFile(path.join(root,page),'utf8');
 assert(html.includes('lang="ko"'),page);
 assert(!/interview-study|pixel-office-dev|source-archive|synapse-design|USERPROFILE|\.work\//.test(html),`Excluded/private data: ${page}`);
 assert.equal((html.match(/<h1\b/g)||[]).length,1,page);
 for(const m of html.matchAll(/(?:href|src)="(\/[^"#?]*)(?:[?#][^"]*)?"/g)){
  const local=path.join(root,decodeURIComponent(m[1]));
  const target=m[1].endsWith('/')?path.join(local,'index.html'):local;
  await fs.access(target).catch(()=>{throw Error(`Broken local link ${page} -> ${m[1]}`);});checked++;
 }
}
for(const p of projects){const html=await fs.readFile(path.join(root,`projects/${p.id}/index.html`),'utf8');
 assert(html.includes(`href="https://github.com/MaoEmong/${p.repo}"`),p.id);
 const pdf=await fs.readFile(path.join(root,'output/pdf',`${p.id}-portfolio.pdf`));assert.equal(pdf.subarray(0,5).toString(),'%PDF-');
 assert.equal(pdf.length,manifest[p.id].bytes,p.id);
}
console.log(JSON.stringify({ok:true,projectPages:projects.length,pdfs:Object.keys(manifest).length,htmlPages:pages.length,localLinks:checked,pdfPages:Object.values(manifest).reduce((s,p)=>s+p.pages,0),privateRepositoryLinks:0,excludedStudyReferences:0}));
