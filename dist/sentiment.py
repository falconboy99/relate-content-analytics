"""Portable, inspectable English relatability classifier. No third-party dependencies.
Usage: python3 python/sentiment.py --text 'This is exactly me'
       python3 python/sentiment.py --input comments.csv --output tagged.csv
       python3 python/sentiment.py --train
"""
import argparse, csv, json, math, re, unicodedata
from collections import Counter
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parent if HERE.name == 'python' else HERE
LABELS = ['Neutral', 'Relatable']

def clean_text(text):
    text = unicodedata.normalize('NFKC', str(text)).replace('’', "'")
    text = re.sub(r'https?://\S+', '', text)
    return re.sub(r'\s+', ' ', text).strip()

def features(text):
    tokens = re.findall(r"[a-z]+(?:'[a-z]+)?", clean_text(text).lower())
    return tokens + [' '.join(tokens[i:i+2]) for i in range(len(tokens)-1)]

def train(rows):
    counts = {label: Counter() for label in LABELS}
    docs = Counter()
    for row in rows:
        docs[row['label']] += 1
        counts[row['label']].update(features(row['text']))
    vocab = sorted(set(counts['Neutral']) | set(counts['Relatable']))
    log_probs = {label:{word:math.log((counts[label][word]+1)/(sum(counts[label].values())+len(vocab))) for word in vocab} for label in LABELS}
    return {'version':'1.0.0', 'algorithm':'Multinomial naive Bayes, word unigrams + bigrams, Laplace alpha=1',
            'labels':LABELS, 'threshold':0.5, 'training_rows':len(rows), 'vocabulary_size':len(vocab),
            'log_prior':{label:math.log(docs[label]/len(rows)) for label in LABELS}, 'log_probs':log_probs,
            'scope':'English, author-labeled demonstration corpus. Scores are not calibrated probabilities.'}

def predict(text, model):
    fs = features(text)
    known = [word for word in fs if word in model['log_probs']['Neutral']]
    if not known:
        return {'label':'Neutral','score':0.5,'review':True,'reason':'No recognized English features'}
    scores = {label:model['log_prior'][label]+sum(model['log_probs'][label][word] for word in known) for label in LABELS}
    margin = scores['Relatable']-scores['Neutral']
    score = 1/(1+math.exp(-max(-700,min(700,margin))))
    label = 'Relatable' if score >= model['threshold'] else 'Neutral'
    evidence = sorted(set(known), key=lambda w:abs(model['log_probs']['Relatable'][w]-model['log_probs']['Neutral'][w]), reverse=True)[:4]
    review = abs(score-0.5)<0.2 or len(known)/max(1,len(fs))<0.35
    return {'label':label, 'score':round(score,6), 'review':review, 'reason':', '.join(evidence)}

def evaluate(rows, model):
    matrix = {a:{b:0 for b in LABELS} for a in LABELS}
    mistakes=[]
    for r in rows:
        p=predict(r['text'],model)['label']; matrix[r['label']][p]+=1
        if p != r['label']: mistakes.append({'text':r['text'],'expected':r['label'],'predicted':p})
    tp=matrix['Relatable']['Relatable']; fp=matrix['Neutral']['Relatable']; fn=matrix['Relatable']['Neutral']
    precision=tp/(tp+fp) if tp+fp else 0; recall=tp/(tp+fn) if tp+fn else 0
    return {'test_rows':len(rows),'accuracy':sum(matrix[l][l] for l in LABELS)/len(rows), 'precision':precision, 'recall':recall,
            'f1':2*precision*recall/(precision+recall) if precision+recall else 0,'confusion_matrix':matrix,'mistakes':mistakes,
            'evaluation_scope':'Frozen, separately authored demo holdout; not an independent real-world benchmark.'}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--text'); parser.add_argument('--input',type=Path); parser.add_argument('--output',type=Path)
    parser.add_argument('--train',action='store_true'); args=parser.parse_args()
    if args.train:
        rows=list(csv.DictReader((ROOT/'data/sentiment_corpus.csv').open()))
        train_rows=[r for r in rows if r['split']=='train']; test_rows=[r for r in rows if r['split']=='test']
        assert not set(clean_text(r['text']).lower() for r in train_rows) & set(clean_text(r['text']).lower() for r in test_rows)
        model=train(train_rows)
        (ROOT/'models/sentiment.json').write_text(json.dumps(model,indent=2))
        result=evaluate(test_rows,model); (ROOT/'models/evaluation.json').write_text(json.dumps(result,indent=2)); print(json.dumps(result,indent=2))
        return
    model=json.loads((ROOT/'models/sentiment.json').read_text())
    if args.text is not None: print(json.dumps(predict(args.text,model),indent=2))
    elif args.input and args.output:
        rows=list(csv.DictReader(args.input.open(encoding='utf-8-sig')))
        if not rows or 'text' not in rows[0]: parser.error('CSV must contain a text column and at least one row')
        out=[dict(r,**predict(r['text'],model)) for r in rows]
        with args.output.open('w',newline='',encoding='utf-8') as f:
            w=csv.DictWriter(f,fieldnames=list(out[0]));w.writeheader();w.writerows(out)
        print(f'Tagged {len(out)} comments: {args.output}')
    else: parser.error('Choose --train, --text, or --input with --output')
if __name__=='__main__': main()
