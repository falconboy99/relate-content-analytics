export const ratio=(a,b)=>b>0?a/b:null;
export const sum=(rows,key)=>rows.reduce((s,r)=>s+Number(r[key]||0),0);
export function cleanText(t){return String(t).normalize('NFKC').replaceAll('’',"'").replace(/https?:\/\/\S+/g,'').replace(/\s+/g,' ').trim()}
export function features(text){const w=cleanText(text).toLowerCase().match(/[a-z]+(?:'[a-z]+)?/g)||[];return [...w,...w.slice(0,-1).map((v,i)=>`${v} ${w[i+1]}`)]}
export function predict(text,model){
 const fs=features(text),known=fs.filter(w=>Object.hasOwn(model.log_probs.Neutral,w));
 if(!known.length)return {label:'Neutral',score:.5,review:true,reason:'No recognized English features'};
 const scoreFor=l=>model.log_prior[l]+known.reduce((s,w)=>s+model.log_probs[l][w],0);
 const score=1/(1+Math.exp(-Math.max(-700,Math.min(700,scoreFor('Relatable')-scoreFor('Neutral')))));
 const evidence=[...new Set(known)].sort((a,b)=>Math.abs(model.log_probs.Relatable[b]-model.log_probs.Neutral[b])-Math.abs(model.log_probs.Relatable[a]-model.log_probs.Neutral[a])).slice(0,4);
 return {label:score>=model.threshold?'Relatable':'Neutral',score:Math.round(score*1e6)/1e6,review:Math.abs(score-.5)<.2||known.length/fs.length<.35,reason:evidence.join(', ')};
}
export function metrics(posts,comments){const m={};for(const k of ['views','reach','likes','comments','shares','saves','followers_gained'])m[k]=sum(posts,k);
 m.actions=m.likes+m.comments+m.shares+m.saves;m.engagement=ratio(m.actions,m.reach);m.viral=ratio(100*(3*m.shares+2*m.saves+m.likes),m.reach);m.saveShare=ratio(m.saves,m.shares);m.shareRate=ratio(m.shares,m.reach);
 m.analyzed=comments.length;m.relatable=comments.filter(c=>c.label==='Relatable').length;m.relatableRate=ratio(m.relatable,m.analyzed);m.coverage=ratio(m.analyzed,m.comments);m.retention=ratio(posts.reduce((s,p)=>s+p.retention_rate*p.views,0),m.views);return m;
}
export function topicStats(posts,comments){return [...new Set(posts.map(p=>p.topic))].map(topic=>{const ps=posts.filter(p=>p.topic===topic),ids=new Set(ps.map(p=>p.post_id));return {topic,posts:ps.length,...metrics(ps,comments.filter(c=>ids.has(c.post_id)))}}).sort((a,b)=>(b.relatableRate??-1)-(a.relatableRate??-1))}
export function wilson(success,n){if(!n)return null;const z=1.96,p=success/n,den=1+z*z/n,center=(p+z*z/(2*n))/den,half=z*Math.sqrt(p*(1-p)/n+z*z/(4*n*n))/den;return [Math.max(0,center-half),Math.min(1,center+half)]}
export function experiments(posts){
 const pairs=[];
 for(const id of new Set(posts.map(p=>p.experiment_id).filter(Boolean))){const group=posts.filter(p=>p.experiment_id===id),a=group.filter(p=>p.variant==='A'),b=group.filter(p=>p.variant==='B');
  if(a.length!==1||b.length!==1)continue;
  const A=a[0],B=b[0];if(['topic','platform','format','duration_seconds','observation_hours','content_id'].some(k=>A[k]!==B[k])||!A.reach||!B.reach)continue;
  pairs.push({id,A,B,delta:B.shares/B.reach-A.shares/A.reach});
 }
 const n=pairs.length;if(!n)return {pairs,n:0,mean:null,p:null,interval:null};
 const diffs=pairs.map(p=>p.delta),mean=diffs.reduce((s,v)=>s+v,0)/n;
 let p=null,interval=null;
 if(n>=3){let seed=42;const rand=()=>{seed=(1664525*seed+1013904223)>>>0;return seed/4294967296};const exact=n<=16,permutations=exact?2**n:10000;let extreme=0;
  for(let i=0;i<permutations;i++){const v=diffs.reduce((s,d,j)=>s+d*(exact?(i&(1<<j)?1:-1):(rand()>.5?1:-1)),0)/n;if(Math.abs(v)>=Math.abs(mean)-1e-12)extreme++}
  p=exact?extreme/permutations:(extreme+1)/(permutations+1);
  const boots=Array.from({length:2000},()=>Array.from({length:n},()=>diffs[Math.floor(rand()*n)]).reduce((s,d)=>s+d,0)/n).sort((a,b)=>a-b);interval=[boots[50],boots[1949]];
 }
 return {pairs,n,mean,p,interval};
}
export function forecast(rows){
 const sorted=[...rows].sort((a,b)=>a.week.localeCompare(b.week));if(sorted.length<4)return null;
 const start=Date.parse(sorted[0].week),xs=sorted.map(r=>(Date.parse(r.week)-start)/86400000),ys=sorted.map(r=>r.index);
 function fit(x,y){const mx=x.reduce((a,b)=>a+b)/x.length,my=y.reduce((a,b)=>a+b)/y.length;const ss=x.reduce((s,v)=>s+(v-mx)**2,0);if(!ss)return null;const slope=x.reduce((s,v,i)=>s+(v-mx)*(y[i]-my),0)/ss;return {slope,intercept:my-slope*mx}}
 const fitAll=fit(xs,ys);if(!fitAll)return null;
 const f=fit(xs.slice(0,-1),ys.slice(0,-1));const error=f?Math.abs(f.intercept+f.slope*xs.at(-1)-ys.at(-1)):null;
 return {latest:ys.at(-1),next:Math.max(0,Math.min(100,fitAll.intercept+fitAll.slope*(xs.at(-1)+7))),slope:fitAll.slope*7,error,date:new Date(Date.parse(sorted.at(-1).week)+7*86400000).toISOString().slice(0,10),rows:sorted};
}
export function parseCSV(text,{allowEmpty=false,required=[]}={}){
 const rows=[];let row=[],value='',quoted=false;const s=text.replace(/^\uFEFF/,'');
 for(let i=0;i<s.length;i++){const c=s[i];if(c==='"'){if(quoted&&s[i+1]==='"'){value+='"';i++}else if(quoted){quoted=false}else if(value===''){quoted=true}else throw Error('Unexpected quote in CSV')}
 else if(c===','&&!quoted){row.push(value);value=''}else if((c==='\n'||c==='\r')&&!quoted){if(c==='\r'&&s[i+1]==='\n')i++;row.push(value);if(row.some(v=>v!==''))rows.push(row);row=[];value=''}else value+=c}
 if(quoted)throw Error('Unclosed quote in CSV');row.push(value);if(row.some(v=>v!==''))rows.push(row);
 if(!rows.length||(!allowEmpty&&rows.length<2))throw Error('CSV needs a header and at least one data row');const header=rows.shift().map(h=>h.trim());if(new Set(header).size!==header.length)throw Error('Duplicate CSV headers');for(const key of required)if(!header.includes(key))throw Error('Missing CSV column: '+key);
 return rows.map((r,i)=>{if(r.length!==header.length)throw Error(`CSV row ${i+2}: expected ${header.length} columns`);return Object.fromEntries(header.map((h,j)=>[h,r[j]]))});
}
export function csvText(rows){if(!rows.length)return '';const keys=Object.keys(rows[0]);const escape=v=>{let s=String(v??'');if(/^[=+@\-\t\r]/.test(s)&&typeof v==='string')s="'"+s;return '"'+s.replaceAll('"','""')+'"'};return [keys,...rows.map(r=>keys.map(k=>r[k]))].map(r=>r.map(escape).join(',')).join('\r\n')}
export function validateBundle(input,model){
 if(!input||!Array.isArray(input.posts)||!input.posts.length||!Array.isArray(input.comments)||!Array.isArray(input.trends??[]))throw Error('Expected posts (nonempty), comments and optional trends arrays');
 if(input.posts.length>10000||input.comments.length>50000)throw Error('Limit: 10,000 posts and 50,000 comments per import');
 const posts=[],comments=[],trends=[],seen=new Map(),cs=new Map(),ts=new Map(),audit={duplicate_posts:0,duplicate_comments:0,empty_comments:0,duplicate_trends:0};
 const str=(v)=>cleanText(v??'');
 const validDate=v=>/^\d{4}-\d{2}-\d{2}$/.test(v)&&Number.isFinite(Date.parse(v))&&new Date(v).toISOString().slice(0,10)===v;
 for(const [i,r] of input.posts.entries()){
  const p={};for(const k of ['post_id','content_id','title','topic','platform','published_at','format','hook','variant','experiment_id'])p[k]=str(r[k]);
  for(const k of ['post_id','title','topic','platform','published_at','format','hook'])if(!p[k])throw Error(`Post ${i+1}: missing ${k}`);
  if(!validDate(p.published_at))throw Error(`Post ${i+1}: use a valid YYYY-MM-DD date`);
  if(!['A','B',''].includes(p.variant)||Boolean(p.variant)!==Boolean(p.experiment_id))throw Error(`Post ${i+1}: variant A/B and experiment_id must be supplied together`);
  for(const k of ['duration_seconds','views','reach','likes','comments','shares','saves','followers_gained','observation_hours']){const v=Number(r[k]);if(r[k]===undefined||r[k]===null||String(r[k]).trim()===''||!Number.isSafeInteger(v)||v<0)throw Error(`Post ${i+1}: ${k} must be a nonnegative integer`);p[k]=v}
  p.retention_rate=Number(r.retention_rate);if(r.retention_rate===undefined||r.retention_rate===null||String(r.retention_rate).trim()===''||!Number.isFinite(p.retention_rate)||p.retention_rate<0||p.retention_rate>1)throw Error(`Post ${i+1}: retention_rate must be 0–1`);
  if(!p.observation_hours)throw Error(`Post ${i+1}: observation_hours must be positive`);
  p.source=input.meta?.source==='synthetic_demo'?'synthetic_demo':'user_import';
  if(seen.has(p.post_id)){if(JSON.stringify(seen.get(p.post_id))!==JSON.stringify(p))throw Error(`Conflicting duplicate post: ${p.post_id}`);audit.duplicate_posts++;continue}seen.set(p.post_id,p);posts.push(p);
 }
 for(const [i,r] of input.comments.entries()){
  const c={};for(const k of ['comment_id','post_id','text','created_at'])c[k]=str(r[k]);if(!c.text){audit.empty_comments++;continue}
  if(!c.comment_id||!seen.has(c.post_id))throw Error(`Comment ${i+1}: missing comment_id or unknown post_id`);
  if(!validDate(c.created_at))throw Error(`Comment ${i+1}: invalid created_at`);
  c.source=input.meta?.source==='synthetic_demo'?'synthetic_demo':'user_import';
  if(cs.has(c.comment_id)){if(JSON.stringify(cs.get(c.comment_id))!==JSON.stringify(c))throw Error(`Conflicting duplicate comment: ${c.comment_id}`);audit.duplicate_comments++;continue}
  cs.set(c.comment_id,{...c});comments.push({...c,...predict(c.text,model)});
 }
 for(const r of input.trends||[]){const t={topic:str(r.topic),week:str(r.week),index:Number(r.index),source:input.meta?.source==='synthetic_demo'?'synthetic_demo':'user_import'};
  if(!t.topic||!validDate(t.week)||r.index===null||r.index===undefined||String(r.index).trim()===''||!Number.isFinite(t.index)||t.index<0||t.index>100)throw Error('Each trend needs topic, valid week date and index 0–100');
  const key=t.topic+'|'+t.week;if(ts.has(key)){if(JSON.stringify(ts.get(key))!==JSON.stringify(t))throw Error('Conflicting trend: '+key);audit.duplicate_trends++;continue}ts.set(key,t);trends.push(t);
 }
 posts.sort((a,b)=>a.published_at.localeCompare(b.published_at)||a.post_id.localeCompare(b.post_id));
 return {meta:{schema_version:1,name:str(input.meta?.name||'Imported campaign'),source:input.meta?.source==='synthetic_demo'?'synthetic_demo':'user_import',cleaning:{...audit,posts:posts.length,comments:comments.length,trends:trends.length}},posts,comments,trends};
}
