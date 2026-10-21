import fs from 'node:fs';
import path from 'node:path';
const tree=JSON.parse(fs.readFileSync('legacy/legacy-tree.json','utf8'));
const files=tree.tree.filter(f=>f.type==='blob'&&f.path.startsWith('images/'));
let failed=0,downloaded=0;
for(const file of files){const target=path.join('originals',file.path);if(fs.existsSync(target)&&fs.statSync(target).size===file.size)continue;try{const response=await fetch(`https://raw.githubusercontent.com/xuepeiyao/xuepeiyao.github.io/${tree.sha}/${file.path}`,{signal:AbortSignal.timeout(30000)});if(!response.ok)throw Error('HTTP '+response.status);const data=Buffer.from(await response.arrayBuffer());if(data.length!==file.size)throw Error('文件大小不符');fs.mkdirSync(path.dirname(target),{recursive:true});fs.writeFileSync(target,data);downloaded++;}catch(err){failed++;console.error(file.path,err.message);if(failed>=3)break;}}
console.log({downloaded,failed});if(failed)process.exitCode=1;
