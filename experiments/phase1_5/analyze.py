"""Phase 1.5 analysis: gate, pre-registered variant selection (dev), and the report (dev or test).

    python -m experiments.phase1_5.analyze --split dev  --traces dev,dev-nochat
    python -m experiments.phase1_5.analyze --split test --traces test
"""
import argparse
import json
from collections import Counter, defaultdict

from dlm import report, stats
from dlm.models import ROOT
from dlm.scoring import CATEGORIES

BASE = ROOT / 'results/phase1_5'
MODELS = ('llada', 'dream')
ORDERS = ('A-first', 'B-first', 'CF')
CONDS = ('Direct', 'Shared-path', 'Separate-path')
GATE_SIZES = (4, 8)
PREFERENCE = ('V1', 'V4', 'V2', 'V3')
DIRECT_MIN, PATH_LO, PATH_HI = .90, .40, .80


def load(traces):
    rows = []
    for t in traces:
        for m in MODELS:
            p = BASE / 'traces' / f'{t}-{m}.jsonl'
            if p.exists():
                rows += [dict(json.loads(x), model=m) for x in open(p) if x.strip()]
    ids = [r['run_id'] for r in rows]
    if len(ids) != len(set(ids)):
        raise ValueError('duplicate run_ids')
    return rows


def index(rows):
    d = defaultdict(list)
    for r in rows:
        d[(r['model'], r['variant'], r['experiment'], r['table_size'], r['condition'], r['order'])].append(r)
    return d


def ci(rs, key='B_correct'):
    return stats.cluster_bootstrap([float(r[key]) for r in rs], [r['source_id'] for r in rs])


def gate(ix, model, variant, size):
    out = {}
    for o in ORDERS:
        c = ci(ix[(model, variant, 2, size, 'Direct', o)])
        out[f'direct_{o}'] = dict(ci=c, ok=c['mean'] >= DIRECT_MIN)
    for cond, key in (('Shared-path', 'shared'), ('Separate-path', 'separate')):
        pooled = [r for o in ORDERS for r in ix[(model, variant, 2, size, cond, o)]]
        c = ci(pooled)
        ok = c['lo'] > 1 / size and (PATH_LO <= c['mean'] <= PATH_HI if key == 'shared' else True)
        out[key] = dict(ci=c, ok=ok)
    return out


def variant_gate(ix, variant):
    g = {(m, n): gate(ix, m, variant, n) for m in MODELS for n in GATE_SIZES}
    met = sum(v['ok'] for x in g.values() for v in x.values())
    total = sum(len(x) for x in g.values())
    min_direct = min(v['ci']['mean'] for x in g.values() for k, v in x.items() if k.startswith('direct'))
    return dict(cells=g, passed=met == total, met=met, total=total, min_direct=min_direct)


def select(ix, variants):
    """Pre-registered rule: first passing variant in V1, V4, V2, V3 with the chat template; if none,
    the '-nochat' arm of the closest variant if it passes; otherwise no variant."""
    gates = {v: variant_gate(ix, v) for v in variants}
    base = [v for v in PREFERENCE if v in gates]
    passing = [v for v in base if gates[v]['passed']]
    closest = max(base, key=lambda v: (gates[v]['met'], gates[v]['min_direct']))
    if passing:
        choice, why = passing[0], f'{passing[0]} is the first passing variant in the order V1, V4, V2, V3'
    elif f'{closest}-nochat' in gates and gates[f'{closest}-nochat']['passed']:
        choice, why = f'{closest}-nochat', f'no chat-template variant passed; {closest}-nochat (closest variant without the template) passed'
    else:
        choice, why = None, f'no variant passed; closest is {closest} ({gates[closest]["met"]}/{gates[closest]["total"]} criteria)'
    return dict(choice=choice, reason=why, closest=closest, passing=passing, gates=gates)


def pct(c):
    return stats.fmt(c)


def accuracy_table(ix, model, variant, sizes):
    lines = ['| Size | Condition | Order | A | B | Both |', '|---:|---|---|---:|---:|---:|']
    for n in sizes:
        for cond in CONDS:
            for o in ORDERS:
                rs = ix[(model, variant, 2, n, cond, o)]
                if rs:
                    lines.append(f'| {n} | {cond} | {o} | {pct(ci(rs, "A_correct"))} | {pct(ci(rs))} | {pct(ci(rs, "both_correct"))} |')
    return '\n'.join(lines)


def gate_table(g):
    lines = ['| Model | Size | Direct A-first | Direct B-first | Direct CF | Shared (avg of orders) | Separate (avg of orders) | Pass |',
             '|---|---:|---:|---:|---:|---:|---:|---|']
    for (m, n), cell in g['cells'].items():
        f = lambda k: ('' if cell[k]['ok'] else '✗ ') + pct(cell[k]['ci'])
        lines.append(f"| {m} | {n} | {f('direct_A-first')} | {f('direct_B-first')} | {f('direct_CF')} | {f('shared')} | {f('separate')} | "
                     f"{'yes' if all(v['ok'] for v in cell.values()) else 'no'} |")
    return '\n'.join(lines)


def taxonomy_table(ix, model, variant, sizes, exp=2, arms=ORDERS, conds=CONDS):
    lines = ['| Condition | Order | n | ' + ' | '.join(CATEGORIES) + ' |', '|---|---|---:|' + '---:|' * len(CATEGORIES)]
    for cond in conds:
        for o in arms:
            rs = [r for n in sizes for r in ix[(model, variant, exp, n, cond, o)]]
            if rs:
                c = Counter(r['taxonomy']['B'] for r in rs)
                lines.append(f'| {cond} | {o} | {len(rs)} | ' + ' | '.join(str(c[k]) for k in CATEGORIES) + ' |')
    return '\n'.join(lines)


def paired_table(ix, model, variant, sizes):
    lines = ['| Size | Condition | Both right | Both wrong | Only A-first right | Only B-first right | McNemar p | A-first − B-first B accuracy |',
             '|---:|---|---:|---:|---:|---:|---:|---:|']
    for n in sizes:
        for cond in CONDS:
            a = {r['source_id']: r for r in ix[(model, variant, 2, n, cond, 'A-first')]}
            b = {r['source_id']: r for r in ix[(model, variant, 2, n, cond, 'B-first')]}
            keys = sorted(a.keys() & b.keys())
            if not keys:
                continue
            mc = stats.mcnemar([a[k]['B_correct'] for k in keys], [b[k]['B_correct'] for k in keys])
            gap = stats.paired_bootstrap([a[k]['B_correct'] for k in keys], [b[k]['B_correct'] for k in keys], keys)
            lines.append(f"| {n} | {cond} | {mc['both']} | {mc['neither']} | {mc['only_a']} | {mc['only_b']} | {mc['p']:.3g} | {pct(gap)} |")
    return '\n'.join(lines)


def interaction_table(ix, model, variant, sizes):
    lines = ['| Size | Shared A-first − B-first | Separate A-first − B-first | Shared − Separate |', '|---:|---:|---:|---:|']
    for n in sizes:
        per = {}
        for cond in ('Shared-path', 'Separate-path'):
            a = {r['source_id']: r['B_correct'] for r in ix[(model, variant, 2, n, cond, 'A-first')]}
            b = {r['source_id']: r['B_correct'] for r in ix[(model, variant, 2, n, cond, 'B-first')]}
            per[cond] = {k: a[k] - b[k] for k in a.keys() & b.keys()}
        keys = sorted(per['Shared-path'].keys() & per['Separate-path'].keys())
        if not keys:
            continue
        sh = stats.cluster_bootstrap([per['Shared-path'][k] for k in keys], keys)
        se = stats.cluster_bootstrap([per['Separate-path'][k] for k in keys], keys)
        it = stats.cluster_bootstrap([per['Shared-path'][k] - per['Separate-path'][k] for k in keys], keys)
        lines.append(f'| {n} | {pct(sh)} | {pct(se)} | {pct(it)} |')
    return '\n'.join(lines)


def exp3_tables(ix, model, variant, sizes):
    lines = ['| Size | Condition | Masked B | Gold − Masked | Predicted − Masked | Wrong − Masked | Wrong B = wrong row\'s B |',
             '|---:|---|---:|---:|---:|---:|---:|']
    for n in sizes:
        for cond in ('Shared-path', 'Separate-path'):
            d = {o: {r['source_id']: r for r in ix[(model, variant, 3, n, cond, o)]} for o in ('Masked', 'Gold', 'Predicted', 'Wrong')}
            if not d['Masked']:
                continue
            keys = sorted(d['Masked'])
            gaps = [stats.paired_bootstrap([d[o][k]['B_correct'] for k in keys], [d['Masked'][k]['B_correct'] for k in keys], keys)
                    for o in ('Gold', 'Predicted', 'Wrong')]
            alt = stats.cluster_bootstrap([float(d['Wrong'][k]['B_matches_alternative']) for k in keys], keys)
            lines.append(f"| {n} | {cond} | {pct(ci(list(d['Masked'].values())))} | {pct(gaps[0])} | {pct(gaps[1])} | {pct(gaps[2])} | {pct(alt)} |")
    return '\n'.join(lines)


def step0_table(ix, model, variant, sizes):
    lines = ['| Size | Condition | Mean A top-1 | Mean B top-1 | CF commits A first | CF min margin < 0.02 |', '|---:|---|---:|---:|---:|---:|']
    for n in sizes:
        for cond in CONDS:
            rs = ix[(model, variant, 2, n, cond, 'CF')]
            if not rs:
                continue
            a = sum(r['step0']['A']['top5_probs'][0] for r in rs) / len(rs)
            b = sum(r['step0']['B']['top5_probs'][0] for r in rs) / len(rs)
            fa = sum(r['first_field'] == 'A' for r in rs) / len(rs)
            low = sum(min(s['cf_margin'] for s in r['steps'] if s['cf_margin'] is not None) < .02 for r in rs) / len(rs)
            lines.append(f'| {n} | {cond} | {a:.3f} | {b:.3f} | {fa:.3f} | {low:.3f} |')
    return '\n'.join(lines)


def norm_counts(rows):
    c = Counter()
    for r in rows:
        for f, s in r['fields'].items():
            c[(r['model'], f)] += s['changed_by_norm']
    return ', '.join(f'{m} {f}: {n}' for (m, f), n in sorted(c.items())) or 'none'


def run(split, traces):
    rows = load(traces)
    ix = index(rows)
    variants = sorted({r['variant'] for r in rows})
    sizes = sorted({r['table_size'] for r in rows})
    sections = {}
    meta = {(r['meta']['hostname'], r['meta']['gpu_name'], r['meta']['git_commit']) for r in rows}
    sections['Run summary'] = '\n'.join([
        f'- Split: {split}; traces: {", ".join(traces)}; rows: {len(rows)}; variants: {", ".join(variants)}; sizes: {sizes}.',
        f'- Hosts / GPUs / commits: {sorted(meta)}.',
        f'- Answers whose correctness changed under whitespace normalization: {norm_counts(rows)}.'])
    out = {}
    if split == 'dev':
        sel = select(ix, variants)
        out = dict(choice=sel['choice'], reason=sel['reason'], closest=sel['closest'], passing=sel['passing'],
                   gates={v: dict(passed=g['passed'], met=g['met'], total=g['total'], min_direct=g['min_direct'],
                                  cells={f'{m}-{n}': {k: dict(ok=x['ok'], **x['ci']) for k, x in c.items()} for (m, n), c in g['cells'].items()})
                          for v, g in sel['gates'].items()})
        sections['Selection'] = f"**Choice: {sel['choice'] or 'none'}.** {sel['reason']}."
        for v in variants:
            sections[f'Gate: {v}'] = gate_table(sel['gates'][v])
    for m in MODELS:
        for v in variants:
            if not any(k[0] == m and k[1] == v for k in ix):
                continue
            sections[f'{m} {v}: accuracy'] = accuracy_table(ix, m, v, sizes)
            sections[f'{m} {v}: B error taxonomy (all sizes)'] = taxonomy_table(ix, m, v, sizes)
            sections[f'{m} {v}: paired A-first vs B-first (B correct)'] = paired_table(ix, m, v, sizes)
            sections[f'{m} {v}: order × path interaction'] = interaction_table(ix, m, v, sizes)
            sections[f'{m} {v}: step-0 confidence and CF'] = step0_table(ix, m, v, sizes)
            if split == 'test':
                sections[f'{m} {v}: gate on test'] = gate_table(variant_gate(ix, v))
                sections[f'{m} {v}: Exp 3 prefilled A'] = exp3_tables(ix, m, v, sizes)
                sections[f'{m} {v}: Exp 3 B error taxonomy'] = taxonomy_table(ix, m, v, sizes, exp=3, arms=('Masked', 'Gold', 'Predicted', 'Wrong'),
                                                                               conds=('Shared-path', 'Separate-path'))
    sections['Interpretation limits'] = '\n'.join([
        '- A is always left of B in this stage, so CF order preference is not separated from position (Exp 4).',
        '- Separate-path is held only to a chance-level gate (team decision B).',
        '- Dev results inform only the pre-registered variant choice; test sources never inform choices.'])
    sections['Deviations'] = (ROOT / 'experiments/phase1_5/DECISIONS.md').read_text() if (ROOT / 'experiments/phase1_5/DECISIONS.md').exists() else ''
    title = f'Phase 1.5 {split} report'
    name = 'dev_report.md' if split == 'dev' else 'report.md'
    (BASE / name).write_text(report.build(title, sections, required=['Interpretation limits', 'Deviations']))
    if out:
        (BASE / 'dev_selection.json').write_text(json.dumps(out, indent=2) + '\n')
    print(f'wrote {BASE / name}', json.dumps({k: out[k] for k in ('choice', 'reason')}) if out else '')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--split', choices=['dev', 'test'], required=True)
    ap.add_argument('--traces', required=True)
    a = ap.parse_args()
    run(a.split, a.traces.split(','))


if __name__ == '__main__':
    main()
