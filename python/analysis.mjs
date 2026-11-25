import {readFile,writeFile} from 'node:fs/promises';
import {experiments,metrics,topicStats,forecast} from '../src/analytics.js';
const root=new URL('../',import.meta.url),data=JSON.parse(await readFile(new URL('data/clean/dashboard.json',root),'utf8'));
const xs=data.posts.map(p=>metrics([p],data.comments.filter(c=>c.post_id===p.post_id)).relatableRate),ys=data.posts.map(p=>p.followers_gained),mx=xs.reduce((s,v)=>s+v)/xs.length,my=ys.reduce((s,v)=>s+v)/ys.length;
const correlation=xs.reduce((s,v,i)=>s+(v-mx)*(ys[i]-my),0)/Math.sqrt(xs.reduce((s,v)=>s+(v-mx)**2,0)*ys.reduce((s,v)=>s+(v-my)**2,0));
const exp=experiments(data.posts);const result={metrics:metrics(data.posts,data.comments),topics:topicStats(data.posts,data.comments),experiment:{n:exp.n,mean:exp.mean,p:exp.p,interval:exp.interval},correlation,trends:[...new Set(data.trends.map(t=>t.topic))].map(topic=>({topic,...forecast(data.trends.filter(t=>t.topic===topic))}))};
await writeFile(new URL('reports/analysis.json',root),JSON.stringify(result,null,2));console.log(JSON.stringify({experiment:result.experiment,correlation},null,2));
