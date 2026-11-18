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


def load(trace, model, lenient=False):
    t = BASE / 'traces' / f'{trace}-{model}.jsonl'
    s = BASE / 'scores' / f"{trace}-{model}{'-lenient' if lenient else ''}.jsonl"
    if not t.exists():
        return []          # block not run: reported as such, never as partial results (PREREG)
    if not s.exists():
        raise FileNotFoundError(f'trace {t} exists but its scores {s} do not; run score.py first')
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
    # Not statsmodels.api: it imports statsmodels.tsa, which breaks under pandas 3 (deprecate_kwarg signature).
    from statsmodels.genmod import cov_struct, families
    from statsmodels.genmod.bayes_mixed_glm import BinomialBayesMixedGLM
    from statsmodels.genmod.generalized_estimating_equations import GEE
    form = 'wrong ~ fn_rank + C(order)' + (' + C(schema)' if df.schema.nunique() > 1 else '')
    try:
        bm = BinomialBayesMixedGLM.from_formula(form, {'item': '0 + C(item)'}, df).fit_vb()
        i = list(bm.model.exog_names).index('fn_rank')
        out.append(f'Mixed logistic (VB, random intercept per item): fn_rank log-odds {bm.fe_mean[i]:+.3f} '
                   f'[{bm.fe_mean[i] - 1.96 * bm.fe_sd[i]:+.3f}, {bm.fe_mean[i] + 1.96 * bm.fe_sd[i]:+.3f}] (posterior mean ± 1.96 sd).')
    except Exception as e:
        out.append(f'Mixed logistic failed: {type(e).__name__}: {e}')
    try:
        g = GEE.from_formula(form, 'item', df, family=families.Binomial(), cov_struct=cov_struct.Exchangeable()).fit()
        lo, hi = g.conf_int().loc['fn_rank']
        out.append(f'GEE logistic (exchangeable within item): fn_rank log-odds {g.params["fn_rank"]:+.3f} [{lo:+.3f}, {hi:+.3f}], p = {g.pvalues["fn_rank"]:.3g}.')
    except Exception as e:
        out.append(f'GEE failed: {type(e).__name__}: {e}')
    return '\n'.join(out)


CLASSES_SHORT = (('Parse valid', lambda r: r['parse_valid']), ('AST accuracy', lambda r: r['ast_valid']),
                 ('Wrong function', lambda r: r['error_class'] == 'wrong_function'),
                 ('Argument error', lambda r: r['error_class'] == 'argument_error'),
                 ('Wrong count', lambda r: r['error_class'] == 'wrong_count'))


def lenient_table(strict, lenient):
    """Strict vs lenient AST accuracy per schema x order, paired by item (secondary score, PREREG addendum)."""
    sa, la = item_means(strict, lambda r: r['ast_valid']), item_means(lenient, lambda r: r['ast_valid'])
    ch = item_means(lenient, lambda r: r['lenient_changed'])
    lines = ['| Schema | Order | Strict AST | Lenient AST | Lenient − strict | Outputs changed by the rules |', '|---|---|---:|---:|---:|---:|']
    out = {}
    for schema in ('original', 'reversed'):
        for g in GROUPS + ('AR',):
            k = (schema, g)
            if k not in sa or k not in la:
                continue
            keys = sorted(sa[k].keys() & la[k].keys())
            d = stats.paired_bootstrap([la[k][i] for i in keys], [sa[k][i] for i in keys], keys)
            out[f'{schema} {g}'] = dict(strict=ci(sa[k]), lenient=ci(la[k]), diff=d)
            lines.append(f'| {schema} | {g} | {stats.fmt(ci(sa[k]))} | {stats.fmt(ci(la[k]))} | {stats.fmt(d)} | {stats.fmt(ci(ch[k]))} |')
    return '\n'.join(lines), out


def reference_table(rows):
    """AR reference: one order ('AR'); metrics per schema and the reversed - original difference."""
    lines = ['| Schema | ' + ' | '.join(n for n, _ in CLASSES_SHORT) + ' | Hit length limit |', '|---|' + '---:|' * (len(CLASSES_SHORT) + 1)]
    for schema in ('original', 'reversed'):
        sub = [r for r in rows if r['schema'] == schema]
        if sub:
            cells = [stats.fmt(ci(item_means(sub, f)[(schema, 'AR')])) for _, f in CLASSES_SHORT]
            lim = stats.fmt(ci(item_means(sub, lambda r: r['hit_length_limit'])[(schema, 'AR')]))
            lines.append(f'| {schema} | ' + ' | '.join(cells) + f' | {lim} |')
    acc = item_means(rows, lambda r: r['ast_valid'])
    o, rv = acc.get(('original', 'AR'), {}), acc.get(('reversed', 'AR'), {})
    keys = sorted(o.keys() & rv.keys())
    if keys:
        d = stats.paired_bootstrap([rv[k] for k in keys], [o[k] for k in keys], keys)
        lines.append(f'\nReversed − original schema, AST accuracy: {stats.fmt(d)} ({len(keys)} items).')
    return '\n'.join(lines)


def run(traces, sanity, ar=None, ar_sanity=None):
    sections, summary = {}, {}
    for m in MODELS:
        loaded = {t: load(t, m) for t in traces}
        missing = [t for t, rs in loaded.items() if not rs]
        if missing:
            sections[f'{m}: blocks not run'] = ', '.join(missing)
        rows = [r for rs in loaded.values() for r in rs]
        if not rows:
            continue
        schemas = sorted({r['schema'] for r in rows})
        summary[m] = dict(rows=len(rows), schemas=schemas)
        sections[f'{m}: metrics by schema and order'] = f'Rows: {len(rows)}; schemas: {schemas}.\n\n' + metric_table(rows)
        sections[f'{m}: order and schema contrasts'] = contrasts(rows)
        sections[f'{m}: by category'] = category_table(rows)
        sections[f'{m}: EOS commit rank by order'] = eos_table(rows)
        sections[f'{m}: function-name commit rank vs wrong-function errors'] = fn_rank_models(rows)
        len_rows = [r for t in traces if loaded[t] for r in load(t, m, lenient=True)]
        if len_rows:
            tab, out = lenient_table(rows, len_rows)
            summary[m]['lenient'] = out
            sections[f'{m}: secondary lenient-parse score (strict vs lenient)'] = tab
            sections[f'{m}: lenient-parse order and schema contrasts'] = contrasts(len_rows)
            sections[f'{m}: lenient-parse error classes'] = metric_table(len_rows)
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
    if ar:
        rows = load(ar, 'qwen')
        if rows:
            sections['Autoregressive reference (Qwen2.5-7B-Instruct, greedy): strict'] = (
                f'Rows: {len(rows)}; hosts/GPUs {sorted({(r["meta"]["hostname"], r["meta"]["gpu_name"]) for r in rows})}. '
                'Descriptive reference only: a different model and tokenizer, no order manipulation.\n\n' + reference_table(rows))
            lrows = load(ar, 'qwen', lenient=True)
            if lrows:
                tab, out = lenient_table(rows, lrows)
                summary['qwen'] = dict(rows=len(rows), lenient=out)
                sections['Autoregressive reference: strict vs lenient'] = tab
        else:
            sections['Autoregressive reference (Qwen2.5-7B-Instruct, greedy): strict'] = 'Not run.'
    if ar_sanity:
        rows = load(ar_sanity, 'qwen')
        if rows:
            a = ci(item_means(rows, lambda r: r['ast_valid'])[('original', 'AR')])
            sections['Autoregressive reference: sanity set'] = f'- qwen, greedy, 100 live_simple items, JSON format: AST accuracy {stats.fmt(a)}.'
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
    ap.add_argument('--ar', default=None, help='AR reference trace (qwen), e.g. test-ar')
    ap.add_argument('--ar-sanity', default=None)
    a = ap.parse_args()
    run(a.traces.split(','), a.sanity, a.ar, a.ar_sanity)


if __name__ == '__main__':
    main()
