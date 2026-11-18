import json,sys,re
sys.path.insert(0,'/data/rbg/users/linrui/llada')
from transformers import AutoTokenizer
from phase1.run import ROOT,CFG,instruction
from phase1.tasks import make_source
for name,info in CFG['model_revisions'].items():
    path=ROOT/'weights'/info['repo'].split('/')[1]
    tok=AutoTokenizer.from_pretrained(path,trust_remote_code=True,use_fast=True)
    words=json.loads((ROOT/f'results/phase1/words-{name}.json').read_text())
    bad=0; checked=0; ex=[]
    for n in CFG['sizes']:
      for sid in range(200):
        s=make_source(n,sid,words,CFG['seed'])
        vals={v for r in s['rows'] for k,v in r.items() if k!='q'}
        for cond in ['Direct','Shared-path','Separate-path']:
          text=tok.apply_chat_template([{'role':'user','content':instruction(s,cond)}],tokenize=False,add_generation_prompt=True)
          ids=tok.encode(text,add_special_tokens=False); offs=[]; pos=0
          for t in ids:
              piece=tok.decode([t],skip_special_tokens=False); offs.append((pos,pos+len(piece))); pos+=len(piece)
          assert pos==len(text),(pos,len(text))
          for m in re.finditer(r'(?<![|_a-z])[a-z]+(?![|_a-z])',text):
            if m.group() not in vals: continue
            st,en=m.span(); checked+=1
            cover=[(a,b) for a,b in offs if b>st and a<en]
            # one token, covering the value plus at most a leading space
            if not (len(cover)==1 and cover[0][1]==en and text[cover[0][0]:st] in ('',' ')):
                bad+=1; ex.append((m.group(),[text[a:b] for a,b in cover]))
    print(name,'type',type(tok).__name__,'value occurrences',checked,'not single-token',bad,ex[:5],flush=True)
