import {test} from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import {projects} from '../data/projects.mjs';

const expected=['flowmes','ems','commerce','support-desk','ieum','pixel-office','video-translator','synapse','travel','langgraph-rag','haru'];
test('public catalog leads with FlowMES and preserves the ten existing projects',()=>{
  assert.deepEqual(projects.map(p=>p.id),expected);
  assert.equal(projects.filter(p=>p.featured).length,7);
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
  assert.equal((main.match(/data-project /g)||[]).length,projects.length);
  for(const p of projects){
    const html=await fs.readFile(new URL('../projects/'+p.id+'/index.html',import.meta.url),'utf8');
    for(const id of ['context','features','architecture','engineering','contribution','validation','sources']){
      assert(html.includes('id="'+id+'"'),p.id+': missing section '+id);
    }
    assert(html.includes('href="/output/pdf/'+p.id+'-portfolio.pdf" download'),p.id);
    assert(html.includes(p.detail.engineering[0].choice.replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;')),p.id+': missing actual decision text');
  }
});
test('FlowMES separates completed development, simulated checks and remaining operating limits',async()=>{
  const p=projects.find(p=>p.id==='flowmes');
  assert.equal(p.repo,'flowmes');
  assert(p.detail.base.scope.includes('8단계 개발과 최종 검사'));
  assert(p.detail.validation[0].scope.includes('시뮬레이터'));
  assert(p.detail.validation[0].scope.includes('복구는 실패'));
  assert(p.detail.validation[2].result.includes('실제 모델을 끈 상태'));
  assert(p.detail.limitations.some(t=>t.includes('위험 2건')));
  assert(p.detail.limitations.some(t=>t.includes('가동 시간 오차')));
  const assets=JSON.parse(await fs.readFile(new URL('../data/assets.json',import.meta.url),'utf8'));
  assert.equal(assets.flowmes.images.length,6);
  for(const im of assets.flowmes.images){
    assert(im.source.startsWith('https://raw.githubusercontent.com/MaoEmong/flowmes/'));
    assert(im.alt.includes('시연 데이터'));
    assert.equal(im.width,1440);
  }
});
