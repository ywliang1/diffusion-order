"""Row-level comparison of the Stage 3 rerun (results/stage3_rerun) with the original run (results/stage3).

    python -m experiments.stage3.compare_rerun
"""
import json

from dlm import report
from dlm.models import ROOT


def key_steps(r):
    return [(s['pos'], s['token_id']) for s in r['steps']]


def main():
    out = {}
    for m in ('llada', 'dream'):
        for k in (2, 3):
            a = {r['run_id']: r for r in report.read_required(ROOT / f'results/stage3/traces/main-k{k}-{m}.jsonl')}
            b = {r['run_id']: r for r in report.read_required(ROOT / f'results/stage3_rerun/traces/main-k{k}-{m}.jsonl')}
            ids = sorted(a.keys() & b.keys())
            same_steps = sum(key_steps(a[i]) == key_steps(b[i]) for i in ids)
            same_probs = sum([s['prob'] for s in a[i]['steps']] == [s['prob'] for s in b[i]['steps']] for i in ids)
            same_dep = sum(a[i]['dependent_correct'] == b[i]['dependent_correct'] for i in ids)
            gpus = sorted({r['meta']['gpu_name'] for r in b.values()} | {r['meta']['gpu_name'] for r in a.values()})
            out[f'{m} k={k}'] = dict(rows_original=len(a), rows_rerun=len(b), matched_ids=len(ids),
                                     identical_commit_sequence=same_steps, identical_probabilities=same_probs,
                                     same_dependent_correctness=same_dep, gpus=gpus,
                                     commits=sorted({r['meta']['git_commit'][:7] for r in b.values()}))
            print(m, k, out[f'{m} k={k}'])
    (ROOT / 'results/stage3_rerun/compare.json').write_text(json.dumps(out, indent=2) + '\n')


if __name__ == '__main__':
    main()
