"""Validate and clean export CSVs; classify comments; build the dashboard dataset.
python3 python/pipeline.py --input data/raw --output data/clean --source synthetic_demo
For real exports, use --source user_import and preserve the documented CSV schema.
"""
import argparse,csv,json,math
from pathlib import Path
from datetime import date
from sentiment import clean_text,predict,ROOT
COUNTS=['duration_seconds','views','reach','likes','comments','shares','saves','followers_gained','observation_hours']
STRINGS=['post_id','content_id','title','topic','platform','published_at','format','hook','variant','experiment_id']

def read_csv(path):
 with path.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def write_csv(path,rows,fieldnames=None):
 # Always replace the export, even when a new campaign has zero records.
 columns=fieldnames or (list(rows[0]) if rows else None)
 if not columns:raise ValueError('An empty export requires explicit columns')
 with path.open('w',encoding='utf-8',newline='') as f:
  w=csv.DictWriter(f,fieldnames=columns);w.writeheader();w.writerows(rows)
def valid_date(value):
 if len(value)!=10 or date.fromisoformat(value).isoformat()!=value:raise ValueError(f'Invalid ISO date: {value}')
def clean(raw_posts,raw_comments,raw_trends,source,model):
 posts=[];comments=[];trends=[];seen={};cs={};ts={};audit={'duplicate_posts':0,'duplicate_comments':0,'empty_comments':0,'duplicate_trends':0}
 for n,row in enumerate(raw_posts,2):
  p={k:clean_text(row.get(k,'')) for k in STRINGS}
  if not all(p[k] for k in ['post_id','title','topic','platform','published_at','format','hook']):raise ValueError(f'posts row {n}: missing required text')
  valid_date(p['published_at'])
  if p['variant'] not in ['A','B','']:raise ValueError(f'posts row {n}: variant must be A, B or blank')
  if bool(p['variant'])!=bool(p['experiment_id']):raise ValueError(f'posts row {n}: variant and experiment_id must both be set or both blank')
  for key in COUNTS:
   try:v=float(row[key])
   except (ValueError,KeyError,TypeError):raise ValueError(f'posts row {n}: {key} must be a number; missing values are not zero')
   if not math.isfinite(v) or v<0 or int(v)!=v:raise ValueError(f'posts row {n}: invalid nonnegative integer {key}')
   p[key]=int(v)
  p['retention_rate']=float(row['retention_rate'])
  if not math.isfinite(p['retention_rate']) or not 0<=p['retention_rate']<=1:raise ValueError('retention_rate must be in [0,1]')
  if p['observation_hours']==0:raise ValueError('observation_hours must be positive')
  p['source']=source
  if p['post_id'] in seen:
   if seen[p['post_id']]!=p:raise ValueError(f'Conflicting duplicate post {p["post_id"]}')
   audit['duplicate_posts']+=1;continue
  seen[p['post_id']]=p;posts.append(p)
 if not posts:raise ValueError('At least one valid post is required')
 for n,row in enumerate(raw_comments,2):
  c={k:clean_text(row.get(k,'')) for k in ['comment_id','post_id','text','created_at']}
  if not c['text']:audit['empty_comments']+=1;continue
  if not c['comment_id'] or c['post_id'] not in seen:raise ValueError(f'comments row {n}: missing ID or unknown post_id')
  valid_date(c['created_at']);c['source']=source
  if c['comment_id'] in cs:
   if cs[c['comment_id']]!=c:raise ValueError(f'Conflicting duplicate comment {c["comment_id"]}')
   audit['duplicate_comments']+=1;continue
  cs[c['comment_id']]=dict(c);c.update(predict(c['text'],model));comments.append(c)
 for row in raw_trends:
  t={k:clean_text(row.get(k,'')) for k in ['topic','week']};valid_date(t['week']);t['index']=float(row['index']);t['source']=source
  if not t['topic'] or not math.isfinite(t['index']) or not 0<=t['index']<=100:raise ValueError('Trend topic and index [0,100] required')
  key=(t['topic'],t['week'])
  if key in ts:
   if ts[key]!=t:raise ValueError(f'Conflicting trend {key}')
   audit['duplicate_trends']+=1;continue
  ts[key]=t;trends.append(t)
 posts.sort(key=lambda p:(p['published_at'],p['post_id']));trends.sort(key=lambda t:(t['topic'],t['week']))
 audit.update(posts=len(posts),comments=len(comments),trends=len(trends),source=source)
 return {'meta':{'schema_version':1,'name':'Seen & Understood' if source=='synthetic_demo' else 'Imported campaign','source':source,'description':'Fictional seeded campaign; no real users or published results.' if source=='synthetic_demo' else 'User-supplied exports. Verify source and measurement definitions.','cleaning':audit},'posts':posts,'comments':comments,'trends':trends}

def summary(data):
 out=[]
 for topic in sorted(set(p['topic'] for p in data['posts'])):
  ps=[p for p in data['posts'] if p['topic']==topic];ids={p['post_id'] for p in ps};cs=[c for c in data['comments'] if c['post_id'] in ids]
  totals={k:sum(p[k] for p in ps) for k in ['views','reach','likes','shares','saves','comments','followers_gained']}
  def ratio(a,b):return a/b if b else None
  out.append(dict(topic=topic,posts=len(ps),**totals,analyzed_comments=len(cs),relatable=sum(c['label']=='Relatable' for c in cs),relatable_rate=ratio(sum(c['label']=='Relatable' for c in cs),len(cs)),engagement_rate=ratio(sum(totals[k] for k in ['likes','comments','shares','saves']),totals['reach']),viral_score=ratio(100*(3*totals['shares']+2*totals['saves']+totals['likes']),totals['reach']),save_share_ratio=ratio(totals['saves'],totals['shares'])))
 return sorted(out,key=lambda x:x['relatable_rate'] or 0,reverse=True)
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--input',type=Path,default=ROOT/'data/raw');ap.add_argument('--output',type=Path,default=ROOT/'data/clean');ap.add_argument('--source',choices=['synthetic_demo','user_import'],default='user_import');args=ap.parse_args()
 model=json.loads((ROOT/'models/sentiment.json').read_text());trend=args.input/'trends.csv'
 data=clean(read_csv(args.input/'posts.csv'),read_csv(args.input/'comments.csv'),read_csv(trend) if trend.exists() else [],args.source,model)
 args.output.mkdir(parents=True,exist_ok=True)
 empty_columns={'comments':['comment_id','post_id','text','created_at','source','label','score','review','reason'],'trends':['topic','week','index','source']}
 for key in ['posts','comments','trends']:write_csv(args.output/f'{key}.csv',data[key],empty_columns.get(key))
 (args.output/'dashboard.json').write_text(json.dumps(data,indent=2,ensure_ascii=False))
 (args.output/'audit.json').write_text(json.dumps(data['meta']['cleaning'],indent=2))
 write_csv(args.output/'topic_summary.csv',summary(data));print(json.dumps(data['meta']['cleaning'],indent=2))
if __name__=='__main__':main()
