import json,math,collections,sys
from pathlib import Path
import numpy as np
from scipy.stats import binomtest
from phase1.run import CFG,ROOT

BASE=ROOT/'results/phase1'; TR=BASE/'traces'
def read(name,exp):
    p=TR/f'{name}-exp{exp}.jsonl'
    if not p.exists(): return []
    rows=[json.loads(x) for x in p.read_text().splitlines() if x]
    ids=[r['run_id'] for r in rows]
    if len(ids)!=len(set(ids)): raise ValueError(f'duplicate runs in {p}')
    return rows

def ci_by_source(rows,metric,seed=7331):
    if not rows:return (float('nan'),float('nan'),float('nan'))
    groups=collections.defaultdict(list)
    for r in rows: groups[(r['table_size'],r['source_id'])].append(float(metric(r)))
    vals=np.array([np.mean(x) for x in groups.values()]); n=len(vals)
    rng=np.random.default_rng(seed); b=[]
    for _ in range(CFG['bootstrap_resamples']): b.append(vals[rng.integers(n,size=n)].mean())
    return float(vals.mean()),float(np.quantile(b,.025)),float(np.quantile(b,.975))

def fmt(stat):
    x,l,u=stat; return f'{100*x:.1f}% [{100*l:.1f}, {100*u:.1f}]'

def paired_gap(left,right,metric):
    l={(r['table_size'],r['source_id']):r for r in left}; r={(x['table_size'],x['source_id']):x for x in right}; keys=sorted(l.keys()&r.keys())
    fake=[dict(table_size=k[0],source_id=k[1],v=float(metric(l[k]))-float(metric(r[k]))) for k in keys]
    return ci_by_source(fake,lambda x:x['v'])

def interaction(rows,cond1,cond2,metric,left,right):
    d={(r['table_size'],r['source_id'],r['condition'],r['order_or_branch']):r for r in rows}
    keys=sorted({(r['table_size'],r['source_id']) for r in rows})
    vals=[]
    for n,sid in keys:
        need=[(n,sid,c,o) for c in [cond1,cond2] for o in [left,right]]
        if not all(k in d for k in need):continue
        v=(float(metric(d[n,sid,cond1,left]))-float(metric(d[n,sid,cond1,right])))-(float(metric(d[n,sid,cond2,left]))-float(metric(d[n,sid,cond2,right])))
        vals.append(dict(table_size=n,source_id=sid,v=v))
    return ci_by_source(vals,lambda r:r['v'])

def analyze(name):
    e1,e2,e3=(read(name,i) for i in (1,2,3)); lines=[f'# Phase 1 pilot: {name}','']
    g0=BASE/f'G0-{name}.json'; g0data=json.loads(g0.read_text()) if g0.exists() else {}
    env=json.loads((BASE/'environment.json').read_text())
    g1=all(np.mean([r[f'{field}_correct'] for r in e1 if r['order_or_branch']==order])>=CFG['g1_min_accuracy'] for order in ['A-first','B-first','CF'] for field in ['A','B']) if e1 else False
    expected1=60; expected2=9*len(CFG['sizes'])*int(CFG['sources_per_cell']); expected3=8*len(CFG['sizes'])*int(CFG['sources_per_cell'])
    lines += ['## Run summary','',f'- Environment: {env["gpu_count"]} {env["gpu_model"]} GPUs ({env["gpu_vram_MiB"]} MiB each); used GPU {0 if name=="llada" else 1}; PyTorch {env["torch"]}, CUDA {env["cuda_runtime"]}, Transformers {env["transformers"]}.',f'- Revision: `{CFG["model_revisions"][name]["revision"]}`; code commit in each trace row.',f'- Rows: Exp 1 {len(e1)}/{expected1}, Exp 2 {len(e2)}/{expected2}, Exp 3 {len(e3)}/{expected3}.',f'- G0: {g0data.get("status","missing")}; G1: {"pass" if g1 else "fail or incomplete"}.','']
    if g0data: lines += [f'- G0 speed: {g0data.get("two_pass_seconds_by_size",{})} s per two-pass run; projected {g0data.get("projected_hours_at_200_sources",0):.2f} h at 200 sources; peak allocated VRAM {g0data.get("peak_vram_GB",0):.2f} GB.','']
    timings=[]; peaks=[]
    import re
    for exp in [1,2,3]:
        path=BASE/'logs'/f'run-{name}-exp{exp}.log'
        if path.exists():
            for line in path.read_text().splitlines():
                m=re.search(r'DONE (\d+) (\d+) new (\d+) seconds ([0-9.]+) peak_GB ([0-9.]+)',line)
                if m:timings.append(float(m.group(4)));peaks.append(float(m.group(5)))
    if timings:lines += [f'- Actual measured run time: {sum(timings)/3600:.2f} GPU-hours across Exp 1–3; peak allocated VRAM {max(peaks):.2f} GB.','']
    lines += ['## Exp 1 and G1','', '| Order | A accuracy | B accuracy |','|---|---:|---:|']
    for order in ['A-first','B-first','CF']:
        subset=[r for r in e1 if r['order_or_branch']==order]
        lines += [f'| {order} | {fmt(ci_by_source(subset,lambda r:r["A_correct"]))} | {fmt(ci_by_source(subset,lambda r:r["B_correct"]))} |']
    lines += ['','## Exp 2 accuracy','', '| Size | Condition | Order | A | B | Both |','|---:|---|---|---:|---:|---:|']
    for n in CFG['sizes']:
      for cond in ['Direct','Shared-path','Separate-path']:
       for order in ['A-first','B-first','CF']:
        sub=[r for r in e2 if r['table_size']==n and r['condition']==cond and r['order_or_branch']==order]
        lines += [f'| {n} | {cond} | {order} | {fmt(ci_by_source(sub,lambda r:r["A_correct"]))} | {fmt(ci_by_source(sub,lambda r:r["B_correct"]))} | {fmt(ci_by_source(sub,lambda r:r["both_correct"]))} |']
    lines += ['','## Exp 2 paired order outcomes','', '| Size | Condition | Both right | Both wrong | Only A-first right | Only B-first right | McNemar p | CF chose successful first field |','|---:|---|---:|---:|---:|---:|---:|---:|']
    g2parts=[]
    for n in CFG['sizes']:
      for cond in ['Direct','Shared-path','Separate-path']:
        sub=[r for r in e2 if r['table_size']==n and r['condition']==cond]
        d={(r['source_id'],r['order_or_branch']):r for r in sub}; c=[0,0,0,0]; selected=[]
        for sid in sorted({r['source_id'] for r in sub}):
          if any((sid,o) not in d for o in ['A-first','B-first','CF']):continue
          a=d[sid,'A-first']['both_correct']; b=d[sid,'B-first']['both_correct']
          ix=0 if a and b else 1 if not a and not b else 2 if a else 3;c[ix]+=1
          if a!=b:selected.append(d[sid,'CF']['first_field']==('A' if a else 'B'))
        p=binomtest(min(c[2],c[3]),c[2]+c[3],.5).pvalue if c[2]+c[3] else float('nan')
        lines += [f'| {n} | {cond} | {c[0]} | {c[1]} | {c[2]} | {c[3]} | {p:.4g} | {sum(selected)}/{len(selected)} |']
        g2parts.append((n,cond,c[2]+c[3]))
    lines += ['','## Exp 2 order interactions','', '| Size | Shared A-first minus B-first B accuracy | Separate gap | Shared minus Separate |','|---:|---:|---:|---:|']
    for n in CFG['sizes']:
      gaps={}
      for cond in ['Shared-path','Separate-path']:
        a=[r for r in e2 if r['table_size']==n and r['condition']==cond and r['order_or_branch']=='A-first']; b=[r for r in e2 if r['table_size']==n and r['condition']==cond and r['order_or_branch']=='B-first']; gaps[cond]=paired_gap(a,b,lambda r:r['B_correct'])
      lines += [f'| {n} | {fmt(gaps["Shared-path"])} | {fmt(gaps["Separate-path"])} | {fmt(interaction([r for r in e2 if r["table_size"]==n],"Shared-path","Separate-path",lambda r:r["B_correct"],"A-first","B-first"))} |']
    lines += ['','## Exp 3 prefilled A intervention','', '| Size | Condition | Gold minus Masked | Predicted minus Masked | Wrong minus Masked | Wrong B matches alternative |','|---:|---|---:|---:|---:|---:|']
    for n in CFG['sizes']:
      for cond in ['Shared-path','Separate-path']:
        d={o:[r for r in e3 if r['table_size']==n and r['condition']==cond and r['order_or_branch']==o] for o in ['Masked','Gold','Predicted','Wrong']}
        gaps=[paired_gap(d[o],d['Masked'],lambda r:r['B_correct']) for o in ['Gold','Predicted','Wrong']]
        lines += [f'| {n} | {cond} | {fmt(gaps[0])} | {fmt(gaps[1])} | {fmt(gaps[2])} | {fmt(ci_by_source(d["Wrong"],lambda r:r["B_matches_alternative"]))} |']
    lines += ['','### Shared-path minus Separate-path Exp 3 gaps','', '| Size | Gold gap interaction | Predicted gap interaction | Wrong gap interaction | Wrong alternative match difference |','|---:|---:|---:|---:|---:|']
    for n in CFG['sizes']:
      sub=[r for r in e3 if r['table_size']==n]
      vals=[fmt(interaction(sub,'Shared-path','Separate-path',lambda r:r['B_correct'],branch,'Masked')) for branch in ['Gold','Predicted','Wrong']]
      w=[r for r in sub if r['order_or_branch']=='Wrong']; sh=[r for r in w if r['condition']=='Shared-path']; se=[r for r in w if r['condition']=='Separate-path']
      prop=paired_gap(sh,se,lambda r:r['B_matches_alternative'])
      lines += [f'| {n} | {vals[0]} | {vals[1]} | {vals[2]} | {fmt(prop)} |']
    lines += ['','## Step-0 confidence and CF choice','', '| Size | Condition | Mean A top-1 | Mean B top-1 | CF first A |','|---:|---|---:|---:|---:|']
    for n in CFG['sizes']:
      for cond in ['Direct','Shared-path','Separate-path']:
        sub=[r for r in e2 if r['table_size']==n and r['condition']==cond and r['order_or_branch']=='CF']
        if not sub:continue
        ac=np.mean([r['step0']['A']['top5_probs'][0] for r in sub]); bc=np.mean([r['step0']['B']['top5_probs'][0] for r in sub]); fa=np.mean([r['first_field']=='A' for r in sub]); lines += [f'| {n} | {cond} | {ac:.3f} | {bc:.3f} | {fa:.3f} |']
    cf=[r for r in e2 if r['order_or_branch']=='CF']
    if cf:
        concord=sum((r['step0']['A']['top5_probs'][0]>=r['step0']['B']['top5_probs'][0])==(r['first_field']=='A') for r in cf)
        lines += ['',f'Step-0 top-1 confidence predicts CF first-field choice in {concord}/{len(cf)} runs (ties use a seeded draw).']
    lines += ['','## G2','']
    g2_pass_sizes=[]
    for n in CFG['sizes']:
      direct_by_order={o:[r for r in e2 if r['table_size']==n and r['condition']=='Direct' and r['order_or_branch']==o] for o in ['A-first','B-first','CF']}
      dacc={o:ci_by_source(sub,lambda r:r['B_correct'])[0] for o,sub in direct_by_order.items()}
      path={}
      for cond in ['Shared-path','Separate-path']:
        sub=[r for r in e2 if r['table_size']==n and r['condition']==cond]
        path[cond]=ci_by_source(sub,lambda r:r['B_correct'])
      discord={x[1]:x[2] for x in g2parts if x[0]==n}
      passes=all(v>=CFG['g2_direct_min_accuracy'] for v in dacc.values()) and all(v[1]>1/n and v[0]<CFG['g2_path_max_approx_accuracy'] for v in path.values()) and all(v>=CFG['g2_min_discordant_pairs'] for v in discord.values())
      if passes:g2_pass_sizes.append(n)
      lines += [f'- Size {n}: {"pass" if passes else "fail"}; Direct B by order {dacc}; path B with intervals {path}; discordant pairs {discord}.']
    lines += ['','## Interpretation limits','', '- A stays left of B throughout Phase 1, so CF preference cannot yet be separated from position. Exp 4 tests that.','- Gold beating Wrong does not show that the correct value helps; Masked is the relevant baseline.','- Exp 3 measures conditional response in a fixed context, not an equal-compute method comparison.','- Results are pilot evidence; these sources must stay out of any final test set.','']
    candidates=[]
    for n in g2_pass_sizes:
        sub=[r for r in e2 if r['table_size']==n and r['condition']=='Shared-path']
        af=[r for r in sub if r['order_or_branch']=='A-first']
        bf=[r for r in sub if r['order_or_branch']=='B-first']
        gap=paired_gap(af,bf,lambda r:r['B_correct'])
        if gap[1]>0:candidates.append(n)
    if candidates:
        chosen=min(candidates)
        rec=f'Awaiting human review: lock Shared-path, table size {chosen}, A-first for Exp 4; G2 passed and the paired B-accuracy gap has a positive 95% lower bound.'
    else:
        rec='Awaiting human review: lock no Exp 4 configuration from this pilot; no table size both passed G2 and showed a positive 95% lower bound for the Shared-path A-first B-accuracy gap.'
    lines += ['','## Exp 4 recommendation','',rec,'']
    return '\n'.join(lines)

if __name__=='__main__':
    names=sys.argv[1:] or ['llada','dream']
    report=['# Phase 1 report','']
    for name in names: report.append(analyze(name))
    report.extend(['## Deviations, failed checks, and fixes','',(BASE/'DECISIONS.md').read_text()])
    (BASE/'report.md').write_text('\n\n'.join(report)+'\n')
