// Optional: npm install --no-save sharp, then node python/render_cards.mjs
// Supply SHARP_MODULE only to use a separately installed runtime package.
import {readFile,mkdir,writeFile} from 'node:fs/promises';
const {default:sharp}=await import(process.env.SHARP_MODULE||'sharp');
const root=new URL('../',import.meta.url),series=JSON.parse(await readFile(new URL('content/series.json',root)));
await mkdir(new URL('content/png/',root),{recursive:true});
for(const item of series){const svg=await readFile(new URL(item.asset,root));const png=await sharp(svg).png().toBuffer();await writeFile(new URL('content/png/'+item.id+'.png',root),png)}
console.log(`Rendered ${series.length} original vector cards to 1080 x 1350 PNG.`);
