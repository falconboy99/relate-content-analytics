import unittest,sys,json,csv,copy,tempfile,subprocess
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'python'))
from sentiment import ROOT,predict,clean_text
from pipeline import clean,read_csv,write_csv
class PipelineTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.model=json.loads((ROOT/'models/sentiment.json').read_text());cls.posts=read_csv(ROOT/'data/raw/posts.csv');cls.comments=read_csv(ROOT/'data/raw/comments.csv');cls.trends=read_csv(ROOT/'data/raw/trends.csv')
 def test_audit(self):
  d=clean(self.posts,self.comments,self.trends,'synthetic_demo',self.model)
  self.assertEqual(len(d['posts']),24);self.assertEqual(len(d['comments']),720);self.assertEqual(d['meta']['cleaning']['empty_comments'],1)
 def test_conflicting_duplicate(self):
  rows=copy.deepcopy(self.posts);rows[-1]['views']='1'
  with self.assertRaisesRegex(ValueError,'Conflicting duplicate'):clean(rows,self.comments,[],'user_import',self.model)
 def test_orphan(self):
  rows=copy.deepcopy(self.comments);rows[0]['post_id']='missing'
  with self.assertRaisesRegex(ValueError,'unknown post_id'):clean(self.posts,rows,[],'user_import',self.model)
 def test_missing_metrics(self):
  rows=copy.deepcopy(self.posts);rows[0]['shares']=''
  with self.assertRaisesRegex(ValueError,'must be a number'):clean(rows,[],[],'user_import',self.model)
 def test_empty_comments(self):
  d=clean(self.posts,[],[],'user_import',self.model);self.assertEqual(d['comments'],[])
 def test_train_test_disjoint(self):
  rows=read_csv(ROOT/'data/sentiment_corpus.csv');train={clean_text(r['text']).lower() for r in rows if r['split']=='train'};test={clean_text(r['text']).lower() for r in rows if r['split']=='test'}
  self.assertFalse(train&test);self.assertEqual(len(train),120);self.assertEqual(len(test),36)
 def test_url_unicode_cleanup(self):self.assertEqual(clean_text('  I’m  seen https://example.com  '),"I'm seen")
 def test_unknown_text(self):self.assertTrue(predict('🔥',self.model)['review'])
 def test_empty_export_replaces_stale_rows(self):
  with tempfile.TemporaryDirectory() as directory:
   path=Path(directory)/'comments.csv';path.write_text('comment_id,text\nold,stale data\n')
   write_csv(path,[],['comment_id','text'])
   self.assertEqual(path.read_text(),'comment_id,text\n');self.assertEqual(read_csv(path),[])
 def test_cli_does_not_keep_previous_campaign_exports(self):
  with tempfile.TemporaryDirectory() as directory:
   inp=Path(directory)/'input';out=Path(directory)/'output';inp.mkdir();out.mkdir()
   write_csv(inp/'posts.csv',self.posts)
   write_csv(inp/'comments.csv',[],['comment_id','post_id','text','created_at'])
   (out/'comments.csv').write_text('comment_id,text\nold,stale\n')
   (out/'trends.csv').write_text('topic,week,index\nold,2026-01-01,30\n')
   subprocess.run([sys.executable,str(ROOT/'python/pipeline.py'),'--input',str(inp),'--output',str(out),'--source','user_import'],check=True,capture_output=True)
   self.assertEqual(read_csv(out/'comments.csv'),[]);self.assertEqual(read_csv(out/'trends.csv'),[])
   bundle=json.loads((out/'dashboard.json').read_text());self.assertEqual(bundle['comments'],[]);self.assertEqual(bundle['trends'],[])

if __name__=='__main__':unittest.main()
