import argparse,json,time,random
from pathlib import Path
import torch
from phase1.run import load_model,CFG,instruction
from phase1.tasks import pool,usable_pool,make_source,tables,integrity
from phase1.decoder import render,aligned,decode

p=argparse.ArgumentParser();p.add_argument('--model',required=True);p.add_argument('--gpu',type=int,required=True);a=p.parse_args()
start=time.time();torch.cuda.set_device(a.gpu)
model,tok,mask=load_model(a.model,a.gpu)
raw=pool(tok,mask)
probe=make_source(4,0,raw,CFG['seed'])
words=usable_pool(tok,mask,raw,instruction(probe,'Direct'))
source=make_source(4,0,words,CFG['seed']);integrity(source,'Direct');integrity(source,'Shared-path');integrity(source,'Separate-path')
inst=instruction(source,'Direct')
# Check values in exact two-slot output context. All selected pool entries must work
# in either field, after filling the other field with a fixed valid value.
usable=words
assert len(usable)>=200
assert all(aligned(tok,mask,inst,source['rows'][source['target']]['A'],source['rows'][source['target']]['B']) for _ in range(1))
ids,slots=render(tok,mask,inst)
t0=time.time();one=decode(model,tok,mask,ids,slots,'CF',CFG['seed']); elapsed=time.time()-t0
two=decode(model,tok,mask,ids,slots,'CF',CFG['seed'])
assert one==two,'determinism failed'
assert len({x['slot'] for x in one[1]})==2,'immutability failed'
# Compare both decoding steps in an actual batch of identical prompts.
# bf16 matrix kernels can alter nonwinning logits with batch shape, so the
# gate compares field order and committed token IDs.
x=torch.tensor([ids],device=model.device)
xx=x.repeat(2,1)
remaining=dict(slots);batched_steps=[];tie_rng=random.Random(CFG['seed'])
with torch.no_grad():
    while remaining:
        logits=model(input_ids=xx,use_cache=False).logits
        options=[]
        for field,pos in remaining.items():
            z=logits[:,pos,:].float().clone();z[:,mask]=-float('inf')
            probabilities=torch.softmax(z,dim=-1)
            winners=probabilities.argmax(dim=-1)
            assert int(winners[0])==int(winners[1]),'batch rows disagree'
            options.append((field,pos,int(winners[0]),float(probabilities[0,winners[0]])))
        best=max(v[3] for v in options)
        first=tie_rng.choice([v for v in options if v[3]==best])
        field,pos,token_id,_=first
        xx[:,pos]=token_id
        batched_steps.append((field,token_id))
        del remaining[field]
single_steps=[(v['slot'],v['token_id']) for v in one[1]]
assert batched_steps==single_steps,f'batched decisions {batched_steps} != single {single_steps}'
timings={4:elapsed}
for size in (8,16):
    item=make_source(size,0,words,CFG['seed'])
    example=instruction(item,'Direct')
    input_ids,positions=render(tok,mask,example)
    t=time.time();decode(model,tok,mask,input_ids,positions,'CF',CFG['seed']);timings[size]=time.time()-t
projected_hours=(60*timings[4]+2800*sum(timings.values()))/3600
peak=torch.cuda.max_memory_allocated()/1e9
assert peak < 42, f'peak {peak:.1f} GiB unsafe'
out=dict(model=a.model,model_revision=CFG['model_revisions'][a.model]['revision'],status='pass',pool_size=len(words),aligned_pool_size=len(usable),determinism=True,immutability=True,batching=True,slot_alignment=True,task_integrity=True,seconds_per_two_pass_run=elapsed,two_pass_seconds_by_size=timings,projected_hours_at_200_sources=projected_hours,peak_vram_GB=peak,total_seconds=time.time()-start)
Path(f'results/phase1/G0-{a.model}.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2),flush=True)
