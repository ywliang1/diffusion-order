"""Dev validity check (PREREG): per model and arm, one-hop all-three-correct >= 90% and two-hop h accuracy >= 90%.

    python -m experiments.rq1_3f.dev_check
"""
import json

from dlm import report, stats
from dlm.models import ROOT

BASE = ROOT / 'results/rq1_3f'
ARMS = {'dev-n8': ('llada', 'dream'), 'dev-n128': ('llada',)}


def main():
    out = {}
    for trace, models in ARMS.items():
        for m in models:
            rows = report.read_required(BASE / 'traces' / f'{trace}-{m}.jsonl')
            one = [r for r in rows if r['hop'] == 1]
            two = [r for r in rows if r['hop'] == 2]
            a1 = stats.cluster_bootstrap([float(r['all_correct']) for r in one], [r['source_id'] for r in one])
            h2 = stats.cluster_bootstrap([float(r['fields']['H']['correct']) for r in two], [r['source_id'] for r in two])
            out[f'{m} {trace}'] = dict(one_hop_all_correct=a1, two_hop_h_correct=h2, n_one=len(one), n_two=len(two),
                                       passes=a1['mean'] >= .9 and h2['mean'] >= .9)
            print(f'{m} {trace}: one-hop all-three {stats.fmt(a1)}, two-hop h {stats.fmt(h2)} -> '
                  f'{"PASS" if out[f"{m} {trace}"]["passes"] else "FAIL"}')
    (BASE / 'dev_check.json').write_text(json.dumps(out, indent=2) + '\n')


if __name__ == '__main__':
    main()
