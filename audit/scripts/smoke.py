"""Smoke: replay 5 Phase 1 Exp 2 rows with unmodified phase1 code; write only to scratch."""
import json,sys,time
sys.path.insert(0,'/data/rbg/users/linrui/llada')
import torch
from phase1.run import load_model,make_row,ROOT,CFG,commit
from phase1.tasks import pool,usable_pool,make_source,integrity
from phase1.run import instruction
name,gpu,out=sys.argv[1],int(sys.argv[2]),sys.argv[3]
torch.cuda.set_device(gpu)
t=time.time(); model,tok,mask=load_model(name,gpu); load_s=time.time()-t
words=json.loads((ROOT/f'results/phase1/words-{name}.json').read_text())
# confirm the regenerated pool equals the exported Phase 1 pool
raw=pool(tok,mask); regen=usable_pool(tok,mask,raw,instruction(make_source(4,0,raw,CFG['seed']),'Direct'))
assert regen==words,'pool regeneration differs from Phase 1 export'
old={json.loads(l)['run_id']:json.loads(l) for l in open(ROOT/f'results/phase1/traces/{name}-exp2.jsonl')}
picks=[(4,0,'Direct','CF'),(8,1,'Shared-path','A-first'),(16,2,'Separate-path','B-first'),(8,3,'Direct','B-first'),(16,4,'Shared-path','CF')]
torch.cuda.reset_peak_memory_stats(); res=[]
for size,sid,cond,order in picks:
    s=make_source(size,sid,words,CFG['seed']); integrity(s,cond)
    torch.cuda.synchronize(); t=time.time()
    r=make_row(name,2,s,cond,order,model,tok,mask,'smoke')
    torch.cuda.synchronize(); dt=time.time()-t
    o=old[r['run_id']]
    same_tokens=[x['token_id'] for x in r['steps']]==[x['token_id'] for x in o['steps']] and [x['slot'] for x in r['steps']]==[x['slot'] for x in o['steps']]
    maxdp=max(abs(a-b) for f in r['step0'] for a,b in zip(r['step0'][f]['top5_probs'],o['step0'][f]['top5_probs']))
    res.append(dict(run_id=r['run_id'],seconds=dt,prompt_tokens=None,same_commits_as_phase1=same_tokens,max_step0_prob_diff=maxdp,pred=(r['predicted_A'],r['predicted_B']),gold=(r['target_A'],r['target_B'])))
    print(json.dumps(res[-1]),flush=True)
# determinism: rerun first pick
s=make_source(4,0,words,CFG['seed']); a=make_row(name,2,s,'Direct','CF',model,tok,mask,'smoke'); b=make_row(name,2,s,'Direct','CF',model,tok,mask,'smoke')
summary=dict(model=name,gpu=torch.cuda.get_device_name(gpu),load_seconds=load_s,pool_matches_phase1=True,
  per_instance_seconds=[x['seconds'] for x in res],all_commits_match_phase1=all(x['same_commits_as_phase1'] for x in res),
  rerun_identical=(a['steps']==b['steps'] and a['step0']==b['step0']),
  peak_allocated_GB=torch.cuda.max_memory_allocated(gpu)/1e9,peak_reserved_GB=torch.cuda.max_memory_reserved(gpu)/1e9,rows=res)
json.dump(summary,open(out,'w'),indent=2); print('SUMMARY',json.dumps({k:v for k,v in summary.items() if k!='rows'}),flush=True)
