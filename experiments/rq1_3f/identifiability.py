"""Identifiability check for the three-field RQ1 design. Simulation only; no model outputs.

Commit orders are drawn from a Plackett-Luce (PL) model whose log-worth depends on (role, position),
with a planted role x position interaction. The script checks:
  1. Fisher-information rank of the PL cell model: 2 fields (current design) vs 3 fields (proposed).
  2. Recovery of the planted interaction by the PL fit and by the model-free pairwise contrast
     (difference-in-differences in P(field committed before the independent field)).

    python -m experiments.rq1_3f.identifiability
"""
import itertools

import numpy as np
from scipy.optimize import minimize

ROLES = ('P', 'D', 'I')          # prerequisite, dependent, independent reference
BASE = {'P': 1.0, 'D': -1.0, 'I': 0.0}


def cells(roles, npos):
    return [(r, p) for r in roles for p in range(npos)]


def simulate(rng, roles, npos, inter, n_src):
    cs = cells(roles, npos)
    idx = {c: i for i, c in enumerate(cs)}
    theta = np.array([BASE[r] - .3 * p for r, p in cs])
    theta[idx[('D', npos - 1)]] += inter       # moving D to the last slot raises its worth by `inter`
    seqs, src = [], []
    for s in range(n_src):
        for _direction in range(2):
            for lay in itertools.permutations(range(npos)):
                left, order = [idx[(r, p)] for r, p in zip(roles, lay)], []
                while left:
                    w = np.exp(theta[left])
                    order.append(left.pop(rng.choice(len(left), p=w / w.sum())))
                seqs.append(order)
                src.append(s)
    return np.array(seqs), np.array(src), cs, idx


def pl_fit(S, ncell, ridge=0.0):
    def f(t):
        t = t - t[0]
        g, ll = np.zeros_like(t), 0.0
        for k in range(S.shape[1] - 1):
            sub = S[:, k:]
            w = np.exp(t[sub])
            Z = w.sum(1)
            ll += (t[S[:, k]] - np.log(Z)).sum()
            np.add.at(g, S[:, k], 1)
            np.add.at(g, sub.ravel(), -(w / Z[:, None]).ravel())
        return -ll + ridge * (t @ t), -g + 2 * ridge * t
    res = minimize(f, np.zeros(ncell), jac=True, method='L-BFGS-B', options=dict(maxiter=5000))
    return res.x - res.x[0]


def fisher_rank(S, theta):
    F = np.zeros((len(theta), len(theta)))
    for k in range(S.shape[1] - 1):
        for row in S[:, k:]:
            w = np.exp(theta[row])
            p = w / w.sum()
            e = np.zeros(len(theta))
            np.add.at(e, row, p)
            Fi = -np.outer(e, e)
            np.add.at(Fi, (row, row), p)
            F += Fi
    return np.linalg.matrix_rank(F, 1e-8)


def interaction(t, idx, npos):
    a, b = 0, npos - 1
    return (t[idx[('D', b)]] - t[idx[('D', a)]]) - (t[idx[('P', b)]] - t[idx[('P', a)]])


def did(S, cs, npos):
    """[P(D before I | D last) - P(D before I | D first)] - [same for P]."""
    out = {}
    for role in ('P', 'D'):
        for pos in (0, npos - 1):
            hits = []
            for order in S:
                where = {cs[c]: k for k, c in enumerate(order)}
                mine = [k for (r, p), k in where.items() if r == role and p == pos]
                ref = [k for (r, p), k in where.items() if r == 'I']
                if mine:
                    hits.append(mine[0] < ref[0])
            out[(role, pos)] = np.mean(hits)
    return (out[('D', npos - 1)] - out[('D', 0)]) - (out[('P', npos - 1)] - out[('P', 0)])


def main():
    rng = np.random.default_rng(4610)
    for roles, npos in ((('P', 'D'), 2), (ROLES, 3)):
        S, _, cs, idx = simulate(rng, roles, npos, 1.0, 50)
        theta = np.array([BASE[r] - .3 * p for r, p in cs])
        theta[idx[('D', npos - 1)]] += 1.0
        print(f'{len(roles)} fields: PL Fisher rank {fisher_rank(S, theta)}/{len(cs)} '
              f'(full = {len(cs) - 1}; interaction identifiable: {fisher_rank(S, theta) == len(cs) - 1})')
    for inter in (0.0, 0.5, 1.0):
        pl, dd = [], []
        for _ in range(40):
            S, _, cs, idx = simulate(rng, ROLES, 3, inter, 200)
            pl.append(interaction(pl_fit(S, len(cs), ridge=1e-3), idx, 3))
            dd.append(did(S, cs, 3))
        print(f'3 fields, 200 sources, planted PL interaction {inter:+.1f}: PL estimate {np.mean(pl):+.3f} '
              f'(sd over 40 sims {np.std(pl):.3f}); model-free DiD {np.mean(dd):+.3f} (sd {np.std(dd):.3f})')


if __name__ == '__main__':
    main()
