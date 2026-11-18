"""Batched vs unbatched decisions on 50 instances (3 orders each, lockstep batch of 3).

    python -m experiments.equivalence.batchcheck --model llada --gpu 7
"""
import argparse
import json

from dlm.models import ROOT, load
from dlm.runner import grouped, load_cfg
from experiments.equivalence import exp


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--model', required=True)
    ap.add_argument('--gpu', type=int, required=True)
    ap.add_argument('--n', type=int, default=50)
    a = ap.parse_args()
    bundle = load(a.model, a.gpu)
    cfg = load_cfg(ROOT / 'experiments/equivalence/config_exp2.yaml')
    ctx = exp.prepare(bundle.tok, bundle.mask_id, a.model, cfg)
    groups = grouped(exp.jobs(ctx))
    stride = len(groups) // a.n
    picks = groups[::stride][:a.n]
    same_dec = same_prob = 0
    max_diff = 0.0
    bad = []
    for g in picks:
        one = exp.execute(bundle, ctx, g, batch=False)
        many = exp.execute(bundle, ctx, g, batch=True)
        for x, y in zip(one, many):
            d1 = [(s['pos'], s['token_id']) for s in x['steps']]
            d2 = [(s['pos'], s['token_id']) for s in y['steps']]
            p1 = [s['prob'] for s in x['steps']]
            p2 = [s['prob'] for s in y['steps']]
            same_dec += d1 == d2
            same_prob += p1 == p2
            max_diff = max(max_diff, max(abs(u - v) for u, v in zip(p1, p2)))
            if d1 != d2:
                bad.append(x['run_id'])
    n = sum(len(g) for g in picks)
    out = dict(model=a.model, gpu=bundle.meta['gpu_name'], host=bundle.meta['hostname'], instances=len(picks), rows=n,
               same_decisions=same_dec, identical_probs=same_prob, max_prob_diff=max_diff, decision_mismatches=bad,
               verdict='batching allowed' if same_dec == n else 'use batch size 1')
    path = ROOT / 'results/equivalence' / f'batchcheck-{a.model}.json'
    path.write_text(json.dumps(out, indent=2) + '\n')
    print(json.dumps(out), flush=True)


if __name__ == '__main__':
    main()
