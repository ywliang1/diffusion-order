"""Three-field RQ1 analysis (PREREG: experiments/rq1_3f/PREREG.md).

Primary, per model and size, two-hop CF traces:
  B(R, p)  share of traces in which role R (prerequisite or dependent) is committed before the independent
           field h, among traces with R in slot p.
  DiD      [B(dep,last) - B(dep,first)] - [B(pre,last) - B(pre,first)]          (H1b, role x slot)
  POS      0.5 * [B(dep,last) - B(dep,first) + B(pre,last) - B(pre,first)]      (H1, slot main effect)
  PL       Plackett-Luce on the three-field commit order: log-worth = role x slot cells + field b, ridge 1e-3.
Intervals: 10,000 source-clustered bootstrap resamples (seed 7331), percentile 95% CIs.

    python -m experiments.rq1_3f.analyze --traces main-n8,main-n128
"""
import argparse
import json

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.stats import chi2

from dlm import report, stats
from dlm.models import ROOT

BASE = ROOT / 'results/rq1_3f'
MODELS = ('llada', 'dream')
ROLES = ('prerequisite', 'dependent', 'independent')
SLOTS = ('first', 'middle', 'last')
CELLS = [(r, s) for r in ROLES for s in SLOTS]
CIDX = {c: i for i, c in enumerate(CELLS)}
MARGIN, FLIP, RIDGE = 0.10, 0.02, 1e-3
N_BOOT, SEED = stats.B_DEFAULT, stats.SEED_DEFAULT


def load(trace, model):
    p = BASE / 'traces' / f'{trace}-{model}.jsonl'
    if not p.exists():
        return None
    rows = report.read_required(p)
    for r in rows:
        r.pop('steps', None)
        r.pop('step0', None)
    return rows


# ---------- model-free contrasts ----------

def counts(rows):
    """Per source: hits[R, p] and n[R, p] for R in (pre, dep) committed before h, p in slots."""
    srcs = sorted({r['source_id'] for r in rows})
    sidx = {s: i for i, s in enumerate(srcs)}
    hits, n = np.zeros((len(srcs), 2, 3)), np.zeros((len(srcs), 2, 3))
    for r in rows:
        role_of = {f: role for f, role in r['roles'].items()}
        h = next(f for f, role in role_of.items() if role == 'independent')
        for ri, role in enumerate(('prerequisite', 'dependent')):
            f = next(g for g, x in role_of.items() if x == role)
            pi = SLOTS.index(r['slot'][f])
            n[sidx[r['source_id']], ri, pi] += 1
            hits[sidx[r['source_id']], ri, pi] += r['first_commit'][f] < r['first_commit'][h]
    return hits, n


def contrasts(B):
    """B: (..., 2, 3) shares. Returns DiD, POS and both role-specific slot effects."""
    pre = B[..., 0, 2] - B[..., 0, 0]
    dep = B[..., 1, 2] - B[..., 1, 0]
    return dict(did=dep - pre, pos=(dep + pre) / 2, pre_slot=pre, dep_slot=dep)


def boot_model_free(rows):
    hits, n = counts(rows)
    est = contrasts(hits.sum(0) / n.sum(0))
    rng = np.random.default_rng(SEED)
    S = len(hits)
    draws = {k: np.empty(N_BOOT) for k in est}
    cells = np.empty((N_BOOT, 2, 3))
    for b in range(N_BOOT):
        i = rng.integers(S, size=S)
        Bb = hits[i].sum(0) / n[i].sum(0)
        cells[b] = Bb
        for k, v in contrasts(Bb).items():
            draws[k][b] = v
    out = {k: dict(mean=float(est[k]), lo=float(np.quantile(draws[k], .025)), hi=float(np.quantile(draws[k], .975)),
                   n_clusters=S) for k in est}
    Bhat = hits.sum(0) / n.sum(0)
    out['cells'] = {f'{role}|{slot}': dict(mean=float(Bhat[ri, pi]), lo=float(np.quantile(cells[:, ri, pi], .025)),
                                           hi=float(np.quantile(cells[:, ri, pi], .975)), n=int(n.sum(0)[ri, pi]))
                    for ri, role in enumerate(('prerequisite', 'dependent')) for pi, slot in enumerate(SLOTS)}
    return out


# ---------- Plackett-Luce ----------

def pl_arrays(rows):
    """Per trace, the three fields in commit order: cell index and is-field-b indicator."""
    cell, isb, src = [], [], []
    for r in rows:
        order = sorted(r['first_commit'], key=r['first_commit'].get)
        cell.append([CIDX[(r['roles'][f], r['slot'][f])] for f in order])
        isb.append([f == 'B' for f in order])
        src.append(r['source_id'])
    return np.array(cell), np.array(isb, dtype=float), np.array(src)


def pl_fit(cell, isb, x0=None):
    """Parameters: 9 cell log-worths (cell 0 fixed at 0) + field-b effect."""
    def f(x):
        th = np.concatenate([[0.], x[:8]])
        u = th[cell] + x[8] * isb                       # (n, 3) utilities in commit order
        g = np.zeros(10)
        ll = 0.0
        for k in range(2):
            w = np.exp(u[:, k:] - u[:, k:].max(1, keepdims=True))
            p = w / w.sum(1, keepdims=True)              # (n, 3-k)
            ll += (np.log(p[:, 0])).sum()
            # gradient wrt utilities: 1{chosen} - p
            gu = -p
            gu[:, 0] += 1
            np.add.at(g, cell[:, k:].ravel(), gu.ravel())
            g[9] += (gu * isb[:, k:]).sum()
        grad = np.concatenate([g[1:9], [g[9]]])
        return -ll + RIDGE * (x @ x), -grad + 2 * RIDGE * x
    res = minimize(f, np.zeros(9) if x0 is None else x0, jac=True, method='L-BFGS-B', options=dict(maxiter=2000))
    return res.x, res.success


def pl_quantities(x):
    th = np.concatenate([[0.], x[:8]]).reshape(3, 3)    # rows: roles, cols: slots
    pre = th[0, 2] - th[0, 0]
    dep = th[1, 2] - th[1, 0]
    dc = th - th.mean(0, keepdims=True) - th.mean(1, keepdims=True) + th.mean()
    return dict(interaction=dep - pre, slot=(dep + pre) / 2, field_b=x[8], dc=dc[:2, :2].ravel())


def boot_pl(rows):
    cell, isb, src = pl_arrays(rows)
    x, ok = pl_fit(cell, isb)
    est = pl_quantities(x)
    srcs = np.unique(src)
    by = [np.where(src == s)[0] for s in srcs]
    rng = np.random.default_rng(SEED)
    keys = ('interaction', 'slot', 'field_b')
    draws = {k: np.empty(N_BOOT) for k in keys}
    dcs = np.empty((N_BOOT, 4))
    fails = 0
    for b in range(N_BOOT):
        i = np.concatenate([by[j] for j in rng.integers(len(srcs), size=len(srcs))])
        xb, okb = pl_fit(cell[i], isb[i], x0=x)
        fails += not okb
        q = pl_quantities(xb)
        for k in keys:
            draws[k][b] = q[k]
        dcs[b] = q['dc']
    out = {k: dict(mean=float(est[k]), lo=float(np.quantile(draws[k], .025)), hi=float(np.quantile(draws[k], .975)))
           for k in keys}
    cov = np.cov(dcs.T)
    w = float(est['dc'] @ np.linalg.pinv(cov) @ est['dc'])
    out['joint'] = dict(wald=w, df=4, p=float(chi2.sf(w, 4)))
    out['converged'] = bool(ok)
    out['bootstrap_nonconverged'] = int(fails)
    return out


# ---------- verdicts ----------

def excludes0(c):
    return c['lo'] > 0 or c['hi'] < 0


def same_sign(a, b):
    return np.sign(a['mean']) == np.sign(b['mean'])


def verdict(mf, pl_c):
    if excludes0(mf) and excludes0(pl_c) and same_sign(mf, pl_c):
        return 'supported'
    if -MARGIN < mf['lo'] and mf['hi'] < MARGIN:
        return 'contradicted'
    return 'inconclusive'


# ---------- secondary ----------

def mixed_rank(rows):
    recs = [dict(rank=r['ranks'][f], role=r['roles'][f], slot=r['slot'][f], is_b=float(f == 'B'), source=r['source_id'])
            for r in rows for f in r['roles']]
    df = pd.DataFrame(recs)
    fit = stats.mixedlm(df, "rank ~ C(role, Treatment('independent')) * C(slot, Treatment('first')) + is_b", 'source')
    lines = ['| Term | Coef [95% CI] |', '|---|---:|']
    for k, v in fit['coefs'].items():
        lines.append(f"| {k} | {v['coef']:+.3f} [{v['lo']:+.3f}, {v['hi']:+.3f}] |")
    return ('Mean normalized rank (0 = committed first). Caveat (PREREG): ranks in a trace still sum to a constant, '
            'so a nonzero interaction here reflects dependence on where the other fields sit; the DiD and PL rows '
            'are the interpretable ones.\n\n' + '\n'.join(lines))


def alignment(rows):
    def pre_first(r):
        pre = next(f for f, x in r['roles'].items() if x == 'prerequisite')
        dep = next(f for f, x in r['roles'].items() if x == 'dependent')
        return float(r['first_commit'][pre] < r['first_commit'][dep])
    two = [r for r in rows if r['hop'] == 2]
    one = [r for r in rows if r['hop'] == 1]
    a2 = stats.cluster_bootstrap([pre_first(r) for r in two], [r['source_id'] for r in two])
    a1 = stats.cluster_bootstrap([pre_first(r) for r in one], [r['source_id'] for r in one])
    m2 = dict(zip(*stats.cluster_means([pre_first(r) for r in two], [r['source_id'] for r in two])))
    m1 = dict(zip(*stats.cluster_means([pre_first(r) for r in one], [r['source_id'] for r in one])))
    keys = sorted(set(m2) & set(m1))
    d = stats.cluster_bootstrap([m2[k] - m1[k] for k in keys], keys)
    return (f'Prerequisite committed before dependent: two-hop {stats.fmt(a2)}, one-hop (nominal roles) {stats.fmt(a1)}, '
            f'difference {stats.fmt(d)} points.')


def accuracy(rows):
    lines = ['| Hop | a correct | b correct | h correct | All three correct |', '|---:|---:|---:|---:|---:|']
    for hop in (2, 1):
        sub = [r for r in rows if r['hop'] == hop]
        cl = [r['source_id'] for r in sub]
        cs = [stats.fmt(stats.cluster_bootstrap([float(r['fields'][f]['correct']) for r in sub], cl)) for f in ('A', 'B', 'H')]
        allc = stats.fmt(stats.cluster_bootstrap([float(r['all_correct']) for r in sub], cl))
        lines.append(f'| {hop} | {" | ".join(cs)} | {allc} |')
    return '\n'.join(lines)


def cell_table(mf):
    lines = ['| Role | Slot | n traces | Committed before h |', '|---|---|---:|---:|']
    for k, v in mf['cells'].items():
        role, slot = k.split('|')
        lines.append(f'| {role} | {slot} | {v["n"]} | {stats.fmt(v)} |')
    return '\n'.join(lines)


def f3(c):
    return f'{c["mean"]:+.3f} [{c["lo"]:+.3f}, {c["hi"]:+.3f}]'


def run(traces):
    sections, summary = {}, {}
    for trace in traces:
        for m in MODELS:
            rows = load(trace, m)
            if rows is None:
                continue
            rows = [r for r in rows if r['order'] == 'CF']
            key = f'{m} {trace}'
            meta = sorted({(r['meta']['hostname'], r['meta']['gpu_name'], r['meta']['git_commit']) for r in rows})
            res = {}
            for hop in (2, 1):
                sub = [r for r in rows if r['hop'] == hop]
                res[hop] = dict(mf=boot_model_free(sub), pl=boot_pl(sub))
            mf, pl = res[2]['mf'], res[2]['pl']
            v1b = verdict(mf['did'], pl['interaction'])
            v1 = verdict(mf['pos'], pl['slot'])
            two = [r for r in rows if r['hop'] == 2]
            flip = float(np.mean([r['min_cf_margin'] is not None and r['min_cf_margin'] < FLIP for r in two]))
            sens = {}
            for name, keep in (('excluding flip-sensitive traces', lambda r: not (r['min_cf_margin'] is not None and r['min_cf_margin'] < FLIP)),
                               ('fully correct traces only', lambda r: r['all_correct'])):
                sub = [r for r in two if keep(r)]
                sens[name] = (len(sub), boot_model_free(sub) if len(sub) >= 50 else None)
            summary[key] = dict(size=rows[0]['table_size'], rows=len(rows), h1b=v1b, h1=v1,
                                did=mf['did'], pos=mf['pos'], pl_interaction=pl['interaction'], pl_slot=pl['slot'],
                                pl_joint=pl['joint'], one_hop_did=res[1]['mf']['did'], flip_fraction=flip)
            sections[f'{key}: summary'] = (
                f'Table size {rows[0]["table_size"]}; CF traces {len(rows)}; hosts/GPUs/commits {meta}.\n\n'
                f'- **H1b (role × slot): {v1b}.** DiD {f3(mf["did"])}; PL interaction {f3(pl["interaction"])} log-worth; '
                f'joint 4-df role × slot Wald {pl["joint"]["wald"]:.1f}, p = {pl["joint"]["p"]:.3g}.\n'
                f'- **H1 (slot main effect): {v1}.** POS {f3(mf["pos"])}; PL slot (last − first) {f3(pl["slot"])}.\n'
                f'- Two-hop traces with a CF margin below {FLIP}: {100 * flip:.1f}%. '
                f'PL converged: {pl["converged"]}; non-converged bootstrap refits: {pl["bootstrap_nonconverged"]}.')
            lines = ['| Hop | Contrast | Model-free (share before h) | Plackett–Luce (log-worth) |', '|---:|---|---:|---:|']
            for hop in (2, 1):
                a, b = res[hop]['mf'], res[hop]['pl']
                lines += [f'| {hop} | role × slot (DiD / interaction) | {f3(a["did"])} | {f3(b["interaction"])} |',
                          f'| {hop} | slot main effect (last − first) | {f3(a["pos"])} | {f3(b["slot"])} |',
                          f'| {hop} | prerequisite: last − first | {f3(a["pre_slot"])} | |',
                          f'| {hop} | dependent: last − first | {f3(a["dep_slot"])} | |',
                          f'| {hop} | field b − field a | | {f3(b["field_b"])} |']
            sections[f'{key}: contrasts'] = '\n'.join(lines)
            sections[f'{key}: share committed before h, two-hop'] = cell_table(mf)
            sections[f'{key}: share committed before h, one-hop'] = cell_table(res[1]['mf'])
            sl = ['| Subset | Two-hop traces | DiD | POS |', '|---|---:|---:|---:|']
            for name, (n, s) in sens.items():
                sl.append(f'| {name} | {n} | {f3(s["did"]) if s else "n < 50"} | {f3(s["pos"]) if s else "n < 50"} |')
            sections[f'{key}: sensitivity'] = '\n'.join(sl)
            sections[f'{key}: mean-rank mixed model, two-hop'] = mixed_rank(two)
            sections[f'{key}: alignment'] = alignment(rows)
            sections[f'{key}: accuracy'] = accuracy(rows)
    sections['Interpretation limits'] = '\n'.join([
        '- One commit per forward pass, CF only; three single-token fields; V2 row format (not validated by the Phase 1.5 gate).',
        '- Between-model and between-size comparisons are descriptive.',
        '- Hardware is one GPU type for the whole stage (see Deviations); rows are not comparable across GPU types, effects are.'])
    dec = ROOT / 'experiments/rq1_3f/DECISIONS.md'
    sections['Deviations'] = dec.read_text() if dec.exists() else ''
    (BASE / 'report.md').write_text(report.build('Three-field RQ1 study: role × slot on CF commit order', sections,
                                                 required=['Interpretation limits', 'Deviations']))
    (BASE / 'summary.json').write_text(json.dumps(summary, indent=2, default=float) + '\n')
    print('wrote', BASE / 'report.md', {k: (v['h1b'], v['h1']) for k, v in summary.items()})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--traces', default='main-n8,main-n128')
    a = ap.parse_args()
    run(a.traces.split(','))


if __name__ == '__main__':
    main()
