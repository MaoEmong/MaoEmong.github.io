import {test} from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import {projects} from '../data/projects.mjs';

const expected=['ems','commerce','support-desk','ieum','pixel-office','video-translator','synapse','travel','langgraph-rag','haru'];
test('public catalog contains exactly the ten agreed projects with six featured projects',()=>{
  assert.deepEqual(projects.map(p=>p.id),expected);
  assert.equal(projects.filter(p=>p.featured).length,6);
});
test('every selected project explains its own problem, decisions, contribution and evidence',()=>{
  for(const p of projects){
    const d=p.detail;
    assert(d,p.id+': missing detailed case study');
    assert(d.problem.length>=2,p.id);
    assert(d.architecture.length>=3,p.id);
    assert(d.journey.length>=4,p.id);
    assert(d.engineering.length>=3,p.id);
    assert(d.contribution.length>=2,p.id);
    assert(d.validation.length>=2,p.id);
    assert(d.limitations.length>=2,p.id);
    assert(d.sources.length>=3,p.id);
    assert(JSON.stringify(d).length>=2200,p.id+': description remains too short');
    for(const c of d.engineering){
      assert(c.problem&&c.choice&&c.tradeoff,p.id+': decision lacks reasoning');
      assert.match(c.source.url,/^https:\/\/github.com\/MaoEmong\//,p.id);
    }
    for(const s of [...d.sources,...d.validation]) assert.match(s.url,/^https:\/\/github.com\//,p.id);
  }
});
test('pixel office uses current 0.2.5 release and matching image captions',()=>{
  const p=projects.find(p=>p.id==='pixel-office');
  assert(p.release.endsWith('/v0.2.5'));
  assert(!JSON.stringify(p).includes('0.1.2'));
});
test('generated selected pages expose substantial HTML and independently downloadable PDF links',async()=>{
  const main=await fs.readFile(new URL('../index.html',import.meta.url),'utf8');
  assert.equal((main.match(/data-project /g)||[]).length,10);
  for(const p of projects){
    const html=await fs.readFile(new URL('../projects/'+p.id+'/index.html',import.meta.url),'utf8');
    for(const id of ['context','features','architecture','engineering','contribution','validation','sources']){
      assert(html.includes('id="'+id+'"'),p.id+': missing section '+id);
    }
    assert(html.includes('href="/output/pdf/'+p.id+'-portfolio.pdf" download'),p.id);
    assert(html.includes(p.detail.engineering[0].choice.replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;')),p.id+': missing actual decision text');
  }
});
