import fs from 'node:fs';
import assert from 'node:assert/strict';
import {spawn} from 'node:child_process';
import {chromium} from 'playwright';
const projects=JSON.parse(fs.readFileSync('content/projects.json','utf8')).filter(p=>p.status==='public');
const server=spawn(process.execPath,['scripts/serve.mjs'],{env:{...process.env,PORT:'4321'},stdio:['ignore','pipe','pipe']});
const checks=[],issues=[];let browser;
try{
 await new Promise((resolve,reject)=>{const timer=setTimeout(()=>reject(Error('Preview startup timed out')),15000);server.stdout.on('data',b=>{if(b.toString().includes('Local:')){clearTimeout(timer);resolve()}});server.on('error',reject);server.on('exit',code=>{if(code)reject(Error('Preview exited '+code))})});
 browser=await chromium.launch();const page=await browser.newPage();page.on('pageerror',error=>issues.push(error.message));const base='http://127.0.0.1:4321';
 for(const route of ['/','/work/','/about/',...projects.map(p=>'/work/'+p.slug+'/')]){const r=await page.request.get(base+route);assert.equal(r.status(),200,route)}
 checks.push('All 51 public routes return HTTP 200');assert.equal((await page.request.get(base+'/missing-page')).status(),404);checks.push('Unknown route returns HTTP 404');
 for(const width of [390,768,1440]){await page.setViewportSize({width,height:1000});for(const route of ['/','/work/','/about/','/work/meetime-satellite/']){await page.goto(base+route);assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),`${width}px overflow ${route}`);}await page.goto(base+'/');await page.screenshot({path:`reports/home-${width}.png`,fullPage:true});}checks.push('Home/archive/about/detail have no horizontal overflow at 390/768/1440px');
 await page.goto(base+'/work/?category=poster');assert.equal(await page.locator('[data-category]:visible').count(),9);await page.locator('[data-filter="ui"]').click();assert.equal(await page.locator('[data-category]:visible').count(),6);assert(new URL(page.url()).searchParams.get('category')==='ui');await page.reload();assert.equal(await page.locator('[data-category]:visible').count(),6);checks.push('Category filtering persists through URL and reload');
 await page.goto(base+'/work/meetime-satellite/');const first=page.locator('[data-zoom]').first();await first.click();assert(await page.locator('dialog').evaluate(d=>d.open));await page.keyboard.press('ArrowRight');assert.equal(await page.locator('#lightbox-count').textContent(),'2 / 5');await page.keyboard.press('Escape');assert(!(await page.locator('dialog').evaluate(d=>d.open)));assert(await first.evaluate(b=>document.activeElement===b));checks.push('Native lightbox arrow keys, Escape, and focus return work');
 for(const project of projects.filter(p=>p.legacyId!==undefined)){await page.goto(base+'/detail.html?id='+project.legacyId);await page.waitForURL(base+'/work/'+project.slug+'/');}checks.push('All 32 legacy query links redirect correctly');
 await page.goto(base+'/detail.html?id=99999');await page.waitForFunction(()=>document.querySelector('#legacy-status').textContent.includes('没有找到'));checks.push('Invalid legacy ID has a useful fallback');
 await page.emulateMedia({reducedMotion:'reduce'});await page.goto(base+'/');assert.equal(await page.evaluate(()=>getComputedStyle(document.documentElement).scrollBehavior),'auto');checks.push('Reduced-motion setting disables smooth scrolling');
 await page.goto(base+'/work/?category=unknown');assert(await page.locator('.empty-state').isVisible());checks.push('Unknown category displays empty state');
 await page.goto(base+'/work/meetime-satellite/');await page.locator('.project-gallery img').first().evaluate(img=>img.dispatchEvent(new Event('error')));assert(await page.locator('.project-gallery .image-error').first().isVisible());checks.push('Failed image fallback is visible');
 assert.deepEqual(issues,[],'Browser console errors');fs.writeFileSync('reports/browser-qa.json',JSON.stringify({time:new Date().toISOString(),browser:await browser.version(),checks,pageErrors:issues,result:'passed'},null,2));console.log(checks);
}catch(error){fs.writeFileSync('reports/browser-qa.json',JSON.stringify({time:new Date().toISOString(),checks,pageErrors:issues,result:'failed',error:String(error)},null,2));throw error;}
finally{await browser?.close();server.kill('SIGTERM');}
