import json
from pathlib import Path
from transformers import AutoTokenizer
from phase1.run import ROOT,CFG,instruction
from phase1.tasks import pool,usable_pool,make_source,tables,integrity
from phase1.decoder import render
for name,info in CFG['model_revisions'].items():
    path=ROOT/'weights'/info['repo'].split('/')[1]
    tok=AutoTokenizer.from_pretrained(path,trust_remote_code=True,use_fast=True)
    mask=json.loads((path/'config.json').read_text())['mask_token_id']
    raw=pool(tok,mask);probe=make_source(4,0,raw,CFG['seed']);words=usable_pool(tok,mask,raw,instruction(probe,'Direct'))
    mismatches=[]
    for n in CFG['sizes']:
        for sid in range(CFG['sources_per_cell']):
            source=make_source(n,sid,words,CFG['seed'])
            lengths=[]
            for cond in ['Direct','Shared-path','Separate-path']:
                integrity(source,cond)
                ids,_=render(tok,mask,instruction(source,cond))
                lengths.append(len(ids))
            if len(set(lengths))!=1:mismatches.append((n,sid,lengths))
    print(name,'pool',len(words),'mismatches',len(mismatches),'examples',mismatches[:5],flush=True)
