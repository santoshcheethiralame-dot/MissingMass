"""E02 zoo.py: marginal p_i recovered from a compensated SynthSAEBench world."""

import importlib.util
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("e02_zoo", ROOT / "analysis/e02/zoo.py")
zoo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(zoo)

# 4 features, Zipf exponent 1 in [0.01, 0.4]: base p = [0.4, 0.14, 0.05333, 0.01].
CFG = dict(num_features=4,
           firing_probability=dict(generator_name="zipfian", exponent=1.0, max_prob=0.4, min_prob=0.01),
           hierarchy=dict(compensate_probabilities=True))
# Root 0 with mutually exclusive children 1 and 2; feature 3 is outside the hierarchy.
HIER = dict(roots=[dict(feature_index=0, mutually_exclusive_children=True, children=[
    dict(feature_index=1, mutually_exclusive_children=False, children=[]),
    dict(feature_index=2, mutually_exclusive_children=False, children=[])])])
BASE = np.array([0.4, 0.14, 0.16 / 3, 0.01])
# What SAELens stores: base x (1 / p_parent) x (1 + sibling p / p_parent) for ME children.
STORED = BASE * np.array([1, 2.5 * (1 + (0.16 / 3) / 0.4), 2.5 * (1 + 0.14 / 0.4), 1])


def test_compensated_world_gives_base_p():
    assert np.allclose(zoo.marginal_p(STORED, CFG, HIER), BASE, rtol=1e-6)


def test_uncompensated_world_keeps_stored_p():
    cfg = dict(CFG, hierarchy=dict(compensate_probabilities=False))
    assert np.array_equal(zoo.marginal_p(STORED, cfg, HIER), STORED)
    assert np.array_equal(zoo.marginal_p(STORED, None, None), STORED)


def test_mismatch_with_config_is_an_error():
    with pytest.raises(SystemExit, match="do not match"):
        zoo.marginal_p(STORED * 1.1, CFG, HIER)
