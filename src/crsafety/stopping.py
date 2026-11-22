"""Coverage stopping rules for audit campaigns (E13; PH6).

A campaign adds runs one at a time in a given order. After k runs:
- R-point stops at the first k >= k_min with C_hat(k) >= target;
- R-lower stops at the first k >= k_min where the one-sided lower bound of
  the realized coverage (:func:`crsafety.coverage_interval`, D-010) is
  >= target;
- R-CS (D-019) stops at the first k >= k_min where the anytime-valid upper
  bound of Li et al. (arXiv 2611.15835) on the share of the next run's
  detections that are new is below 1 - target;
- R-fixed always runs all K_max runs.
A rule that never fires stops at K_max. The lower bound is computed only
when C_hat(k) >= target, since the bound never exceeds the estimate.
"""

import warnings

import numpy as np

from .bootstrap import coverage_interval
from .estimators import IncidenceData, coverage


def true_coverage(X, pi, k):
    """C(k) = sum of pi over items found in the first k columns / sum over pi > 0."""
    found = X[:, :k].any(axis=1)
    return float(pi[found].sum() / pi[pi > 0].sum())


def _data(X, k):
    Xk = X[:, :k]
    Xk = Xk[Xk.any(axis=1)]
    return IncidenceData.from_matrix(Xk) if Xk.shape[0] else None


def stop_point(X, target, k_min=3):
    for k in range(k_min, X.shape[1] + 1):
        d = _data(X, k)
        if d is not None and coverage(d) >= target:
            return k
    return X.shape[1]


def stop_lower(X, target, k_min=3, level=0.95, B=1000, seed=None):
    ss = seed if isinstance(seed, np.random.SeedSequence) else np.random.SeedSequence(seed)
    seeds = ss.spawn(X.shape[1] + 1)
    for k in range(k_min, X.shape[1] + 1):
        d = _data(X, k)
        if d is None or coverage(d) < target:
            continue
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            lo = coverage_interval(d, B=B, level=level, seed=seeds[k])["lower_one_sided"]
        if lo >= target:
            return k
    return X.shape[1]


def new_share(X):
    """Z_k = share of run k's detections that no earlier run detected (0 for an empty run)."""
    X = np.asarray(X, dtype=bool)
    seen_before = np.zeros(X.shape[0], dtype=bool)
    z = np.zeros(X.shape[1])
    for k in range(X.shape[1]):
        n = X[:, k].sum()
        z[k] = (X[:, k] & ~seen_before).sum() / n if n else 0.0
        seen_before |= X[:, k]
    return z


def unseen_ucs(z, alpha=0.05, n_lambda=100, C=2.11, iters=50):
    """Anytime-valid upper confidence sequence on the chance that the next draw
    is new (Li, Hays, Ramdas, Raghavan 2026, arXiv 2611.15835, Algorithm 1 as
    implemented in their Appendix C.1): restart weights w_s = 1 / (C (s+1)
    log(s+1)^2), a midpoint grid of n_lambda betting fractions, reserve
    0.999 - sum w. Returns U_t for t = 1..len(z). z must lie in [0, 1]."""
    z = np.asarray(z, dtype=float)
    lam = (np.arange(1, n_lambda + 1) - 0.5) / n_lambda
    out = np.empty(len(z))
    for t in range(1, len(z) + 1):
        s = np.arange(1, t + 1)
        w = 1.0 / (C * (s + 1) * np.log(s + 1) ** 2)
        tail = 0.999 - w.sum()

        def M(u):
            lf = np.log1p(lam[:, None] * (u - z[None, :t]))      # (n_lambda, t)
            suffix = np.cumsum(lf[:, ::-1], axis=1)[:, ::-1]     # sum_{i >= s} log f_i
            return float(np.mean(np.exp(suffix + np.log(w)[None, :]).sum(axis=1)) + tail)

        if M(1.0) < 1 / alpha:
            out[t - 1] = 1.0
            continue
        lo, hi = 0.0, 1.0
        for _ in range(iters):
            mid = 0.5 * (lo + hi)
            lo, hi = (mid, hi) if M(mid) < 1 / alpha else (lo, mid)
        out[t - 1] = hi
    return out


def stop_cs(X, target, k_min=3, alpha=0.05):
    """R-CS (D-019): stop at the first k >= k_min where the anytime upper bound
    on the share of the next run's detections that are new is < 1 - target.
    Runs are the draws; Z_k is :func:`new_share`."""
    U = unseen_ucs(new_share(X), alpha=alpha)
    for k in range(k_min, X.shape[1] + 1):
        if U[k - 1] < 1 - target:
            return k
    return X.shape[1]


RULES = ("R-point", "R-lower", "R-CS", "R-fixed")


def campaign(X, pi, order, targets=(0.8, 0.9), k_min=3, level=0.95, B=1000, seed=None):
    """Apply every rule to one run order. Returns a list of dicts, one per
    (rule, target): k_stop, true C at stop, success, runs saved vs R-fixed,
    undershoot (target - C when it fails, else 0)."""
    Xo = X[:, list(order)]
    K = Xo.shape[1]
    out = []
    for t in targets:
        for rule in RULES:
            if rule == "R-point":
                k = stop_point(Xo, t, k_min)
            elif rule == "R-lower":
                k = stop_lower(Xo, t, k_min, level, B, seed)
            elif rule == "R-CS":
                k = stop_cs(Xo, t, k_min)
            else:
                k = K
            C = true_coverage(Xo, pi, k)
            out.append(dict(rule=rule, target=t, k_stop=k, C_at_stop=C, success=C >= t,
                            saved=(K - k) / K, undershoot=max(t - C, 0.0)))
    return out
