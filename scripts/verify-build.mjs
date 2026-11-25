import assert from 'node:assert/strict';
import {readFile, readdir, stat} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
import {validateBundle, metrics} from '../src/analytics.js';

const root = fileURLToPath(new URL('../', import.meta.url));
const dist = path.join(root, 'dist');
const read = name => readFile(path.join(dist, name));
const json = async name => JSON.parse(await read(name));
async function walk(dir, prefix = '') {
  const files = [];
  for (const item of await readdir(dir, {withFileTypes:true})) {
    const relative = path.join(prefix, item.name);
    if (item.isDirectory()) files.push(...await walk(path.join(dir,item.name),relative));
    else files.push(relative);
  }
  return files;
}
for (const name of ['index.html','styles.css','app.js','analytics.js']) {
  assert.deepEqual(await read(name), await readFile(path.join(root,'src',name)), `${name}: stale build`);
}
for (const directory of ['data/clean','data/templates','models','content','reports']) {
  for (const name of await walk(path.join(root,directory))) {
    const relative = path.join(directory,name);
    assert.deepEqual(await read(relative), await readFile(path.join(root,relative)), `${relative}: stale build`);
  }
}
const data = await json('data/clean/dashboard.json');
const model = await json('models/sentiment.json');
const clean = validateBundle(data,model);
assert.deepEqual(metrics(clean.posts,clean.comments),metrics(data.posts,data.comments),'Data/model mismatch');
for (const name of ['strategy-report.pdf','content-series.pdf']) {
  assert.equal((await read('reports/'+name)).subarray(0,5).toString(),'%PDF-',`Invalid PDF: ${name}`);
}
const series = await json('content/series.json');
assert.equal(series.length,12,'The original creative series should contain 12 concepts');
for (const item of series) {
  assert.ok((await read(item.asset)).toString().includes('<svg'),'Missing SVG');
  const png=await read('content/png/'+item.id+'.png');
  assert.equal(png.readUInt32BE(16),1080,'Incorrect card width');
  assert.equal(png.readUInt32BE(20),1350,'Incorrect card height');
}
for (const name of await walk(dist)) {
  assert.ok(!name.split(path.sep).some(p=>['.git','node_modules','__pycache__'].includes(p)),`Unexpected build file ${name}`);
  assert.ok(!path.basename(name).startsWith('.env'),`Environment file in build: ${name}`);
  assert.ok((await stat(path.join(dist,name))).size>0,`Empty build file: ${name}`);
}
console.log(`Verified deployment: ${clean.posts.length} posts, ${clean.comments.length} comments, ${series.length} creative assets, PDFs and source parity.`);
