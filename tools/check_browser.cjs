const assert=require('node:assert/strict');
const fs=require('node:fs/promises');
const path=require('node:path');
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'playwright');
const root=path.resolve(__dirname,'..');
const base=process.env.PREVIEW_URL||'http://127.0.0.1:10989';
(async()=>{
const data=JSON.parse(await fs.readFile(path.join(root,'.work/projects.json'),'utf8'));
const browser=await chromium.launch({headless:true});const context=await browser.newContext({viewport:{width:1440,height:1000}});const page=await context.newPage();
const errors=[];page.on('pageerror',e=>errors.push(e.message));
await page.goto(base,{waitUntil:'networkidle'});await page.locator('[data-project]').first().waitFor();
assert.equal(await page.locator('[data-project]').count(),data.length);
assert.equal(await page.locator('.project-row').first().getAttribute('href'),'/projects/ems/');
await page.screenshot({path:path.join(root,'.work/index-desktop.png')});
await page.locator('[data-filter="AI·검색"]').click();assert.equal(await page.locator('[data-project]:visible').count(),4);
await page.locator('#project-search').fill('does-not-exist-78201');await page.locator('.empty-state').waitFor({state:'visible'});
await page.locator('#reset-search').click();assert.equal(await page.locator('[data-project]:visible').count(),data.length);
await page.locator('#project-search').fill('SQLite');assert((await page.locator('[data-project]:visible').count())>0);assert((await page.locator('[data-project]:visible').count())<data.length);await page.locator('#project-search').fill('');
await page.locator('.project-row').first().click();assert.equal(new URL(page.url()).pathname,'/projects/ems/');
await page.screenshot({path:path.join(root,'.work/ems-desktop.png')});
await page.locator('[data-image]').first().click();assert(await page.locator('.image-dialog').evaluate(n=>n.open));await page.keyboard.press('Escape');assert(!(await page.locator('.image-dialog').evaluate(n=>n.open)));
const checks=[];
for(const viewport of [{width:1440,height:1000},{width:390,height:844}]){
 await page.setViewportSize(viewport);
 for(const p of data){
  await page.goto(base+`/projects/${p.id}/`,{waitUntil:'networkidle'});
  assert.equal(await page.locator('h1').textContent(),p.title);
  assert.equal(await page.locator('.repo-link>a').getAttribute('href'),p.github);
  assert(!(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth+1)),`${p.id} ${viewport.width} horizontal overflow`);
  const href=await page.locator('.case-actions a[download]').getAttribute('href');
  assert.equal(href,`/output/pdf/${p.id}-portfolio.pdf`);
  if(viewport.width===1440){const response=await page.request.get(base+href);assert.equal(response.status(),200);assert.equal((await response.body()).subarray(0,5).toString(),'%PDF-');}
  if(viewport.width===1440&&p.id==='commerce')await page.screenshot({path:path.join(root,'.work/commerce-desktop.png')});
  if(viewport.width===390&&['ems','pixel-office','ieum','commerce'].includes(p.id))await page.screenshot({path:path.join(root,`.work/${p.id}-mobile.png`)});
  checks.push({project:p.id,width:viewport.width,ok:true});
 }
}
await page.goto(base,{waitUntil:'networkidle'});await page.screenshot({path:path.join(root,'.work/index-mobile.png')});
await page.locator('.mobile-menu summary').click();await page.locator('.mobile-menu-panel a[href="/projects/pixel-office/"]').click();assert.equal(new URL(page.url()).pathname,'/projects/pixel-office/');
const noJs=await browser.newContext({javaScriptEnabled:false,viewport:{width:390,height:844}});const staticPage=await noJs.newPage();await staticPage.goto(base);assert.equal(await staticPage.locator('[data-project]').count(),data.length);await staticPage.locator('.project-row').first().click();assert.equal(new URL(staticPage.url()).pathname,'/projects/ems/');await noJs.close();
assert.deepEqual(errors,[]);
await fs.writeFile(path.join(root,'.work/browser-check.json'),JSON.stringify({base,checks,search:true,filters:true,imageDialog:true,mobileContents:true,withoutJavaScript:true,pageErrors:errors},null,2));
console.log(JSON.stringify({ok:true,responsiveProjectChecks:checks.length,pdfDownloads:data.length,search:true,filters:true,imageDialog:true,mobileContents:true,withoutJavaScript:true,pageErrors:0}));
await browser.close();
})().catch(e=>{console.error(e);process.exitCode=1;});
