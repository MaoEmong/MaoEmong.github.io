import fs from 'node:fs/promises';
import path from 'node:path';
import {projects} from '../data/projects.mjs';
const root=path.resolve(import.meta.dirname,'..');
const inventory=JSON.parse(await fs.readFile(path.join(root,'.work/inventory.json'),'utf8'));
const out=path.join(root,'.work/originals');await fs.mkdir(out,{recursive:true});
const records={};let next=0;
await Promise.all(Array.from({length:4},async()=>{while(next<projects.length){const p=projects[next++];const meta=inventory.find(r=>r.name===p.repo);if(!meta)throw Error('Missing public repository: '+p.repo);
 let candidates=meta.images.filter(x=>!x.includes('shields.io')&&!x.includes('badge/')&&!x.endsWith('.svg'));
 if(p.id==='pixel-office')candidates=['docs/screenshots/01-hero.jpg','docs/screenshots/03-conversation.jpg','docs/screenshots/08-stage-history.jpg'];
 if(p.id==='travel')candidates=candidates.filter(x=>!x.includes('header'));
 if(p.id==='cult')candidates=[candidates[2],candidates[4],candidates[0]].filter(Boolean);
 if(p.id==='simple-rpg')candidates=[candidates[2],candidates[3],candidates[0]].filter(Boolean);
 const images=[];
 for(const [i,entry] of candidates.slice(0,3).entries()){
  const url=/^https?:/.test(entry)?entry:`https://raw.githubusercontent.com/MaoEmong/${p.repo}/${meta.defaultBranchRef.name}/${entry.replace(/^\.\//,'')}`;
  try{const response=await fetch(new URL(url));if(!response.ok)throw Error('HTTP '+response.status);const type=response.headers.get('content-type')||'';if(!type.startsWith('image/'))throw Error('Not image: '+type);const data=Buffer.from(await response.arrayBuffer());if(data.length>15*1024*1024)throw Error('Image too large');const file=`${p.id}-${i+1}.image`;await fs.writeFile(path.join(out,file),data);images.push({file,source:url,alt:`${p.title} 소개 화면 ${i+1}`});}
  catch(e){console.log(JSON.stringify({imageSkipped:p.id,url,reason:e.message}));}
 }
 records[p.id]={images,readme:`https://github.com/MaoEmong/${p.repo}/blob/${meta.defaultBranchRef.name}/README.md`,branch:meta.defaultBranchRef.name};
}}));
await fs.writeFile(path.join(root,'.work/assets.json'),JSON.stringify(records,null,2));
const vendor=path.join(root,'assets/vendor/pretext');await fs.mkdir(vendor,{recursive:true});
await fs.cp(path.join(root,'.work/package/dist'),vendor,{recursive:true,filter:f=>!f.endsWith('.map')&&!f.endsWith('.ts')});
await fs.copyFile(path.join(root,'.work/package/LICENSE'),path.join(vendor,'LICENSE'));
console.log(JSON.stringify({projects:projects.length,images:Object.values(records).reduce((n,r)=>n+r.images.length,0),vendor:'Pretext 1.0.0, MIT, local'}));
