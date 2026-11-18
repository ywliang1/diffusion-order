"""BFCL analysis (generation venv; reads traces and the official-checker scores).

    python -m experiments.bfcl.analyze --traces test-orig,test-rev [--sanity sanity]
"""
import argparse
import json
from collections import defaultdict

import numpy as np
import pandas as pd

from dlm import report, stats
from dlm.models import ROOT

BASE = ROOT / 'results/bfcl'
MODELS = ('llada', 'dream')
GROUPS = ('L2R', 'R2L', 'random', 'CF')
CLASSES = ('correct', 'parse_error', 'wrong_function', 'wrong_count', 'argument_error')


def load(trace, model):
    t, s = BASE / 'traces' / f'{trace}-{model}.jsonl', BASE / 'scores' / f'{trace}-{model}.jsonl'
    if not (t.exists() and s.exists()):
        return []
    sc = {json.loads(x)['run_id']: json.loads(x) for x in open(s)}
    out = []
    for x in open(t):
        r = json.loads(x)
        r.pop('steps', None)
        r.update({k: v for k, v in sc[r['run_id']].items() if k not in r})
        r['group'] = 'random' if r['order'].startswith('random') else r['order']
        out.append(r)
    return out


def item_means(rows, metric):
    """{(schema, group): {item: mean over seeds}}"""
    d = defaultdict(lambda: defaultdict(list))
    for r in rows:
        d[(r['schema'], r['group'])][r['item']].append(float(metric(r)))
    return {k: {i: float(np.mean(v)) for i, v in it.items()} for k, it in d.items()}


def ratio_ci(rows, num, den, n_boot=stats.B_DEFAULT, seed=stats.SEED_DEFAULT):
    """Sum(num)/sum(den) with an item-clustered bootstrap."""
    per = defaultdict(lambda: [0.0, 0.0])
    for r in rows:
        if den(r):
            per[r['item']][0] += num(r)
            per[r['item']][1] += 1
    keys = sorted(per)
    if not keys:
        return dict(mean=float('nan'), lo=float('nan'), hi=float('nan'))
    a = np.array([per[k][0] for k in keys])
    b = np.array([per[k][1] for k in keys])
    rng = np.random.default_rng(seed)
    idx = rng.integers(len(keys), size=(n_boot, len(keys)))
    boots = a[idx].sum(1) / b[idx].sum(1)
    return dict(mean=float(a.sum() / b.sum()), lo=float(np.quantile(boots, .025)), hi=float(np.quantile(boots, .975)))


def ci(d):
    keys = sorted(d)
    return stats.cluster_bootstrap([d[k] for k in keys], keys)


def metric_table(rows):
    metrics = [('Parse valid', lambda r: r['parse_valid']), ('AST accuracy', lambda r: r['ast_valid']),
               ('Wrong function', lambda r: r['error_class'] == 'wrong_function'),
               ('Argument error', lambda r: r['error_class'] == 'argument_error'),
               ('Wrong count', lambda r: r['error_class'] == 'wrong_count')]
    lines = ['| Schema | Order | ' + ' | '.join(m for m, _ in metrics) + ' | AST among parseable | Hit length limit |',
             '|---|---|' + '---:|' * (len(metrics) + 2)]
    for schema in ('original', 'reversed'):
        for g in GROUPS:
            sub = [r for r in rows if r['schema'] == schema and r['group'] == g]
            if not sub:
                continue
            cells = [stats.fmt(ci(item_means(sub, f)[(schema, g)])) for _, f in metrics]
            amp = stats.fmt(ratio_ci(sub, lambda r: r['ast_valid'], lambda r: r['parse_valid']))
            lim = stats.fmt(ci(item_means(sub, lambda r: r['hit_length_limit'])[(schema, g)]))
            lines.append(f'| {schema} | {g} | ' + ' | '.join(cells) + f' | {amp} | {lim} |')
    return '\n'.join(lines)


def contrasts(rows):
    acc = item_means(rows, lambda r: r['ast_valid'])
    lines = ['| Contrast | Items | AST accuracy difference [95% CI] |', '|---|---:|---:|']
    for schema in ('original', 'reversed'):
        base = acc.get((schema, 'L2R'))
        if not base:
            continue
        for g in ('R2L', 'random', 'CF'):
            other = acc.get((schema, g), {})
            keys = sorted(base.keys() & other.keys())
            if keys:
                d = stats.paired_bootstrap([other[k] for k in keys], [base[k] for k in keys], keys)
                lines.append(f'| {schema}: {g} − L2R | {len(keys)} | {stats.fmt(d)} |')
    for g in GROUPS:
        o, r = acc.get(('original', g), {}), acc.get(('reversed', g), {})
        keys = sorted(o.keys() & r.keys())
        if keys:
            d = stats.paired_bootstrap([r[k] for k in keys], [o[k] for k in keys], keys)
            lines.append(f'| {g}: reversed − original schema | {len(keys)} | {stats.fmt(d)} |')
    return '\n'.join(lines)


def category_table(rows):
    lines = ['| Category | Schema | Order | AST accuracy | Wrong function |', '|---|---|---|---:|---:|']
    for cat in ('simple_python', 'multiple'):
        for schema in ('original', 'reversed'):
            for g in GROUPS:
                sub = [r for r in rows if r['category'] == cat and r['schema'] == schema and r['group'] == g]
                if sub:
                    a = ci(item_means(sub, lambda r: r['ast_valid'])[(schema, g)])
                    w = ci(item_means(sub, lambda r: r['error_class'] == 'wrong_function')[(schema, g)])
                    lines.append(f'| {cat} | {schema} | {g} | {stats.fmt(a)} | {stats.fmt(w)} |')
    return '\n'.join(lines)


def eos_table(rows):
    lines = ['| Schema | Order | First end token commit rank | Mean commit rank of non-content positions | Content tokens |', '|---|---|---:|---:|---:|']
    for schema in ('original', 'reversed'):
        for g in GROUPS:
            sub = [r for r in rows if r['schema'] == schema and r['group'] == g]
            if not sub:
                continue
            fe = item_means([r for r in sub if r['first_end_rank'] is not None], lambda r: r['first_end_rank']).get((schema, g), {})
            nc = item_means([r for r in sub if r['noncontent_mean_rank'] is not None], lambda r: r['noncontent_mean_rank']).get((schema, g), {})
            cl = item_means(sub, lambda r: r['content_len'])[(schema, g)]
            f = lambda d: stats.fmt(ci(d), pct=False) if d else 'n/a'
            lines.append(f'| {schema} | {g} | {f(fe)} | {f(nc)} | {np.mean(list(cl.values())):.1f} |')
    return '\n'.join(lines)


def fn_rank_models(rows):
    sub = [r for r in rows if r['group'] in ('CF', 'random') and r['parse_valid'] and r['fn_rank'] is not None]
    if len(sub) < 50:
        return 'Too few parseable CF/random outputs with an identified function name.'
    df = pd.DataFrame(dict(wrong=[int(r['error_class'] == 'wrong_function') for r in sub], fn_rank=[r['fn_rank'] for r in sub],
                           order=[r['group'] for r in sub], schema=[r['schema'] for r in sub], item=[r['item'] for r in sub]))
    out = [f'Rows: {len(df)} (CF and random orders, parseable, called name identified); wrong-function rate {df.wrong.mean():.3f}.']
    if df.wrong.sum() < 5:
        return '\n'.join(out + ['Fewer than 5 wrong-function errors; no model fitted.'])
    import statsmodels.api as sm
    import statsmodels.formula.api as smf
    from statsmodels.genmod.bayes_mixed_glm import BinomialBayesMixedGLM
    form = 'wrong ~ fn_rank + C(order)' + (' + C(schema)' if df.schema.nunique() > 1 else '')
    try:
        bm = BinomialBayesMixedGLM.from_formula(form, {'item': '0 + C(item)'}, df).fit_vb()
        i = list(bm.model.exog_names).index('fn_rank')
        out.append(f'Mixed logistic (VB, random intercept per item): fn_rank log-odds {bm.fe_mean[i]:+.3f} '
                   f'[{bm.fe_mean[i] - 1.96 * bm.fe_sd[i]:+.3f}, {bm.fe_mean[i] + 1.96 * bm.fe_sd[i]:+.3f}] (posterior mean ± 1.96 sd).')
    except Exception as e:
        out.append(f'Mixed logistic failed: {type(e).__name__}: {e}')
    try:
        g = smf.gee(form, 'item', df, family=sm.families.Binomial(), cov_struct=sm.cov_struct.Exchangeable()).fit()
        lo, hi = g.conf_int().loc['fn_rank']
        out.append(f'GEE logistic (exchangeable within item): fn_rank log-odds {g.params["fn_rank"]:+.3f} [{lo:+.3f}, {hi:+.3f}], p = {g.pvalues["fn_rank"]:.3g}.')
    except Exception as e:
        out.append(f'GEE failed: {type(e).__name__}: {e}')
    return '\n'.join(out)


def run(traces, sanity):
    sections, summary = {}, {}
    for m in MODELS:
        rows = [r for t in traces for r in load(t, m)]
        if not rows:
            continue
        schemas = sorted({r['schema'] for r in rows})
        summary[m] = dict(rows=len(rows), schemas=schemas)
        sections[f'{m}: metrics by schema and order'] = f'Rows: {len(rows)}; schemas: {schemas}.\n\n' + metric_table(rows)
        sections[f'{m}: order and schema contrasts'] = contrasts(rows)
        sections[f'{m}: by category'] = category_table(rows)
        sections[f'{m}: EOS commit rank by order'] = eos_table(rows)
        sections[f'{m}: function-name commit rank vs wrong-function errors'] = fn_rank_models(rows)
    if sanity:
        lines = []
        for m in MODELS:
            rows = load(sanity, m)
            if rows:
                a = ci(item_means(rows, lambda r: r['ast_valid'])[('original', 'CF')])
                p = ci(item_means(rows, lambda r: r['parse_valid'])[('original', 'CF')])
                lines.append(f'- {m}, CF, 100 live_simple items, JSON format: AST accuracy {stats.fmt(a)}, parse valid {stats.fmt(p)} '
                             f'(team reference for Dream greedy: about 64%).')
        sections['Harness sanity check'] = '\n'.join(lines)
    sections['Interpretation limits'] = '\n'.join([
        '- One commit per forward pass on a 64-token canvas; results are not comparable to standard (multi-token-per-step) diffusion decoding.',
        '- Function-name rank analyses are associations, not effects of the rank.',
        '- Blocks not run before the session ended are listed as not run; there are no partial blocks.'])
    dec = ROOT / 'experiments/bfcl/DECISIONS.md'
    sections['Deviations'] = dec.read_text() if dec.exists() else ''
    (BASE / 'report.md').write_text(report.build('BFCL: commitment order on single-turn tool calls', sections,
                                                 required=['Interpretation limits', 'Deviations']))
    (BASE / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    print('wrote', BASE / 'report.md')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--traces', default='test-orig,test-rev')
    ap.add_argument('--sanity', default=None)
    a = ap.parse_args()
    run(a.traces.split(','), a.sanity)


if __name__ == '__main__':
    main()
