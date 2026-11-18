"""Exp 4 analysis: H2 (PF vs DF on dependent-field accuracy, two-hop vs one-hop) and H1 at the
calibrated size (CF commit ranks).

    python -m experiments.exp4.analyze --stage exp4 --trace main
"""
import argparse
import json
from collections import defaultdict

import numpy as np

from dlm import report, stats
from dlm.models import ROOT
from experiments.rq1 import analyze as rq1

MODELS = ('llada', 'dream')
ORDERS = ('CF', 'PF', 'DF', 'L2R', 'R2L', 'random')


def load(stage, trace, model):
    p = ROOT / 'results' / stage / 'traces' / f'{trace}-{model}.jsonl'
    return report.read_required(p)


def item_key(r):
    return (r['table_size'], r['source_id'], r['direction'], r['layout'], r['hop'])


def by_order(rows, metric):
    """{order: {item: value}}; the three random seeds are averaged within each item."""
    acc = defaultdict(lambda: defaultdict(list))
    for r in rows:
        o = 'random' if r['order'].startswith('random') else r['order']
        acc[o][item_key(r)].append(float(r[metric]))
    return {o: {k: float(np.mean(v)) for k, v in d.items()} for o, d in acc.items()}


def accuracy_table(rows):
    lines = ['| Hop | Order | n items | Dependent correct | Prerequisite correct | Both correct |', '|---:|---|---:|---:|---:|---:|']
    tabs = {m: by_order(rows, m) for m in ('dependent_correct', 'prerequisite_correct', 'both_correct')}
    for hop in (2, 1):
        for o in ORDERS:
            if o not in tabs['both_correct']:
                continue
            cells = []
            for m in ('dependent_correct', 'prerequisite_correct', 'both_correct'):
                d = {k: v for k, v in tabs[m][o].items() if k[4] == hop}
                cells.append(stats.fmt(stats.cluster_bootstrap(list(d.values()), [k[1] for k in d])))
            lines.append(f'| {hop} | {o} | {len(d)} | ' + ' | '.join(cells) + ' |')
    return '\n'.join(lines)


def h2(rows):
    dep = by_order(rows, 'dependent_correct')
    pf, df = dep['PF'], dep['DF']
    out = {}
    for hop in (2, 1):
        keys = sorted(k for k in pf if k[4] == hop and k in df)
        out[hop] = dict(gap=stats.paired_bootstrap([pf[k] for k in keys], [df[k] for k in keys], [k[1] for k in keys]),
                        mcnemar=stats.mcnemar([pf[k] > .5 for k in keys], [df[k] > .5 for k in keys]), n=len(keys))
    two = {k[:4]: pf[k] - df[k] for k in pf if k[4] == 2 and k in df}
    one = {k[:4]: pf[k] - df[k] for k in pf if k[4] == 1 and k in df}
    keys = sorted(two.keys() & one.keys())
    out['interaction'] = stats.cluster_bootstrap([two[k] - one[k] for k in keys], [k[1] for k in keys])
    g, i = out[2]['gap'], out['interaction']
    if g['lo'] > 0 and i['lo'] > 0:
        v = 'supported (two-hop PF − DF > 0 and larger than in one-hop controls)'
    elif g['hi'] <= 0:
        v = 'contradicted (two-hop PF − DF not above 0)'
    elif g['lo'] > 0:
        v = 'partly supported (two-hop PF − DF > 0, but the hop × order interaction CI includes 0)'
    else:
        v = 'inconclusive'
    out['verdict'] = v
    return out


def h2_table(res):
    lines = ['| Hop | Items | PF − DF dependent accuracy | Both right | Both wrong | Only PF right | Only DF right | McNemar p |',
             '|---:|---:|---:|---:|---:|---:|---:|---:|']
    for hop in (2, 1):
        r = res[hop]
        mc = r['mcnemar']
        lines.append(f"| {hop} | {r['n']} | {stats.fmt(r['gap'])} | {mc['both']} | {mc['neither']} | {mc['only_a']} | {mc['only_b']} | {mc['p']:.3g} |")
    lines.append(f"\nHop × order interaction, (PF − DF | two-hop) − (PF − DF | one-hop): {stats.fmt(res['interaction'])} points.")
    return '\n'.join(lines)


def h1(rows):
    df = rq1.field_frame([r for r in rows if r['order'] == 'CF'])
    two = df[df.hop == 2]
    fit = stats.mixedlm(two, 'rank ~ role_c + pos_c + field_c', 'source')
    boot = dict(position=rq1.contrast(two, 'position', 'right'), role=rq1.contrast(two, 'role', 'dependent'),
                field=rq1.contrast(two, 'field', 'B'))
    c, b = fit['coefs']['pos_c'], boot['position']
    if (c['lo'] > 0 or c['hi'] < 0) and (b['lo'] > 0 or b['hi'] < 0):
        v = 'supported'
    elif -rq1.MARGIN <= b['lo'] and b['hi'] <= rq1.MARGIN:
        v = f'contradicted (position effect within ±{rq1.MARGIN})'
    else:
        v = 'inconclusive'
    lines = ['| Effect | Mixed model coef [95% CI] | Bootstrap [95% CI] |', '|---|---:|---:|']
    for name, key, coef in (('Position (right − left)', 'position', 'pos_c'), ('Role (dependent − prerequisite)', 'role', 'role_c'),
                            ('Field (b − a)', 'field', 'field_c')):
        k = fit['coefs'][coef]
        lines.append(f"| {name} | {k['coef']:+.3f} [{k['lo']:+.3f}, {k['hi']:+.3f}] | {rq1.f3(boot[key])} |")
    return v, '\n'.join(lines), dict(mixedlm=fit, bootstrap=boot)


def run(stage, trace):
    sections, summary = {}, {}
    for m in MODELS:
        rows = load(stage, trace, m)
        if not rows:
            continue
        meta = {(r['meta']['hostname'], r['meta']['gpu_name'], r['meta']['git_commit']) for r in rows}
        sizes = sorted({r['table_size'] for r in rows})
        res = h2(rows)
        v1, t1, s1 = h1(rows)
        cf = [r for r in rows if r['order'] == 'CF']
        flip = np.mean([r['min_cf_margin'] is not None and r['min_cf_margin'] < rq1.FLIP for r in cf])
        summary[m] = dict(sizes=sizes, h2=dict(verdict=res['verdict'], two_hop=res[2]['gap'], one_hop=res[1]['gap'],
                                               interaction=res['interaction']), h1=dict(verdict=v1, **s1), flip_fraction=float(flip))
        sections[f'{m}: summary'] = (f'Table size {sizes}; rows {len(rows)}; hosts/GPUs/commits {sorted(meta)}.\n\n'
                                    f'- **H2: {res["verdict"]}.**\n- **H1 at this size: {v1}.**\n'
                                    f'- CF traces with a margin below {rq1.FLIP}: {100 * flip:.1f}%.')
        sections[f'{m}: H2 (dependent-field accuracy, PF vs DF)'] = h2_table(res)
        sections[f'{m}: accuracy by order'] = accuracy_table(rows)
        sections[f'{m}: H1 (CF commit rank, two-hop)'] = t1
        sections[f'{m}: CF cells'] = rq1.cell_table(cf)
        sections[f'{m}: alignment'] = rq1.alignment(cf)
    sections['Interpretation limits'] = '\n'.join([
        '- Table size is calibrated per model; between-model comparisons are descriptive.',
        '- Single-token values: a field rank is 0 or 1, and the role × position interaction is not identifiable (see RQ1 study).',
        '- Random orders are averaged over three seeds within each item before any comparison.'])
    dec = ROOT / 'experiments' / stage / 'DECISIONS.md'
    sections['Deviations'] = dec.read_text() if dec.exists() else ''
    base = ROOT / 'results' / stage
    (base / 'report.md').write_text(report.build(f'{stage}: role × layout × hop with PF/DF', sections,
                                                 required=['Interpretation limits', 'Deviations']))
    (base / 'summary.json').write_text(json.dumps(summary, indent=2, default=float) + '\n')
    print('wrote', base / 'report.md', {m: (s['h2']['verdict'], s['h1']['verdict']) for m, s in summary.items()})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--stage', default='exp4')
    ap.add_argument('--trace', default='main')
    a = ap.parse_args()
    run(a.stage, a.trace)


if __name__ == '__main__':
    main()
