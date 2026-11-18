"""Exp 4 dev calibration: pick each model's table size by the pre-registered rule.

Among sizes whose one-hop CF full-answer accuracy (averaged over direction x layout) is at least 90%,
take the size whose two-hop CF dependent-field accuracy is closest to 60%; ties go to the smaller
size. If no size reaches 90% one-hop, take the size with the highest one-hop accuracy.

    python -m experiments.exp4.calibrate --trace dev
"""
import argparse
import json
from collections import defaultdict

from dlm.models import ROOT

BASE = ROOT / 'results/exp4'


def calibrate(rows):
    acc = defaultdict(lambda: defaultdict(list))
    for r in rows:
        if r['order'] != 'CF':
            continue
        acc[r['table_size']]['two' if r['hop'] == 2 else 'one'].append(
            r['dependent_correct'] if r['hop'] == 2 else r['both_correct'])
    table = {n: dict(two_hop_dependent=sum(d['two']) / len(d['two']), one_hop_both=sum(d['one']) / len(d['one']),
                     n_two=len(d['two']), n_one=len(d['one'])) for n, d in sorted(acc.items())}
    ok = [n for n, t in table.items() if t['one_hop_both'] >= .90]
    if ok:
        choice = min(ok, key=lambda n: (abs(table[n]['two_hop_dependent'] - .60), n))
        why = 'one-hop >= 90%; two-hop dependent accuracy closest to 60%'
    else:
        choice = max(table, key=lambda n: (table[n]['one_hop_both'], -n))
        why = 'no size reached 90% one-hop; highest one-hop accuracy'
    t = table[choice]
    return dict(choice=choice, reason=why, in_band=.40 <= t['two_hop_dependent'] <= .80, table=table)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--trace', default='dev')
    a = ap.parse_args()
    out = {}
    for m in ('llada', 'dream'):
        p = BASE / 'traces' / f'{a.trace}-{m}.jsonl'
        if p.exists():
            out[m] = calibrate([json.loads(x) for x in open(p) if x.strip()])
    (BASE / 'dev_calibration.json').write_text(json.dumps(out, indent=2) + '\n')
    print(json.dumps(out, indent=2))


if __name__ == '__main__':
    main()
