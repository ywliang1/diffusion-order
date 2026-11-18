"""Statistics: source-clustered bootstrap, exact McNemar, mixed-effects regression.

Bootstrap: average the metric within each cluster (source), resample clusters with
replacement (10,000 by default), report the mean of cluster means and the 2.5/97.5
percentiles.
"""
import numpy as np
from scipy.stats import binomtest

B_DEFAULT = 10000
SEED_DEFAULT = 7331


def _boot(vals, n_boot=B_DEFAULT, seed=SEED_DEFAULT):
    vals = np.asarray(vals, dtype=float)
    n = len(vals)
    if n == 0:
        return dict(mean=float('nan'), lo=float('nan'), hi=float('nan'), n_clusters=0)
    rng = np.random.default_rng(seed)
    means = np.empty(n_boot)
    chunk = max(1, 2_000_000 // n)
    for s in range(0, n_boot, chunk):
        k = min(chunk, n_boot - s)
        means[s:s + k] = vals[rng.integers(n, size=(k, n))].mean(axis=1)
    return dict(mean=float(vals.mean()), lo=float(np.quantile(means, .025)), hi=float(np.quantile(means, .975)), n_clusters=n)


def cluster_means(values, clusters):
    groups = {}
    for v, c in zip(values, clusters):
        groups.setdefault(c, []).append(float(v))
    keys = sorted(groups, key=str)
    return keys, [float(np.mean(groups[k])) for k in keys]


def cluster_bootstrap(values, clusters, n_boot=B_DEFAULT, seed=SEED_DEFAULT):
    _, m = cluster_means(values, clusters)
    return _boot(m, n_boot, seed)


def paired_bootstrap(left, right, clusters, n_boot=B_DEFAULT, seed=SEED_DEFAULT):
    """left/right: aligned per-item metric arrays (same items, two conditions)."""
    d = np.asarray(left, dtype=float) - np.asarray(right, dtype=float)
    return cluster_bootstrap(d, clusters, n_boot, seed)


def mcnemar(a, b):
    """Exact two-sided McNemar on paired booleans a, b."""
    a = np.asarray(a, dtype=bool)
    b = np.asarray(b, dtype=bool)
    only_a = int((a & ~b).sum())
    only_b = int((~a & b).sum())
    n = only_a + only_b
    p = binomtest(min(only_a, only_b), n, .5).pvalue if n else float('nan')
    return dict(both=int((a & b).sum()), neither=int((~a & ~b).sum()), only_a=only_a, only_b=only_b, p=float(p))


def fmt(ci, pct=True):
    k = 100 if pct else 1
    d = 1 if pct else 3
    return f'{k*ci["mean"]:.{d}f} [{k*ci["lo"]:.{d}f}, {k*ci["hi"]:.{d}f}]'


def mixedlm(df, formula, group, reml=True):
    """Random-intercept mixed model. Returns coefficient table with Wald 95% CIs."""
    import statsmodels.formula.api as smf
    model = smf.mixedlm(formula, df, groups=df[group])
    # lbfgs raises a spurious singular-matrix error with scipy 1.17, so it is not used.
    fit, method, errors = None, None, {}
    for method in ('bfgs', 'powell', 'nm'):
        try:
            fit = model.fit(reml=reml, method=method)
        except Exception as e:  # record and try the next optimizer
            errors[method] = repr(e)
            continue
        if fit.converged:
            break
    if fit is None:
        raise RuntimeError(f'MixedLM failed with every optimizer: {errors}')
    ci = fit.conf_int()
    rows = {}
    for name in fit.fe_params.index:
        rows[name] = dict(coef=float(fit.fe_params[name]), se=float(fit.bse_fe[name]),
                          lo=float(ci.loc[name, 0]), hi=float(ci.loc[name, 1]), p=float(fit.pvalues[name]))
    return dict(coefs=rows, group_var=float(fit.cov_re.iloc[0, 0]), resid_var=float(fit.scale),
                converged=bool(fit.converged), optimizer=method, optimizer_errors=errors,
                n_obs=int(fit.nobs), n_groups=len(fit.model.group_labels))
