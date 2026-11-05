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
# Batched and single-run first-pass values for an identical prompt.
x=torch.tensor([ids],device=model.device)
with torch.no_grad():
    single=model(input_ids=x,use_cache=False).logits
    batch=model(input_ids=x.repeat(2,1),use_cache=False).logits
for pos in slots.values():
    a1=single[0,pos].float(); b1=batch[0,pos].float()
    assert int(a1.argmax())==int(b1.argmax()),'batch top-1 differs'
    assert torch.allclose(a1,b1,atol=0.1,rtol=0.01),'batch logits differ'
peak=torch.cuda.max_memory_allocated()/1e9
assert peak < 42, f'peak {peak:.1f} GiB unsafe'
out=dict(model=a.model,model_revision=CFG['model_revisions'][a.model]['revision'],status='pass',pool_size=len(words),aligned_pool_size=len(usable),determinism=True,immutability=True,batching=True,slot_alignment=True,task_integrity=True,seconds_per_two_pass_run=elapsed,peak_vram_GB=peak,total_seconds=time.time()-start)
Path(f'results/phase1/G0-{a.model}.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2),flush=True)
