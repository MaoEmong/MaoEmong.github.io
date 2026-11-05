import fs from 'node:fs/promises';
import path from 'node:path';
import assert from 'node:assert/strict';
import {projects,allProjects} from '../data/projects.mjs';
const root=path.resolve(import.meta.dirname,'..');
const manifest=JSON.parse(await fs.readFile(path.join(root,'output/pdf/manifest.json'),'utf8'));
assert.equal(projects.length,11);
assert.equal(new Set(projects.map(p=>p.id)).size,projects.length);
assert.deepEqual(Object.keys(manifest).sort(),projects.map(p=>p.id).sort());
const pages=['index.html','404.html',...allProjects.map(p=>`projects/${p.id}/index.html`)];
let checked=0;
for(const page of pages){
 const html=await fs.readFile(path.join(root,page),'utf8');
 assert(html.includes('lang="ko"'),page);
 assert(!/pixel-office-dev|source-archive|USERPROFILE|\.work\//.test(html),`Private/local data: ${page}`);
 assert.equal((html.match(/<h1\b/g)||[]).length,1,page);
 for(const m of html.matchAll(/(?:href|src)="(\/[^"#?]*)(?:[?#][^"]*)?"/g)){
  const local=path.join(root,decodeURIComponent(m[1]));
  const target=m[1].endsWith('/')?path.join(local,'index.html'):local;
  await fs.access(target).catch(()=>{throw Error(`Broken local link ${page} -> ${m[1]}`)});checked++;
 }
 for(const m of html.matchAll(/href="#([^"]+)"/g))assert(html.includes(`id="${m[1]}"`),`${page}: missing anchor ${m[1]}`);
}
for(const p of projects){
 const html=await fs.readFile(path.join(root,`projects/${p.id}/index.html`),'utf8');
 assert(html.includes(`href="https://github.com/MaoEmong/${p.repo}"`),p.id);
 const pdf=await fs.readFile(path.join(root,'output/pdf',`${p.id}-portfolio.pdf`));
 assert.equal(pdf.subarray(0,5).toString(),'%PDF-');
 assert.equal(pdf.length,manifest[p.id].bytes,p.id);
 const ids=[...html.matchAll(/\bid="([^"]+)"/g)].map(m=>m[1]);
 assert.equal(new Set(ids).size,ids.length,`${p.id}: duplicate element IDs`);
}
const index=await fs.readFile(path.join(root,'index.html'),'utf8');
const sitemap=await fs.readFile(path.join(root,'sitemap.xml'),'utf8');
for(const p of allProjects.filter(p=>p.archived)){
 assert(!index.includes(`/projects/${p.id}/`),`Excluded from catalog: ${p.id}`);
 assert(!sitemap.includes(`/projects/${p.id}/`),`Excluded from sitemap: ${p.id}`);
 const html=await fs.readFile(path.join(root,`projects/${p.id}/index.html`),'utf8');
 assert(html.includes('noindex,follow')&&html.includes('보관된 프로젝트 소개'),p.id);
}
console.log(JSON.stringify({ok:true,selectedProjectPages:projects.length,archivedPages:allProjects.length-projects.length,pdfs:Object.keys(manifest).length,htmlPages:pages.length,localLinks:checked,pdfPages:Object.values(manifest).reduce((sum,p)=>sum+p.pages,0)}));
