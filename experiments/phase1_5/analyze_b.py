"""Phase 1.5b analysis: per-model size calibration (dev) and the report (dev or test).

    python -m experiments.phase1_5.analyze_b --split dev  --traces dev
    python -m experiments.phase1_5.analyze_b --split test --traces test
"""
import argparse
import json

from dlm import report
from dlm.models import ROOT
from experiments.phase1_5 import analyze as an

BASE = ROOT / 'results/phase1_5b'
# Pre-registered search order per model: the first (variant, size) that passes is frozen.
SEARCH = (('V2', 16), ('V2', 32), ('V2', 64), ('V2', 128), ('V2d', 16), ('V2d', 32), ('V2d', 64))


def cell_pass(ix, model, variant, size):
    g = an.gate(ix, model, variant, size)
    return all(v['ok'] for v in g.values()), g


def select(ix, models=an.MODELS):
    out = {}
    for m in models:
        tried = []
        choice = None
        for v, n in SEARCH:
            if not ix.get((m, v, 2, n, 'Direct', 'CF')):
                continue
            ok, g = cell_pass(ix, m, v, n)
            tried.append(dict(variant=v, size=n, passed=ok, met=sum(x['ok'] for x in g.values()),
                              cells={k: dict(ok=x['ok'], **x['ci']) for k, x in g.items()}))
            if ok and choice is None:
                choice = dict(variant=v, size=n)
        out[m] = dict(choice=choice, tried=tried)
    return out


def gate_rows(sel):
    lines = ['| Model | Variant | Size | Direct A-first | Direct B-first | Direct CF | Shared (avg) | Separate (avg) | Pass |',
             '|---|---|---:|---:|---:|---:|---:|---:|---|']
    for m, s in sel.items():
        for t in s['tried']:
            c = t['cells']
            f = lambda k: ('' if c[k]['ok'] else '✗ ') + an.stats.fmt(c[k])
            lines.append(f"| {m} | {t['variant']} | {t['size']} | {f('direct_A-first')} | {f('direct_B-first')} | {f('direct_CF')} | "
                         f"{f('shared')} | {f('separate')} | {'yes' if t['passed'] else 'no'} |")
    return '\n'.join(lines)


def run(split, traces):
    an.BASE = BASE
    rows = an.load(traces)
    ix = an.index(rows)
    sections = {}
    meta = {(r['meta']['hostname'], r['meta']['gpu_name'], r['meta']['git_commit']) for r in rows}
    sections['Run summary'] = '\n'.join([
        f'- Split: {split}; traces: {", ".join(traces)}; rows: {len(rows)}.',
        f'- Hosts / GPUs / commits: {sorted(meta)}.',
        f'- Answers whose correctness changed under whitespace normalization: {an.norm_counts(rows)}.',
        '- Each model is calibrated separately; comparisons between models are descriptive only.'])
    sel = select(ix)
    if split == 'dev':
        sections['Selection'] = '\n'.join(f"- {m}: " + (f"**{s['choice']['variant']} at size {s['choice']['size']}**" if s['choice'] else '**none passed**')
                                          for m, s in sel.items())
        (BASE / 'dev_selection.json').write_text(json.dumps(sel, indent=2) + '\n')
    sections['Gate'] = gate_rows(sel)
    for m in an.MODELS:
        cells = sorted({(k[1], k[3]) for k in ix if k[0] == m})
        for v in sorted({c[0] for c in cells}):
            sizes = sorted(n for vv, n in cells if vv == v)
            sections[f'{m} {v}: accuracy'] = an.accuracy_table(ix, m, v, sizes)
            sections[f'{m} {v}: B error taxonomy (all sizes)'] = an.taxonomy_table(ix, m, v, sizes)
            sections[f'{m} {v}: paired A-first vs B-first (B correct)'] = an.paired_table(ix, m, v, sizes)
            sections[f'{m} {v}: order × path interaction'] = an.interaction_table(ix, m, v, sizes)
            sections[f'{m} {v}: step-0 confidence and CF'] = an.step0_table(ix, m, v, sizes)
            if split == 'test':
                sections[f'{m} {v}: Exp 3 prefilled A'] = an.exp3_tables(ix, m, v, sizes)
                sections[f'{m} {v}: Exp 3 B error taxonomy'] = an.taxonomy_table(
                    ix, m, v, sizes, exp=3, arms=an.BRANCHES if hasattr(an, 'BRANCHES') else ('Masked', 'Gold', 'Predicted', 'Wrong'),
                    conds=('Shared-path', 'Separate-path'))
    sections['Interpretation limits'] = '\n'.join([
        '- Table size is calibrated per model, so the two models are compared descriptively, not as a test.',
        '- A is always left of B in this stage; position is studied separately (RQ1 study, Exp 4).',
        '- Separate-path is held only to a chance-level gate (team decision B).'])
    dec = ROOT / 'experiments/phase1_5/DECISIONS.md'
    sections['Deviations'] = dec.read_text() if dec.exists() else ''
    name = 'dev_report.md' if split == 'dev' else 'report.md'
    (BASE / name).write_text(report.build(f'Phase 1.5b {split} report', sections, required=['Interpretation limits', 'Deviations']))
    print(f'wrote {BASE / name}', json.dumps({m: s['choice'] for m, s in sel.items()}))
    return sel


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--split', choices=['dev', 'test'], required=True)
    ap.add_argument('--traces', required=True)
    a = ap.parse_args()
    run(a.split, a.traces.split(','))


if __name__ == '__main__':
    main()
