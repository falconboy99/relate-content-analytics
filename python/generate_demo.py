"""Reproducible fictional campaign. Seeded assumptions are NOT real observations."""
import csv, json, random, textwrap, html
from datetime import date,timedelta
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
R=random.Random(42)
def write_csv(path,rows):
 with path.open('w',newline='',encoding='utf-8') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
ideas=[
('Social anxiety','The conversation after the conversation','Still replaying that one sentence?','You said hello. Your brain opened a review meeting.','Let one ordinary conversation stay ordinary.','What moment does your brain keep replaying?'),
('Social anxiety','The phone-call rehearsal','One call. Twelve practice runs.','The call takes thirty seconds. The rehearsal takes the afternoon.','You can start with: “Hi, I have a quick question.”','Do you rehearse the first sentence too?'),
('Burnout','Rest does not need a receipt','You do not have to earn a quiet evening.','Closing the laptop is easy. Closing the mental tabs takes longer.','Choose one small thing that can wait until tomorrow.','What is one thing you are letting wait?'),
('Burnout','The Sunday loading screen','Sunday evening, Monday in your head.','You are sitting on the sofa, already answering tomorrow’s emails.','Write tomorrow’s first task down. Give tonight back to yourself.','When does your weekend start feeling like work?'),
('Self comparison','A timeline of your own','Your life is not a delayed version of theirs.','One promotion post and suddenly your entire year feels too small.','Name one quiet thing you learned this month. That counts too.','What progress did nobody see?'),
('Self comparison','The highlight-reel spiral','Five minutes of scrolling. A whole new set of doubts.','You compare your ordinary Tuesday with everyone’s best day.','Put the phone down and return to one thing you actually enjoy.','What brings you back to your own life?'),
('Friendship','Friendship in calendar invites','“We should catch up” deserves a date.','You miss people you love while both of you are just trying to finish the week.','Try a ten-minute voice note instead of the perfect plan.','Who would you send a tiny life update to?'),
('Friendship','The low-battery friend','A slow reply can still hold a lot of love.','Sometimes you have the affection but not the energy for a conversation.','“Thinking of you. Low on energy. Replying properly soon.”','What makes staying in touch easier for you?'),
('Dating','The three-dot marathon','Typing. Deleting. Typing. Overthinking.','You rewrite one message until it no longer sounds like you.','A clear, kind sentence is allowed to be enough.','Have you ever edited a message into a different personality?'),
('Dating','Small honest signals','Connection can begin with a simple question.','Trying to look effortless can make an ordinary conversation feel like an audition.','Ask about something you are actually curious about.','What question gets you past small talk?'),
('Everyday life','The chair wardrobe','That chair has become a clothing ecosystem.','Clean enough to wear again. Not clean enough for the cupboard.','One small reset is still a reset. Start with the chair.','What is your home’s unofficial storage system?'),
('Everyday life','A small win still counts','Some days, the win is making lunch.','Your to-do list had ten things. You managed two and a glass of water.','Let a small finished thing be a finished thing.','What small win are you counting today?')]
colors=['#176a54','#d18761','#6a5a89','#5c7591','#bc6f7c','#a08a52']
series=[]; posts=[]; comments=[]
rel=['This is exactly what I go through after work','I have felt this way for so long','I do the same thing every week','You described my feelings so well','I feel so seen right now','I thought I was alone in this','This happens to me constantly','I relate to the feeling here','That is literally my experience','I needed this reminder today','We have the same life apparently','This made me feel less alone']
neutral=['Beautiful editing on this clip','What music is playing here?','Can you add captions please?','When will you post part two?','I do not relate to this at all','Interesting choice of colors','Where was the video filmed?','Please share the camera model','Thanks for posting this','The background audio is quiet','I disagree with this interpretation','I never feel like this']
for i,(topic,title,hook,setup,payoff,cta) in enumerate(ideas):
 cid=f'C{i+1:02}';color=colors[i//2]
 caption=f'{hook}\n\n{setup}\n\n{payoff}\n\n{cta}\n#SeenAndUnderstood #EverydayConnection'
 item={'id':cid,'topic':topic,'title':title,'hook_a':hook,'hook_b':f'POV: {setup}','setup':setup,'payoff':payoff,'cta':cta,'caption':caption,'duration_seconds':25,'asset':f'content/{cid}.svg','color':color,
 'script':[{'time':'0–3s','visual':'Close-up, direct eye contact. Hook as large on-screen type.','voiceover':hook},{'time':'3–11s','visual':'Cut to a familiar everyday setting. Hold on one small gesture.','voiceover':setup},{'time':'11–20s','visual':'Return to camera. Slow the pace and soften the delivery.','voiceover':payoff},{'time':'20–25s','visual':'End card with the question. Leave a beat for reflection.','voiceover':cta}],
 'experiment':'Compare text-first hook A with acted POV hook B. Keep the remaining 22 seconds, caption, duration, platform and observation window fixed.'}
 series.append(item)
 lines=textwrap.wrap(hook,width=23); svglines=''.join(f'<tspan x="84" dy="{0 if j==0 else 94}">{html.escape(s)}</tspan>' for j,s in enumerate(lines))
 sub=''.join(f'<tspan x="84" dy="{0 if j==0 else 44}">{html.escape(s)}</tspan>' for j,s in enumerate(textwrap.wrap(payoff,width=43)))
 svg=f'''<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="1350" viewBox="0 0 1080 1350"><rect width="1080" height="1350" fill="#f5f2e9"/><circle cx="930" cy="1080" r="325" fill="{color}" opacity=".12"/><circle cx="930" cy="1080" r="235" fill="none" stroke="{color}" stroke-width="2" opacity=".35"/><path d="M82 143h65m-32-32v64" stroke="{color}" stroke-width="7"/><text x="172" y="156" font-family="Arial,sans-serif" font-size="29" fill="{color}" letter-spacing="5">SEEN &amp; UNDERSTOOD</text><text x="84" y="300" font-family="Arial,sans-serif" font-size="24" fill="{color}" letter-spacing="4">{html.escape(topic.upper())}</text><text x="84" y="440" font-family="Georgia,serif" font-size="79" fill="#203d32">{svglines}</text><text x="84" y="{max(770,440+len(lines)*94+70)}" font-family="Arial,sans-serif" font-size="31" fill="#536158">{sub}</text><path d="M84 1170h912" stroke="#c9cfc3"/><text x="84" y="1233" font-family="Arial,sans-serif" font-size="23" fill="#536158">A little more understood. A little less alone.</text><text x="930" y="1233" font-family="Arial,sans-serif" font-size="23" fill="{color}">{cid}</text></svg>'''
 (ROOT/f'content/{cid}.svg').write_text(svg)
 base=[1.4,1.3,1.15,1.05,.88,.78][i//2]
 for v in ['A','B']:
  pid=f'P{i*2+(1 if v=="A" else 2):03}'
  dt=date(2026,10,1)+timedelta(days=i*3+(v=='B'))
  reach=int(R.uniform(5500,15000)*base*(1.12 if v=='B' else 1))
  views=int(reach*R.uniform(1.1,1.4)); likes=int(reach*R.uniform(.025,.055))
  shares=int(reach*R.uniform(.007,.02)*base*(1.12 if v=='B' else 1)); saves=int(reach*R.uniform(.009,.025)*base)
  n_comments=R.randint(40,90); followers=int(reach*R.uniform(.002,.005)*base)
  posts.append(dict(post_id=pid,content_id=cid,title=title,topic=topic,platform='Instagram' if i%2==0 else 'TikTok',published_at=dt.isoformat(),format='Short video',hook='Text-first' if v=='A' else 'Acted POV',variant=v,experiment_id=f'E{i+1:02}',duration_seconds=25,views=views,reach=reach,likes=likes,comments=n_comments,shares=shares,saves=saves,followers_gained=followers,retention_rate=round(R.uniform(.42,.75),4),observation_hours=168,source='synthetic_demo'))
  rate=[.82,.76,.70,.65,.55,.45][i//2]
  for j in range(30):
   t=R.choice(rel if R.random()<rate else neutral)
   comments.append(dict(comment_id=f'{pid}-{j+1:03}',post_id=pid,text=t,created_at=dt.isoformat(),source='synthetic_demo'))
raw_posts=posts+[dict(posts[0])];raw_comments=comments+[dict(comments[0]),dict(comments[1],comment_id='EMPTY',text='   ')]
raw_comments[2]['text']='  '+raw_comments[2]['text']+'   '
write_csv(ROOT/'data/raw/posts.csv',raw_posts);write_csv(ROOT/'data/raw/comments.csv',raw_comments)
trends=[]
for ti,topic in enumerate(dict.fromkeys(p['topic'] for p in posts)):
 for week in range(6):
  trends.append({'topic':topic,'week':(date(2026,9,28)+timedelta(days=7*week)).isoformat(),'index':round(min(100,30+ti*5+[6.8,4.8,3.8,2.1,1.3,-1.5][ti]*week+R.uniform(-3,3)),1),'source':'synthetic_demo'})
write_csv(ROOT/'data/raw/trends.csv',trends)
(ROOT/'content/series.json').write_text(json.dumps(series,indent=2,ensure_ascii=False))
print(f'Generated {len(posts)} fictional posts, {len(comments)} comments, {len(series)} original content pieces.')
