"""Compare a dlm replay with the frozen Phase 1 traces, row by row.

Exact match = same committed (slot, token id, prob) sequence, same step-0 top-5 tokens and
probabilities, same raw predictions, first field and tie flag. Decision match = same
(slot, token id) sequence. For each row the decision margin is the smallest margin over
its steps: min(token margin, CF choice margin when there was a choice).

    python -m experiments.equivalence.compare --stage equivalence --trace a6000 --exps 1,2,3
"""
import argparse
import json
from collections import defaultdict

from dlm.models import ROOT
from dlm.runner import read_jsonl

BINS = [(0, .01), (.01, .02), (.02, .05), (.05, .1), (.1, 1.01)]


def decisions(steps, new=False):
    return [((s['field'] if new else s['slot']), s['token_id']) for s in steps]


def margin(row):
    m = []
    for s in row['steps']:
        m.append(s['tok_margin'])
        if s.get('choice_margin') is not None:
            m.append(s['choice_margin'])
    return min(m)


def compare(stage, trace, model, exps):
    new = {r['run_id']: r for r in read_jsonl(ROOT / 'results' / stage / 'traces' / f'{trace}-{model}.jsonl')}
    res = dict(rows=0, missing=0, exact=0, decisions=0, preds=0, max_prob_diff=0.0, mismatches=[])
    bins = defaultdict(lambda: dict(n=0, decision_flips=0, b_flips=0, both_flips=0))
    acc = defaultdict(lambda: [0, 0, 0])  # n, phase1 B correct, replay B correct (raw scoring, as Phase 1)
    for exp in exps:
        for old in read_jsonl(ROOT / 'results/phase1/traces' / f'{model}-exp{exp}.jsonl'):
            res['rows'] += 1
            r = new.get(old['run_id'])
            if r is None:
                res['missing'] += 1
                continue
            same_dec = decisions(old['steps']) == decisions(r['steps'], new=True)
            same_pred = (old['predicted_A'], old['predicted_B']) == (r['predicted_A'], r['predicted_B'])
            probs_old = [s['prob'] for s in old['steps']] + [p for f in sorted(old['step0']) for p in old['step0'][f]['top5_probs']]
            probs_new = [s['prob'] for s in r['steps']] + [p for f in sorted(r['step0']) for p in r['step0'][f]['top5_probs']]
            toks_same = all(old['step0'][f]['top5_tokens'] == r['step0'][f]['top5_tokens'] for f in old['step0']) and set(old['step0']) == set(r['step0'])
            diff = max(abs(a - b) for a, b in zip(probs_old, probs_new)) if len(probs_old) == len(probs_new) else float('inf')
            res['max_prob_diff'] = max(res['max_prob_diff'], diff)
            exact = (same_dec and same_pred and toks_same and probs_old == probs_new
                     and old['first_field'] == r['first_field'] and old['tie_broken'] == r['tie_broken']
                     and old.get('B_matches_alternative') == r.get('B_matches_alternative'))
            res['exact'] += exact
            res['decisions'] += same_dec
            res['preds'] += same_pred
            if not exact and len(res['mismatches']) < 20:
                res['mismatches'].append(dict(run_id=old['run_id'], same_decisions=same_dec, prob_diff=diff,
                                              old=decisions(old['steps']), new=decisions(r['steps'], True)))
            m = margin(r)
            b = next(f'{lo:.2f}-{hi:.2f}' for lo, hi in BINS if lo <= m < hi)
            bins[b]['n'] += 1
            bins[b]['decision_flips'] += not same_dec
            bins[b]['b_flips'] += old['B_correct'] != (r['predicted_B'] == old['target_B'])
            bins[b]['both_flips'] += old['both_correct'] != (r['predicted_A'] == old['target_A'] and r['predicted_B'] == old['target_B'])
            key = (exp, old['condition'], old['order_or_branch'])
            acc[key][0] += 1
            acc[key][1] += old['B_correct']
            acc[key][2] += r['predicted_B'] == old['target_B']
    res['by_margin'] = dict(sorted(bins.items()))
    res['b_accuracy'] = {f'e{k[0]} {k[1]} {k[2]}': dict(n=v[0], phase1=v[1] / v[0], replay=v[2] / v[0]) for k, v in sorted(acc.items())}
    gpus = {r['meta']['gpu_name'] for r in new.values()}
    hosts = {r['meta']['hostname'] for r in new.values()}
    res['replay_gpu'] = sorted(gpus)
    res['replay_hosts'] = sorted(hosts)
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--stage', default='equivalence')
    ap.add_argument('--trace', required=True)
    ap.add_argument('--exps', default='1,2,3')
    ap.add_argument('--models', default='llada,dream')
    a = ap.parse_args()
    exps = [int(x) for x in a.exps.split(',')]
    out = {m: compare(a.stage, a.trace, m, exps) for m in a.models.split(',')}
    path = ROOT / 'results' / a.stage / f'compare-{a.trace}.json'
    path.write_text(json.dumps(out, indent=2) + '\n')
    for m, r in out.items():
        print(f"{m}: rows {r['rows']} missing {r['missing']} exact {r['exact']} decisions {r['decisions']} "
              f"preds {r['preds']} max_prob_diff {r['max_prob_diff']:.3g} gpu {r['replay_gpu']} host {r['replay_hosts']}")
        for b, v in r['by_margin'].items():
            print(f"   margin {b}: n {v['n']} decision flips {v['decision_flips']} B flips {v['b_flips']} both flips {v['both_flips']}")
    print('wrote', path)


if __name__ == '__main__':
    main()
