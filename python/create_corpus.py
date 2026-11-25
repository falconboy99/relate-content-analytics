"""Authored English examples. Fixed splits; never tuned on campaign comments."""
import csv
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
train_rel='''This is exactly me
I feel so seen by this
I thought I was the only one
This happens to me every day
I do this all the time
You described my life perfectly
I relate to this so much
Same here every single week
This is literally my life
I have been there too
I needed to hear this today
I struggle with this as well
This makes me feel less alone
I feel understood for once
This hit home for me
I always overthink my messages too
My friends and I do this
I experience the same thing
I keep comparing myself to others
I also feel behind in life
I feel guilty when I take a break
I get nervous before making calls
I am afraid of being judged too
I rehearse conversations in my head
I have felt this for years
I am going through this right now
That is so relatable
So true for me
It feels like you know me
You put my feelings into words
This could have been written about me
I do the exact same thing
We are living the same life
Glad I am not alone in this
I cried because this is my experience
I have this problem every Monday
I am exhausted from pretending too
I feel this in my soul
Yes this is what I deal with
That awkward moment is familiar
This reminds me of my own experience
My life in one video
It is comforting to know others feel this
I have never felt more understood
Same problem here
I can relate to the feeling
This speaks to me personally
I understand because I have lived it
I know exactly how this feels
This is me after every meeting
I save these because they help me feel seen
I share this struggle
I cannot stop doing this either
I thought it was just me
I feel the same anxiety
I have experienced that loneliness
This captures my everyday struggle
Someone finally said what I feel
I needed this reminder for myself
This is my situation right now'''.splitlines()
train_neu='''Nice video
What camera do you use
When is the next episode
Please add subtitles
I like the editing
The music sounds great
Where was this filmed
What is the song called
Thanks for sharing
Good production quality
Interesting topic
Can you post the link
How long did this take to make
The colors are beautiful
That transition was smooth
I do not relate to this
This is not my experience
I never feel this way
This does not describe my life
I cannot relate at all
Not everyone feels like this
I disagree with this message
This feels exaggerated
This is not true for me
That has never happened to me
What time do you upload
Can you make a tutorial
First comment
Looking forward to part two
The sound is too quiet
This looks professionally made
Your typography is nice
Which app did you use
I prefer the previous video
That is a broad generalization
There is no evidence for this claim
I do not understand the point
Please explain the last sentence
The video froze halfway through
I would like more context
The background is distracting
Is this available in another language
The caption has a typo
Great lighting in this shot
Where can I find the full version
That is an interesting perspective
I am here for the soundtrack
Please credit the artist
What font is this
A useful topic for discussion
I am not the target audience
This is unrelated to me
No personal connection here
I feel differently about it
This is not relatable to me
I cannot see myself in this
I do not experience this problem
Neutral on this topic
This has nothing to do with my life
The content is okay'''.splitlines()
test_rel='''You just described what I go through
I feel understood watching this clip
I struggle with that feeling every evening
I thought only I had this problem
That is my entire week in a sentence
I rehearse my order before reaching the counter too
Same here and it makes me feel less alone
This video captured my life so well
I needed this because I am exhausted
I also compare my progress with friends
I have been in that situation before
Finally someone understands how I feel
This is painfully familiar to me
I felt seen for the first time today
My brain does exactly this
I deal with the same thing at work
You have put words to my experience
This reminds me that I am not alone'''.splitlines()
test_neu='''Could you name the background track
The lighting and color choices look lovely
I disagree with the main point
I do not relate to your story
This has never been a problem for me
Please share your editing software
When will the next part come out
The subtitles are hard to read
This is not how I experience life
Can we get a longer version
This does not resonate with me
I am interested in the camera settings
I never struggle with this issue
The last frame has a spelling mistake
Where can I download this music
Nice work on the animation
Not my situation at all
I think this is overstated'''.splitlines()
with (ROOT/'data/sentiment_corpus.csv').open('w',newline='') as f:
 w=csv.writer(f);w.writerow(['id','text','label','split','source'])
 n=0
 for split,label,items in [('train','Relatable',train_rel),('train','Neutral',train_neu),('test','Relatable',test_rel),('test','Neutral',test_neu)]:
  for t in items:
   n+=1;w.writerow([f'L{n:03}',t,label,split,'author_labeled_demo'])
