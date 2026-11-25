import {mkdir,cp,rm,writeFile} from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
const root=path.dirname(fileURLToPath(import.meta.url));
// dist is disposable build output: never retain files from an earlier build.
await rm(path.join(root,'dist'),{recursive:true,force:true});
await mkdir(path.join(root,'dist'),{recursive:true});
for(const file of ['index.html','styles.css','app.js','analytics.js']) await cp(path.join(root,'src',file),path.join(root,'dist',file));
for(const dir of ['data/clean','data/templates','models','content','reports']) await cp(path.join(root,dir),path.join(root,'dist',dir),{recursive:true});
await cp(path.join(root,'data/sentiment_corpus.csv'),path.join(root,'dist/data/sentiment_corpus.csv'));
await cp(path.join(root,'python/sentiment.py'),path.join(root,'dist','sentiment.py'));
await writeFile(path.join(root,'dist','_headers'),'/*\n  X-Content-Type-Options: nosniff\n  Referrer-Policy: no-referrer\n  X-Frame-Options: SAMEORIGIN\n');
console.log('Static build ready in dist/. No npm dependencies or API keys required.');
