import json
from transformers import AutoTokenizer
from phase1.run import ROOT,CFG,instruction
from phase1.tasks import pool,usable_pool,make_source
for name,info in CFG['model_revisions'].items():
    path=ROOT/'weights'/info['repo'].split('/')[1]
    tok=AutoTokenizer.from_pretrained(path,trust_remote_code=True,use_fast=True)
    mask=json.loads((path/'config.json').read_text())['mask_token_id']
    raw=pool(tok,mask)
    probe=make_source(4,0,raw,CFG['seed'])
    words=usable_pool(tok,mask,raw,instruction(probe,'Direct'))
    out=ROOT/'results/phase1'/f'words-{name}.json'
    out.write_text(json.dumps(words,ensure_ascii=False)+'\n')
    print(name,len(words),out,flush=True)
