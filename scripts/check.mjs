import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
import {validate} from './validate.mjs';
const projects=JSON.parse(fs.readFileSync('content/projects.json','utf8'));const profile=JSON.parse(fs.readFileSync('content/profile.json','utf8'));validate(projects,profile);
const published=projects.filter(p=>p.status==='public');const map=JSON.parse(fs.readFileSync('dist/legacy-map.json','utf8'));
let pages=0,refs=0;const externalImages=new Set();
function walk(dir){for(const entry of fs.readdirSync(dir,{withFileTypes:true})){const file=path.join(dir,entry.name);if(entry.isDirectory())walk(file);else if(file.endsWith('.html')){pages++;const html=fs.readFileSync(file,'utf8');assert.match(html,/<h1[ >]/);assert.equal((html.match(/<h1[ >]/g)||[]).length,1);assert.match(html,/<title>[^<]+<\/title>/);assert.match(html,/<meta name="description" content="[^"]+"/);assert.match(html,/<link rel="canonical"/);assert(!html.includes('href="#"'));for(const [,url] of html.matchAll(/(?:href|src)="([^"]+)"/g)){if(url.startsWith('https://xuepeiyao.github.io/images/'))externalImages.add(url);if(!url.startsWith('/')||url.startsWith('//'))continue;const clean=url.split(/[?#]/)[0];const asset=path.join('dist',clean);assert(fs.existsSync(asset),`${file} broken reference ${url}`);refs++;}}}}
walk('dist');for(const p of published){assert(fs.existsSync(`dist/work/${p.slug}/index.html`));if(p.legacyId!==undefined)assert.equal(map[p.legacyId],p.slug);}
assert.equal(Object.keys(map).length,32);const sitemap=fs.readFileSync('dist/sitemap.xml','utf8');assert.equal((sitemap.match(/<url>/g)||[]).length,published.length+3);
if(process.env.AGNES_REQUIRE_LOCAL_MEDIA==='1'){assert(fs.existsSync('dist/images'),'正式发布必须带入旧站 images');assert.equal(externalImages.size,0,'正式发布不能依赖旧站外链图片');}
const report={time:new Date().toISOString(),pages,localReferencesChecked:refs,legacyLinks:32,publishedProjects:published.length,remoteLegacyImageReferences:externalImages.size,localLegacyImagesAvailable:fs.existsSync('dist/images'),result:'passed',limits:['静态构建与数据检查通过；远程旧图可用性未通过网络验证。','浏览器交互与断点检查另见 verification.md。']};fs.writeFileSync('reports/checks.json',JSON.stringify(report,null,2)+'\n');console.log(report);
