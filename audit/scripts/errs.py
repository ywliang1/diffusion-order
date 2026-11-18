import json,sys,collections
sys.path.insert(0,'/data/rbg/users/linrui/llada')
from phase1.tasks import make_source
B='/data/rbg/users/linrui/llada/results/phase1/'
for m in ['llada','dream']:
    words=json.loads(open(B+f'words-{m}.json').read())
    rows=[json.loads(l) for l in open(B+f'traces/{m}-exp2.jsonl')]
    for cond in ['Direct','Shared-path','Separate-path']:
     for o in ['A-first','B-first','CF']:
      c=collections.Counter(); n=0
      for r in rows:
        if r['condition']!=cond or r['order_or_branch']!=o: continue
        n+=1
        if r['B_correct']: c['correct']+=1; continue
        s=make_source(r['table_size'],r['source_id'],words,1729); t=s['rows'][s['target']]; p=r['predicted_B'].strip()
        lab=None
        for k in 'AHBCDE':
          if p==t[k]: lab='target.'+k; break
        if not lab:
          for k in 'AHBCDE':
            if any(p==x[k] for x in s['rows']): lab='other.'+k; break
        if not lab: lab='nontable' + ('(=predA)' if p==r['predicted_A'].strip() else '')
        c[lab]+=1
      # B-first/CF B-first first-step top5 for direct
      print(m,cond,o,n,dict(c.most_common()))
