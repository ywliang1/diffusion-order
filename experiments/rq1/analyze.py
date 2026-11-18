"""RQ1 analysis: role x position effects on normalized CF commit rank.

    python -m experiments.rq1.analyze --trace main
"""
import argparse
import json
from collections import defaultdict

import numpy as np
import pandas as pd

from dlm import report, stats
from dlm.models import ROOT

BASE = ROOT / 'results/rq1'
MODELS = ('llada', 'dream')
MARGIN = 0.10          # pre-registered equivalence margin on the position effect (rank units, 0..1)
FLIP = 0.02            # CF margin below which a trace is flip-sensitive


def load(trace, model):
    p = BASE / 'traces' / f'{trace}-{model}.jsonl'
    return report.read_required(p)


def field_frame(rows):
    """One row per (trace, field): rank, role, position, field, with +-0.5 codes."""
    out = []
    for r in rows:
        for f in ('A', 'B'):
            out.append(dict(source=r['source_id'], trace=r['run_id'], hop=r['hop'], direction=r['direction'], layout=r['layout'],
                            field=f, role=r['roles'][f], position=r['position'][f], rank=r['ranks'][f],
                            correct=r['fields'][f]['correct'], both=r['both_correct'], margin=r['min_cf_margin'],
                            role_c=.5 if r['roles'][f] == 'dependent' else -.5,
                            pos_c=.5 if r['position'][f] == 'right' else -.5,
                            field_c=.5 if f == 'B' else -.5))
    return pd.DataFrame(out)


def contrast(df, col, hi):
    """Cell-balanced contrast: mean rank at col==hi minus col!=hi, averaged within source, bootstrapped by source."""
    per = defaultdict(lambda: [[], []])
    for s, v, x in zip(df['source'], df[col], df['rank']):
        per[s][0 if v == hi else 1].append(x)
    keys = sorted(k for k, v in per.items() if v[0] and v[1])
    vals = [np.mean(per[k][0]) - np.mean(per[k][1]) for k in keys]
    return stats.cluster_bootstrap(vals, keys)


def interaction(df):
    per = defaultdict(lambda: defaultdict(list))
    for s, role, pos, x in zip(df['source'], df['role'], df['position'], df['rank']):
        per[s][(role, pos)].append(x)
    keys = [k for k, v in per.items() if len(v) == 4]
    m = lambda k, c: np.mean(per[k][c])
    vals = [(m(k, ('dependent', 'right')) - m(k, ('dependent', 'left'))) - (m(k, ('prerequisite', 'right')) - m(k, ('prerequisite', 'left')))
            for k in keys]
    return stats.cluster_bootstrap(vals, keys)


def effects(df):
    fit = stats.mixedlm(df, 'rank ~ role_c * pos_c + field_c', 'source')
    boot = dict(position=contrast(df, 'position', 'right'), role=contrast(df, 'role', 'dependent'),
                field=contrast(df, 'field', 'B'), interaction=interaction(df))
    return fit, boot


def verdict(fit, boot):
    c, b = fit['coefs']['pos_c'], boot['position']
    if (c['lo'] > 0 or c['hi'] < 0) and (b['lo'] > 0 or b['hi'] < 0):
        return 'supported (position effect excludes 0 in both the mixed model and the bootstrap)'
    if -MARGIN <= b['lo'] and b['hi'] <= MARGIN:
        return f'contradicted (bootstrap CI of the position effect lies within ±{MARGIN})'
    return 'inconclusive'


def f3(c):
    return f"{c['mean']:+.3f} [{c['lo']:+.3f}, {c['hi']:+.3f}]"


def effect_table(fit, boot):
    lines = ['| Effect | Mixed model coef [95% CI] | p | Bootstrap contrast [95% CI] |', '|---|---:|---:|---:|']
    for name, key in (('Position (right − left)', 'position'), ('Role (dependent − prerequisite)', 'role'),
                      ('Field (b − a)', 'field'), ('Role × position', 'interaction')):
        coef = fit['coefs'][{'position': 'pos_c', 'role': 'role_c', 'field': 'field_c', 'interaction': 'role_c:pos_c'}[key]]
        lines.append(f"| {name} | {coef['coef']:+.3f} [{coef['lo']:+.3f}, {coef['hi']:+.3f}] | {coef['p']:.3g} | {f3(boot[key])} |")
    lines.append(f"\nMixed model: {fit['n_obs']} field rows, {fit['n_groups']} sources, optimizer {fit['optimizer']}, "
                 f"converged {fit['converged']}, source variance {fit['group_var']:.4f}, residual variance {fit['resid_var']:.4f}.")
    return '\n'.join(lines)


def cell_table(rows):
    lines = ['| Hop | Query direction | Layout | n | Left field first | Prerequisite first | a correct | b correct | Both correct |',
             '|---:|---|---|---:|---:|---:|---:|---:|---:|']
    for hop in (2, 1):
        for d in ('a', 'b'):
            for lay in ('ab', 'ba'):
                rs = [r for r in rows if r['hop'] == hop and r['direction'] == d and r['layout'] == lay]
                if not rs:
                    continue
                cl = [r['source_id'] for r in rs]
                g = lambda k: stats.fmt(stats.cluster_bootstrap([float(r[k]) for r in rs], cl))
                lines.append(f"| {hop} | {d} | {lay} | {len(rs)} | {g('left_first')} | {g('prerequisite_first')} | "
                             f"{g('A_correct')} | {g('B_correct')} | {g('both_correct')} |")
    return '\n'.join(lines)


def alignment(rows):
    two = {(r['source_id'], r['direction'], r['layout']): r['prerequisite_first'] for r in rows if r['hop'] == 2}
    one = {(r['source_id'], r['direction'], r['layout']): r['prerequisite_first'] for r in rows if r['hop'] == 1}
    keys = sorted(two.keys() & one.keys())
    cl = [k[0] for k in keys]
    a = stats.cluster_bootstrap([float(two[k]) for k in keys], cl)
    b = stats.cluster_bootstrap([float(one[k]) for k in keys], cl)
    d = stats.paired_bootstrap([float(two[k]) for k in keys], [float(one[k]) for k in keys], cl)
    return (f'Prerequisite field committed first: two-hop {stats.fmt(a)}, one-hop (direction field) {stats.fmt(b)}, '
            f'difference {stats.fmt(d)} percentage points.')


def run(trace):
    sections, summary = {}, {}
    for m in MODELS:
        rows = [r for r in load(trace, m) if r['order'] == 'CF']
        if not rows:
            continue
        meta = {(r['meta']['hostname'], r['meta']['gpu_name'], r['meta']['git_commit']) for r in rows}
        df = field_frame(rows)
        two, one = df[df.hop == 2], df[df.hop == 1]
        fit, boot = effects(two)
        v = verdict(fit, boot)
        summary[m] = dict(verdict=v, mixedlm=fit, bootstrap=boot)
        flip = np.mean([r['min_cf_margin'] is not None and r['min_cf_margin'] < FLIP for r in rows])
        stable = two[two.margin >= FLIP]
        correct = two[two.both]
        fs, bs = effects(stable)
        fc, bc = effects(correct)
        f1, b1 = effects(one)
        sections[f'{m}: H1 verdict'] = f'**{v}.** Rows: {len(rows)}; hosts/GPUs/commits: {sorted(meta)}.'
        sections[f'{m}: two-hop effects on normalized CF rank (primary)'] = effect_table(fit, boot)
        sections[f'{m}: cells'] = cell_table(rows)
        sections[f'{m}: alignment'] = alignment(rows)
        sections[f'{m}: CF margins'] = (f'Traces with a CF margin below {FLIP}: {100 * flip:.1f}%. '
                                       f'Position effect without them: {f3(bs["position"])}; '
                                       f'on fully correct two-hop traces only: {f3(bc["position"])}.')
        sections[f'{m}: one-hop control effects (descriptive)'] = effect_table(f1, b1)
    sections['Interpretation limits'] = '\n'.join([
        '- Size 8, V2 format, single-token values: with two content tokens a field rank is 0 (first) or 1 (second).',
        '- Accuracy is near ceiling here by design (no 40–80% band); RQ2 is not addressed by this study.',
        '- Ranks of a and b sum to 1 within a trace, so the per-source random intercept is expected to be near zero; '
        'the source-clustered bootstrap is reported beside every mixed-model estimate.',
        '- Models are analysed separately; between-model differences are descriptive.'])
    dec = ROOT / 'experiments/rq1/DECISIONS.md'
    sections['Deviations'] = dec.read_text() if dec.exists() else ''
    (BASE / 'report.md').write_text(report.build('RQ1 role × layout commit-rank study', sections,
                                                 required=['Interpretation limits', 'Deviations']))
    (BASE / 'summary.json').write_text(json.dumps(summary, indent=2, default=float) + '\n')
    print('wrote', BASE / 'report.md', {m: s['verdict'] for m, s in summary.items()})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--trace', default='main')
    run(ap.parse_args().trace)


if __name__ == '__main__':
    main()
