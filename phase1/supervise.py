import argparse,json,os,subprocess,sys,time
from pathlib import Path
from phase1.run import ROOT,CFG

p=argparse.ArgumentParser();p.add_argument('--model',choices=['llada','dream'],required=True);p.add_argument('--gpu',type=int,required=True);p.add_argument('--sources',type=int,required=True);a=p.parse_args()
base=ROOT/'results/phase1'; logs=base/'logs'; logs.mkdir(exist_ok=True,parents=True)

def nrows(exp):
    path=base/'traces'/f'{a.model}-exp{exp}.jsonl'
    if not path.exists(): return 0
    return sum(1 for line in path.open() if line.strip())

def expected(exp):
    return {1:60,2:9*len(CFG['sizes'])*a.sources,3:8*len(CFG['sizes'])*a.sources}[exp]

def state(msg):
    (base/f'supervisor-{a.model}.json').write_text(json.dumps(dict(model=a.model,time=time.strftime('%Y-%m-%d %H:%M:%S %Z'),message=msg,counts={i:nrows(i) for i in [1,2,3]},expected={i:expected(i) for i in [1,2,3]}),indent=2)+'\n')
    print(msg,flush=True)

def launch(exp):
    failures=0
    while nrows(exp)<expected(exp):
        cmd=[sys.executable,'-u','-m','phase1.run','--model',a.model,'--gpu',str(a.gpu),'--exp',str(exp),'--sources',str(a.sources)]
        with (logs/f'run-{a.model}-exp{exp}.log').open('a') as f:
            f.write(f'\nSUPERVISOR launch {time.ctime()} count={nrows(exp)}\n');f.flush()
            proc=subprocess.Popen(cmd,cwd=ROOT,stdout=f,stderr=subprocess.STDOUT,env=os.environ.copy())
            last=nrows(exp);last_change=time.time()
            while proc.poll() is None:
                time.sleep(60)
                now=nrows(exp)
                if now>last: last=now;last_change=time.time();state(f'Exp {exp}: {now}/{expected(exp)}')
                if time.time()-last_change>1800:
                    proc.terminate()
                    try:proc.wait(timeout=60)
                    except subprocess.TimeoutExpired:proc.kill();proc.wait()
                    state(f'Exp {exp}: hung at {now}, own process stopped for resume')
                    break
            code=proc.wait()
        if nrows(exp)>=expected(exp):break
        failures+=1;state(f'Exp {exp}: process exit {code}, restart {failures}/3')
        if failures>=3:raise RuntimeError(f'Exp {exp} shard failed three times; inspect log')
        time.sleep(10)
    # Read all IDs and verify no duplicate or count discrepancy.
    path=base/'traces'/f'{a.model}-exp{exp}.jsonl'; rows=[json.loads(x) for x in path.read_text().splitlines() if x]
    assert len(rows)==expected(exp)==len({r['run_id'] for r in rows}),f'Exp {exp} count or duplicate error'
    state(f'Exp {exp}: complete {len(rows)} rows')

state('starting')
launch(1)
rows=[json.loads(x) for x in (base/'traces'/f'{a.model}-exp1.jsonl').read_text().splitlines() if x]
acc={f'{order}-{field}':sum(r[f'{field}_correct'] for r in rows if r['order_or_branch']==order)/20 for order in ['A-first','B-first','CF'] for field in ['A','B']}
(base/f'G1-{a.model}.json').write_text(json.dumps(dict(status='pass' if all(x>=.95 for x in acc.values()) else 'fail',accuracies=acc),indent=2)+'\n')
if not all(x>=.95 for x in acc.values()):state(f'G1 failed: {acc}');sys.exit(2)
state(f'G1 passed: {acc}')
launch(2)
launch(3)
state('all experiments complete')
