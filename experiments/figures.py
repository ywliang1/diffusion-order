"""Figures for results/SUMMARY.md (PNG + PDF in results/figures/). Panels whose data are missing are skipped.

    python -m experiments.figures
"""
import json
from collections import defaultdict

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

from dlm import stats
from dlm.models import ROOT

OUT = ROOT / 'results/figures'
# Reference categorical palette (validated: scripts/validate_palette.js, light mode, all checks pass).
BLUE, ORANGE, AQUA, YELLOW, MAGENTA = '#2a78d6', '#eb6834', '#1baf7a', '#eda100', '#e87ba4'
INK, INK2, GRID, SURFACE = '#0b0b0b', '#52514e', '#e4e3df', '#fcfcfb'
MODELS = (('llada', 'LLaDA-8B-Instruct'), ('dream', 'Dream-v0-Instruct-7B'))

plt.rcParams.update({'font.size': 9, 'axes.edgecolor': INK2, 'axes.labelcolor': INK, 'xtick.color': INK2,
                     'ytick.color': INK2, 'axes.spines.top': False, 'axes.spines.right': False,
                     'figure.facecolor': SURFACE, 'axes.facecolor': SURFACE, 'savefig.facecolor': SURFACE,
                     'axes.titlesize': 9.5, 'axes.titleweight': 'bold', 'legend.frameon': False})


def jsonl(path):
    return [json.loads(x) for x in open(path) if x.strip()] if path.exists() else []


def save(fig, name):
    OUT.mkdir(parents=True, exist_ok=True)
    for ext in ('png', 'pdf'):
        fig.savefig(OUT / f'{name}.{ext}', dpi=200, bbox_inches='tight')
    plt.close(fig)
    print('wrote', OUT / f'{name}.png')


def grid(ax, axis='y'):
    ax.grid(axis=axis, color=GRID, linewidth=.8)
    ax.set_axisbelow(True)


def rank_by_role_position():
    """Mean normalized CF commit rank by role x output position, two-hop items, per model and study."""
    studies = [('RQ1 study', ROOT / 'results/rq1/traces/main-{m}.jsonl'),
               ('Exp 4', ROOT / 'results/exp4/traces/main-{m}.jsonl')]
    data = [(t, m, label, [r for r in jsonl(ROOT / p.relative_to(ROOT).as_posix().format(m=m)) if r['order'] == 'CF' and r['hop'] == 2])
            for t, p in studies for m, label in MODELS]
    data = [d for d in data if d[3]]
    if not data:
        return
    titles = sorted({d[0] for d in data}, key=[s[0] for s in studies].index)
    fig, axes = plt.subplots(len(titles), 2, figsize=(7.2, 2.6 * len(titles)), squeeze=False, sharey=True)
    for t, m, label, rows in data:
        ax = axes[titles.index(t)][0 if m == 'llada' else 1]
        size = rows[0]['table_size']
        for role, color, marker, dx in (('prerequisite', BLUE, 'o', -.06), ('dependent', ORANGE, 's', .06)):
            ys, los, his = [], [], []
            for pos in ('left', 'right'):
                vals = [(r['ranks'][f], r['source_id']) for r in rows for f in ('A', 'B')
                        if r['roles'][f] == role and r['position'][f] == pos]
                c = stats.cluster_bootstrap([v for v, _ in vals], [s for _, s in vals])
                ys.append(c['mean']); los.append(c['mean'] - c['lo']); his.append(c['hi'] - c['mean'])
            xs = np.array([0, 1]) + dx
            ax.errorbar(xs, ys, yerr=[los, his], color=color, marker=marker, markersize=6, linewidth=2, capsize=0,
                        markeredgecolor=SURFACE, markeredgewidth=1.5)
            ax.annotate(role, (xs[-1], ys[-1]), xytext=(8, 0), textcoords='offset points', va='center', color=INK, fontsize=8.5)
        ax.set_xticks([0, 1], ['left field', 'right field'])
        ax.set_xlim(-.35, 1.65)
        ax.set_ylim(-.02, 1.02)
        ax.set_title(f'{label}\n{t}: {size}-row tables', loc='left')
        grid(ax)
    for row in axes:
        row[0].set_ylabel('normalized commit rank\n(0 = committed first)')
    fig.suptitle('Under CF the prerequisite field is committed first; position matters more in large tables', x=.01, ha='left',
                 fontsize=10.5, fontweight='bold', color=INK)
    fig.tight_layout()
    save(fig, 'rank_role_position')


def pf_df_gap():
    """PF - DF dependent-field accuracy by hop: Exp 4 (1-token values) and Stage 3 (2- and 3-token values)."""
    conds = [('Exp 4', 'results/exp4/traces/main-{m}.jsonl', 1), ('Stage 3', 'results/stage3/traces/main-k2-{m}.jsonl', 2),
             ('Stage 3', 'results/stage3/traces/main-k3-{m}.jsonl', 3)]
    panels = []
    for m, label in MODELS:
        got = [(t, k, jsonl(ROOT / p.format(m=m))) for t, p, k in conds]
        got = [g for g in got if g[2]]
        if got:
            panels.append((label, got))
    if not panels:
        return
    fig, axes = plt.subplots(1, len(panels), figsize=(3.7 * len(panels), 3.1), squeeze=False, sharey=True)
    for ax, (label, got) in zip(axes[0], panels):
        ticks = []
        for i, (t, k, rs) in enumerate(got):
            dep = defaultdict(dict)
            for r in rs:
                if r['order'] in ('PF', 'DF'):
                    dep[r['order']][(r['source_id'], r['direction'], r['layout'], r['hop'])] = float(r['dependent_correct'])
            for hop, color, marker, dx in ((2, BLUE, 'o', -.13), (1, ORANGE, 's', .13)):
                keys = sorted(x for x in dep['PF'] if x[3] == hop and x in dep['DF'])
                c = stats.paired_bootstrap([dep['PF'][x] for x in keys], [dep['DF'][x] for x in keys], [x[0] for x in keys])
                ax.errorbar([i + dx], [100 * c['mean']], yerr=[[100 * (c['mean'] - c['lo'])], [100 * (c['hi'] - c['mean'])]],
                            color=color, marker=marker, markersize=7, linewidth=2, capsize=0, markeredgecolor=SURFACE,
                            markeredgewidth=1.5, label=('two-hop' if hop == 2 else 'one-hop control') if i == 0 else None)
                ax.annotate(f'{100 * c["mean"]:+.0f}', (i + dx, 100 * c['hi']), xytext=(0, 4), textcoords='offset points',
                            ha='center', fontsize=7.5, color=INK)
            ticks.append((i, f'{t}\n{k}-token, {rs[0]["table_size"]} rows'))
        ax.axhline(0, color=INK2, linewidth=1)
        ax.set_xticks([t for t, _ in ticks], [l for _, l in ticks], fontsize=7.5)
        ax.set_xlim(-.5, len(got) - .5)
        ax.set_ylim(-8, 68)
        ax.set_title(label, loc='left')
        grid(ax)
    axes[0][0].set_ylabel('PF − DF dependent-field\naccuracy (points)')
    handles, labels = axes[0][0].get_legend_handles_labels()
    axes[0][-1].legend(handles, labels, loc='upper right', fontsize=8.5)
    fig.suptitle('Prerequisite-first beats dependent-first on two-hop items\n95% CI, clustered by source',
                 x=.01, ha='left', fontsize=10.5, fontweight='bold', color=INK)
    fig.tight_layout(rect=(0, 0, 1, .95))
    save(fig, 'pf_df_gap')


def bfcl_errors():
    classes = (('correct', 'AST correct', BLUE), ('argument_error', 'argument error', ORANGE), ('wrong_function', 'wrong function', AQUA),
               ('wrong_count', 'wrong call count', YELLOW), ('parse_error', 'parse error', MAGENTA))
    panels = []
    for m, label in MODELS:
        rows = []
        for t in ('test-orig', 'test-rev'):
            sc = ROOT / f'results/bfcl/scores/{t}-{m}.jsonl'
            rows += jsonl(sc)
        if rows:
            panels.append((label, rows))
    if not panels:
        return
    groups = ('L2R', 'R2L', 'random', 'CF')
    fig, axes = plt.subplots(1, len(panels), figsize=(3.9 * len(panels), 3.0), squeeze=False, sharey=True)
    for ax, (label, rows) in zip(axes[0], panels):
        bars = []
        for schema in ('original', 'reversed'):
            for g in groups:
                sub = [r for r in rows if r['schema'] == schema and (r['order'] == g or (g == 'random' and r['order'].startswith('random')))]
                if sub:
                    bars.append((f'{g}\n{"orig" if schema == "original" else "rev"}', {c: 100 * np.mean([r['error_class'] == c for r in sub]) for c, _, _ in classes}))
        x = np.arange(len(bars))
        bottom = np.zeros(len(bars))
        for c, name, color in classes:
            v = np.array([b[1][c] for b in bars])
            ax.bar(x, v, bottom=bottom, color=color, width=.72, edgecolor=SURFACE, linewidth=1.5, label=name)
            for xi, (vi, bi) in enumerate(zip(v, bottom)):
                if vi >= 12:
                    ax.text(xi, bi + vi / 2, f'{vi:.0f}', ha='center', va='center', fontsize=7.5, color=INK)
            bottom += v
        ax.set_xticks(x, [b[0] for b in bars], fontsize=7.5)
        ax.set_title(label, loc='left')
        ax.set_ylim(0, 100)
        grid(ax)
    axes[0][0].set_ylabel('share of outputs (%)')
    handles, labels = axes[0][0].get_legend_handles_labels()
    fig.legend(handles, labels, loc='upper center', ncol=5, bbox_to_anchor=(.5, 1.06), fontsize=8)
    fig.tight_layout()
    save(fig, 'bfcl_errors')


def bfcl_commit_heatmap():
    """Mean normalized commit step for each canvas position, by order (BFCL, original schema)."""
    panels = []
    for m, label in MODELS:
        p = ROOT / f'results/bfcl/traces/test-orig-{m}.jsonl'
        if not p.exists():
            continue
        acc = defaultdict(lambda: np.zeros(64))
        cnt = defaultdict(int)
        for x in open(p):
            r = json.loads(x)
            g = 'random' if r['order'].startswith('random') else r['order']
            L = r['length']
            start = min(s['pos'] for s in r['steps'])
            v = np.zeros(L)
            for s in r['steps']:
                v[s['pos'] - start] = s['step'] / (L - 1)
            acc[g] += v
            cnt[g] += 1
        panels.append((label, {g: acc[g] / cnt[g] for g in acc}))
    if not panels:
        return
    groups = ('L2R', 'R2L', 'random', 'CF')
    from matplotlib.colors import LinearSegmentedColormap
    cmap = LinearSegmentedColormap.from_list('blue_seq', ['#cde2fb', '#86b6ef', '#3987e5', '#256abf', '#104281', '#0d366b'])
    fig, axes = plt.subplots(len(panels), 1, figsize=(7.2, 1.5 * len(panels) + .6), squeeze=False)
    for ax, (label, d) in zip(axes[:, 0], panels):
        gs = [g for g in groups if g in d]
        im = ax.imshow(np.vstack([d[g] for g in gs]), aspect='auto', cmap=cmap, vmin=0, vmax=1)
        ax.set_yticks(range(len(gs)), gs)
        ax.set_title(label, loc='left')
        ax.set_xlabel('canvas position (0 = first response token)')
        for s in ax.spines.values():
            s.set_visible(False)
    cb = fig.colorbar(im, ax=axes[:, 0], fraction=.025, pad=.01)
    cb.set_label('mean commit step\n(0 = first, 1 = last)')
    fig.suptitle('BFCL commit order across the 64-token canvas (original schema)', x=.01, ha='left', fontsize=10.5, fontweight='bold')
    save(fig, 'bfcl_commit_heatmap')


def main():
    rank_by_role_position()
    pf_df_gap()
    bfcl_errors()
    bfcl_commit_heatmap()


if __name__ == '__main__':
    main()
