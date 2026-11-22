"""Tests for the E13 stopping rules (crsafety.stopping)."""

import numpy as np
import pytest

from crsafety import stopping as st


def world(seed, N=400, K=16, p=0.25):
    rng = np.random.default_rng(seed)
    pi = np.full(N, p)
    return (rng.random((N, K)) < pi[:, None]).astype(np.int8), pi


def test_true_coverage_monotone_in_k():
    X, pi = world(0)
    c = [st.true_coverage(X, pi, k) for k in range(1, 17)]
    assert c == sorted(c) and 0 < c[0] < c[-1] <= 1


def test_rules_order_and_bounds():
    X, pi = world(1)
    for t in (0.8, 0.9, 0.99):
        kp = st.stop_point(X, t)
        kl = st.stop_lower(X, t, B=200, seed=1)
        assert 3 <= kp <= kl <= X.shape[1]   # the lower bound never fires before the estimate


def test_unreachable_target_runs_everything():
    X, pi = world(2, p=0.02, K=8)
    assert st.stop_lower(X, 0.999, B=100, seed=0) == 8
    rows = st.campaign(X, pi, range(8), targets=(0.999,), B=100, seed=0)
    assert {r["rule"]: r["k_stop"] for r in rows}["R-fixed"] == 8


def test_campaign_records():
    X, pi = world(3)
    rows = st.campaign(X, pi, np.random.default_rng(0).permutation(16), B=100, seed=3)
    assert len(rows) == 8
    for r in rows:
        assert r["success"] == (r["C_at_stop"] >= r["target"])
        assert 0 <= r["saved"] < 1 and r["undershoot"] >= 0


def test_seed_sequence_seed_is_accepted_and_reproducible():
    X, pi = world(4)
    s = lambda: np.random.SeedSequence(7, spawn_key=(1, 2))
    assert st.stop_lower(X, 0.9, B=100, seed=s()) == st.stop_lower(X, 0.9, B=100, seed=s())


def test_new_share():
    X = np.array([[1, 1, 0, 0], [1, 0, 1, 0], [0, 1, 1, 0]])
    assert np.allclose(st.new_share(X), [1, 0.5, 0, 0])


def test_unseen_ucs_needs_many_runs_even_when_nothing_is_new():
    U = st.unseen_ucs(np.zeros(60))
    assert np.all(np.diff(U) <= 0) and U[0] == 1.0
    assert int(np.argmax(U < 0.2)) + 1 == 27 and int(np.argmax(U < 0.1)) + 1 == 51


def test_unseen_ucs_covers_a_constant_rate():
    rng = np.random.default_rng(0)
    miss = [(st.unseen_ucs((rng.random(80) < 0.05).astype(float), n_lambda=25) < 0.05).any() for _ in range(40)]
    assert np.mean(miss) <= 0.1


def test_stop_cs_cannot_fire_at_audit_scale():
    X, pi = world(5, p=0.9)
    assert st.stop_cs(X, 0.8) == X.shape[1] == 16
