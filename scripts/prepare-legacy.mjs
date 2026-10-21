import fs from 'node:fs';
import path from 'node:path';
const source=path.resolve(process.argv[2]||'originals');
if(!fs.existsSync(path.join(source,'images')))throw Error('找不到旧站 images，不能发布以免旧图片丢失');
fs.mkdirSync('public/images',{recursive:true});fs.cpSync(path.join(source,'images'),'public/images',{recursive:true});
fs.mkdirSync('originals/images',{recursive:true});if(path.resolve(source,'images')!==path.resolve('originals/images'))fs.cpSync(path.join(source,'images'),'originals/images',{recursive:true});
if(fs.existsSync(path.join(source,'CNAME')))fs.copyFileSync(path.join(source,'CNAME'),'public/CNAME');
console.log('Preserved original images and existing CNAME if present.');
