import fs from 'node:fs';
export function validate(projects,profile){
 const slugs=new Set(),ids=new Set();const cats=['communication','ui','web','poster','illustration'];
 const asset=s=>typeof s==='string'&&/^(images|media)\/[a-zA-Z0-9_./-]+$/.test(s)&&!s.split('/').includes('..');
 for(const p of projects){
  if(!p.title||!/^[a-z0-9]+(-[a-z0-9]+)*$/.test(p.slug)||slugs.has(p.slug))throw Error('Invalid/duplicate slug '+p.slug);slugs.add(p.slug);
  if(!cats.includes(p.category)||!['draft','hidden','public'].includes(p.status)||!Number.isFinite(p.order)||typeof p.featured!=='boolean')throw Error('Invalid project data '+p.slug);
  if(!Array.isArray(p.tags)||p.tags.some(t=>typeof t!=='string')||!Array.isArray(p.media))throw Error('Invalid tags/media '+p.slug);
  if(p.status==='public'&&(!asset(p.cover)||!p.media.length))throw Error('Public project needs cover and media '+p.slug);
  for(const m of p.media)if(!asset(m.src)||!m.alt||typeof m.caption!=='string')throw Error('Invalid media '+p.slug);
  for(const key of ['summary','role','client','background','goal','process','outcome'])if(typeof p[key]!=='string')throw Error('Invalid '+key+' '+p.slug);
  if(p.year!==null&&!/^\d{4}$/.test(String(p.year)))throw Error('Invalid year '+p.slug);
  if(p.legacyId!==undefined){if(ids.has(p.legacyId)||!Number.isInteger(p.legacyId))throw Error('Duplicate legacy ID');ids.add(p.legacyId);}
 }
 for(let i=0;i<32;i++)if(!projects.some(p=>p.legacyId===i&&p.status==='public'))throw Error('Missing legacy public project '+i);
 for(const c of profile.contacts)if(!/^(https:\/\/|mailto:|tel:)/.test(c.url)||!c.label)throw Error('Invalid contact');
 if(profile.resume&&!/^\/[a-zA-Z0-9_./-]+\.pdf$/.test(profile.resume))throw Error('Invalid resume path');
 const meta=JSON.parse(fs.readFileSync('content/image-meta.json','utf8'));
 for(const p of projects.filter(p=>p.status==='public'&&p.source==='provided'))for(const src of [p.cover,...p.media.map(m=>m.src)]){if(!meta[src])throw Error('Missing optimized image '+src);for(const v of meta[src].variants)for(const f of ['jpeg','avif','webp'])if(!fs.existsSync('public'+v[f]))throw Error('Missing '+v[f]);}
}
