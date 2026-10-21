import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import sharp from 'sharp';
import os from 'node:os';
const sourceRoot=process.env.AGNES_ASSETS||path.join(os.homedir(),'Documents/作品');
const legacyOnly=process.argv.includes('--legacy-only');
const manifest=legacyOnly?[]:JSON.parse(fs.readFileSync('content/media-sources.json','utf8'));
const projects=JSON.parse(fs.readFileSync('content/projects.json','utf8'));
for(const p of projects.filter(p=>p.source==='legacy'))for(const src of new Set([p.cover,...p.media.map(m=>m.src)])){const original=path.join('originals',src);if(fs.existsSync(original))manifest.push({original,src});}
const meta=fs.existsSync('content/image-meta.json')?JSON.parse(fs.readFileSync('content/image-meta.json','utf8')):{};const report=[];
for(const entry of manifest){
 const {src}=entry;const original=path.isAbsolute(entry.original)?entry.original:path.join(sourceRoot,entry.original);
 const stat=fs.statSync(original);const info=await sharp(original,{animated:true,limitInputPixels:300000000}).metadata();
 if(info.pages>1){const target=path.join('public',src);fs.mkdirSync(path.dirname(target),{recursive:true});fs.copyFileSync(original,target);meta[src]={width:info.width,height:info.pageHeight||info.height,original:'/'+src,variants:[],animated:true};report.push({src,originalBytes:stat.size,generatedBytes:stat.size,animated:true});continue;}
 const hash=crypto.createHash('sha256').update(fs.readFileSync(original)).digest('hex').slice(0,12);const variants=[];
 const widths=[...new Set([480,768,1200,1600].filter(w=>w<info.width).concat(Math.min(1600,info.width)))];
 for(const width of widths){const item={width,height:Math.round(info.height*width/info.width)};
 for(const format of ['avif','webp','jpeg']){const dest=`media/optimized/${hash}-${width}.${format==='jpeg'?'jpg':format}`;fs.mkdirSync(path.dirname('public/'+dest),{recursive:true});if(!fs.existsSync('public/'+dest)){let image=sharp(original,{limitInputPixels:300000000}).rotate().resize({width,withoutEnlargement:true});image=format==='avif'?image.avif({quality:60,effort:3}):format==='webp'?image.webp({quality:85}):image.flatten({background:'#f4f3ef'}).jpeg({quality:88,mozjpeg:true});await image.toFile('public/'+dest);}item[format]='/'+dest;}
 variants.push(item);}
 meta[src]={width:info.width,height:info.height,variants};report.push({src,originalBytes:stat.size,generatedBytes:variants.reduce((sum,v)=>sum+['avif','webp','jpeg'].reduce((n,f)=>n+fs.statSync('public'+v[f]).size,0),0),thumbnailWebpBytes:fs.statSync('public'+variants[0].webp).size,detailWebpBytes:fs.statSync('public'+variants.at(-1).webp).size});
}
fs.writeFileSync('content/image-meta.json',JSON.stringify(meta,null,2)+'\n');fs.writeFileSync('reports/images.json',JSON.stringify({date:new Date().toISOString(),count:report.length,originalBytes:report.reduce((n,r)=>n+r.originalBytes,0),generatedBytes:report.reduce((n,r)=>n+r.generatedBytes,0),files:report},null,2)+'\n');console.log(`Optimized ${report.length} originals`);
