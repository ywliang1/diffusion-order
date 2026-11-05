import argparse,json,os,random,time,subprocess
from pathlib import Path
import yaml,torch
from transformers import AutoTokenizer,AutoModel
from phase1.tasks import pool,usable_pool,make_source,tables,integrity
from phase1.decoder import render,aligned,decode

ROOT=Path(__file__).resolve().parent.parent
CFG=yaml.safe_load((ROOT/'phase1/config.yaml').read_text())

def load_model(name,gpu):
    info=CFG['model_revisions'][name]; path=ROOT/'weights'/info['repo'].split('/')[1]
    tok=AutoTokenizer.from_pretrained(path,trust_remote_code=True,use_fast=True)
    model=AutoModel.from_pretrained(path,trust_remote_code=True,torch_dtype=torch.bfloat16,device_map=f'cuda:{gpu}',low_cpu_mem_usage=True).eval()
    mask_id=model.config.mask_token_id
    return model,tok,mask_id

def instruction(source,condition=None,copy=False):
    if copy:
        return CFG['copy_prompt_template'].format(A=source['A'],B=source['B']).strip()
    t=tables(source,condition,CFG['seed'])
    return CFG['prompt_template'].format(tables=t,target=source['rows'][source['target']]['q'])

def commit():
    return subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()

def make_row(name,exp,source,condition,order,model,tok,mask_id,code_commit,initial_A=None):
    seed=CFG['seed']; rows=source.get('rows')
    if exp==1:
        A=source['A']; B=source['B']; size=0; sid=source['source_id']; condition='Copy'; branch=None
    else:
        target=rows[source['target']]; A=target['A']; B=target['B']; size=source['size']; sid=source['source_id']; branch=order if exp==3 else None
    inst=instruction(source,condition,copy=(exp==1))
    if exp in (1,2):
        ids,slots=render(tok,mask_id,inst)
        pred,steps,step0,tie=decode(model,tok,mask_id,ids,slots,order,seed+sid+size*1000)
        predA=pred['A']; predB=pred['B']; alt=None
        first=steps[0]['slot']
    else:
        wrong=rows[source['wrong']]; alt=wrong['B'] if order=='Wrong' else None
        ids,slots=render(tok,mask_id,inst)
        # Initial A prediction is always from the same fully masked state.
        if initial_A is None:
            apred,_,_,_=decode(model,tok,mask_id,ids,{'A':slots['A']},'A-first',seed+sid+size*1000)
            predA=apred['A']
        else: predA=initial_A
        if order=='Masked': held=None
        elif order=='Gold': held=A
        elif order=='Predicted': held=predA
        elif order=='Wrong': held=wrong['A']
        else: raise ValueError(order)
        if held is not None:
            tid=tok.encode(held,add_special_tokens=False)
            if len(tid)!=1: raise ValueError(f'held value not single token: {held}')
            ids[slots['A']]=tid[0]
        pred,steps,step0,tie=decode(model,tok,mask_id,ids,{'B':slots['B']},'B-first',seed+sid+size*1000)
        predB=pred['B']; first='B'
    rid=f'{name}-e{exp}-n{size}-s{sid}-{condition}-{order}'
    return dict(run_id=rid,model=name,model_revision=CFG['model_revisions'][name]['revision'],code_commit=code_commit,seed=seed,experiment=exp,source_id=sid,table_size=size,condition=condition,order_or_branch=order,target_A=A,target_B=B,predicted_A=predA,predicted_B=predB,alternative_B=alt,A_correct=(predA==A),B_correct=(predB==B),both_correct=(predA==A and predB==B),B_matches_alternative=(predB==alt if alt is not None else None),first_field=first,steps=steps,step0=step0,tie_broken=tie)

def runs(name,exp,n,words):
    if exp==1:
        rng=random.Random(CFG['seed']); vals=rng.sample(words,40)
        for sid in range(20):
            s=dict(source_id=sid,A=vals[2*sid],B=vals[2*sid+1])
            for order in ['A-first','B-first','CF']: yield s,'Copy',order
    else:
        for size in CFG['sizes']:
            for sid in range(n):
                s=make_source(size,sid,words,CFG['seed'])
                for condition in (['Direct','Shared-path','Separate-path'] if exp==2 else ['Shared-path','Separate-path']):
                    integrity(s,condition)
                    for order in (['A-first','B-first','CF'] if exp==2 else ['Masked','Gold','Predicted','Wrong']): yield s,condition,order

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--model',choices=['llada','dream'],required=True); ap.add_argument('--gpu',type=int,required=True); ap.add_argument('--exp',type=int,choices=[1,2,3],required=True); ap.add_argument('--sources',type=int,default=200); args=ap.parse_args()
    torch.cuda.set_device(args.gpu)
    model,tok,mask=load_model(args.model,args.gpu)
    raw=pool(tok,mask)
    probe=make_source(4,0,raw,CFG['seed'])
    words=usable_pool(tok,mask,raw,instruction(probe,'Direct'))
    print('POOL',len(words),'GPU',args.gpu,flush=True)
    path=ROOT/'results/phase1/traces'/f'{args.model}-exp{args.exp}.jsonl'; path.parent.mkdir(exist_ok=True,parents=True)
    seen=set()
    if path.exists():
        for line in path.read_text().splitlines():
            if line: seen.add(json.loads(line)['run_id'])
    code_commit=commit(); start=time.time(); new=0
    initial_cache={}
    with open(path,'a',buffering=1) as f:
        for s,cond,order in runs(args.model,args.exp,args.sources,words):
            size=s.get('size',0); rid=f'{args.model}-e{args.exp}-n{size}-s{s["source_id"]}-{cond}-{order}'
            if rid in seen: continue
            initial_A=initial_cache.get((size,s["source_id"],cond)) if args.exp==3 else None
            row=make_row(args.model,args.exp,s,cond,order,model,tok,mask,code_commit,initial_A)
            if args.exp==3: initial_cache[(size,s["source_id"],cond)]=row["predicted_A"]
            f.write(json.dumps(row,ensure_ascii=False)+'\n'); f.flush(); os.fsync(f.fileno())
            seen.add(rid); new+=1
            if new%50==0: print('PROGRESS',args.exp,new,len(seen),'elapsed',round(time.time()-start,1),flush=True)
    print('DONE',args.exp,len(seen),'new',new,'seconds',round(time.time()-start,1), 'peak_GB',round(torch.cuda.max_memory_allocated()/1e9,2),flush=True)

if __name__=='__main__': main()
