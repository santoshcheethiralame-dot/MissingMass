# E13: When can we stop auditing? A coverage stopping rule

| Field | Value |
|---|---|
| Status | registered; pilot done (R003); confirmatory R001 needs E02, E06, E09, E10 |
| Owner | Santosh |
| Tier | core |
| Stage | 2 confirmatory (uses data from E02, E06, E09, E10) |
| Depends on | E02, E06, E09, E10 |
| Study hypotheses | PH6 |
| Testbed | resampled campaigns from completed runs; no new runs |
| Compute | CPU |
| Pre-registration | not frozen |

## 1. Question

The practical question for a lab: when is it safe to stop adding audit or
red-team runs? A rule that stops when estimated coverage reaches a target is
only useful if it reaches the target in most campaigns, not just on average.
Technology-assisted document review uses Chao's estimator in exactly this
way: mean recall met its target, but only about 70% of individual reviews
did.

The closest AI-testing work is Li, Hays, Ramdas and Raghavan (2026,
arXiv 2611.15835). Their rule stops when an anytime-valid upper bound on the
chance of an unseen failure falls below a threshold. It needs no model of
detectability, but it treats one draw at a time. E13 tests their bound as a
comparator, R-CS (D-019), on run-level campaigns.

## 2. Pre-registration

<!-- prereg:start -->
### Aims
Evaluate coverage-based stopping rules for reliability and runs saved.

### Testbed
Campaigns are built by drawing run orders at random (1,000 permutations)
from the evaluation and reference runs of E02, E06, E09 (each configuration)
and E10 (arms A1 and A2). The truth C(k) after k runs uses the reference
π_i.

### Rules
- **R-point:** stop at the first k ≥ 3 where Ĉ(k) ≥ c*.
- **R-lower:** stop at the first k ≥ 3 where the lower 95% bootstrap bound
  of Ĉ(k) ≥ c*.
- **R-CS** (comparator, D-019): stop at the first k ≥ 3 where U(k) < 1 − c*.
  U(k) is the anytime-valid 95% upper confidence sequence of Li et al.
  (arXiv 2611.15835, Algorithm 1, as implemented in their Appendix C.1). It
  treats each run as one draw. The observation for run k is Z_k, the share
  of run k's detections not found by runs 1 to k − 1 (0 if run k finds
  nothing). U(k) bounds the expected Z of the next run.
- **R-fixed:** always run K_max (the maximum available).
- Targets c* ∈ {0.8, 0.9}.

### Performance measures
- Success rate: share of campaigns with true C ≥ c* at stopping.
- Runs saved vs R-fixed.
- Undershoot when the rule fails.

### Hypotheses and decision rules

| ID | Hypothesis | Measure | Supported if | Not supported if |
|---|---|---|---|---|
| H13a (→ PH6) | R-lower is reliable | success rate at c* = 0.9, pooled over testbeds with non-adaptive runs | ≥ 0.80 | < 0.70 |
| H13b (→ PH6) | R-lower saves effort | median runs saved | ≥ 30% | < 10% |
| H13c | R-point is not reliable enough | success rate at c* = 0.9 | < R-lower's | ≥ R-lower's |
| H13d | Adaptive campaigns break the rule | success rate, E10 A2 vs A1 | lower for A2 | not lower |

R-CS carries no hypothesis. It is reported next to R-lower: success rate,
runs saved and undershoot, per testbed and on the H13a set. The prediction
below follows from the bound's arithmetic alone, not from data. Even if no
run after the first finds anything new (Z = 0), U(k) first drops below 0.2
at k = 27 and below 0.1 at k = 51. So on every testbed with K_max < 27,
R-CS cannot stop early, and it behaves like R-fixed.

### Planned runs

| Run | Configuration | Replicates | Expected cost |
|---|---|---|---|
| R001 | All rules × testbeds | 1,000 permutations each | CPU hours |

### Sample size
1,000 permutations per testbed. These permutations are not independent of
each other, so intervals use a bootstrap over the underlying items or cells.

### Analysis plan
Confirmatory: H13a to H13d. Descriptive: R-CS next to R-lower (above).
Exploratory: an adaptive-aware rule using the A3 correction; and R-CS with
single detections as the draws (each run's detections in random order).
That gives many more draws, but it breaks the bound's i.i.d. assumption
within a run.

### Exclusions and missing data
Testbeds where K_max < 6 (e.g. E02) are reported separately and excluded from
the pooled H13a figure.

## 2a. Implementation notes (2026-10-23, before the freeze)

- The pilot (R003) ran on simulated campaigns. The confirmatory runner is
  `analysis/e13/run.py` (refuses a dirty tree; smoke tests use permutation
  keys from 9000), tested in `tests/test_e13_run.py`.
- A campaign is a random order of a cell's *estimation* runs (K_max = their
  number). π_i is the catch rate over the cell's *reference* runs.
- E02 cells have no reference runs, so π comes from all runs; they are
  flagged, and with K_max = 5 they are excluded from pooled H13a anyway
  (§2).
- E09 configurations enter as cells of one testbed. E10 arms enter as
  testbeds `E10-A1` and `E10-A2` (A2 marked adaptive and excluded from
  H13a).
- The H13a CI is a bootstrap over cells (§2 allows items or cells).

## 2a. Implementation notes, R-CS (2026-11-23, before the freeze)

- **Why it was added.** R-CS was added on 2026-11-23 after scouting round 1
  (D-019; `research/notes/scout-2026-11-23.md`). It came from the
  literature, not from E13 data. No E13 confirmatory data exist yet. The
  pilot R003 (simulated campaigns) had already been seen, but R-CS was not
  in it.
- **Code.** `crsafety.stopping`: `new_share` (Z_k), `unseen_ucs` (U) and
  `stop_cs`. The setting follows the paper's Appendix C.1:
  - restart weights w_s = 1 / (2.11 (s+1) log(s+1)²);
  - a reserve of 0.999 − Σ w for restarts not yet started;
  - 100 betting fractions λ on a midpoint grid in (0, 1), equal weights;
  - α = 0.05;
  - the bound is found by bisection, and the upper end is kept so that
    rounding is conservative.
- **Checked against the authors' code by reading it, not by running it.**
  `github.com/rachelli2019/unseen-failures-code`, commit `293527e`,
  `src/av_core.py`: the weight indexing, the 0.999 reserve and the e-process
  1 + λ(u − z) match.
- **Our extension: Z can be any value in [0, 1].** The paper's Z is binary.
  The proof still works because each factor 1 + λ(u − Z) stays positive for
  λ < 1. Its conditional mean is at most 1 whenever the next run's expected
  Z is at least u.
- **E13 breaks the i.i.d. assumption.** Its campaigns permute a fixed,
  finite set of runs, so each run is drawn without replacement. The paper's
  assumption therefore holds only approximately.
- **What the bound targets.** U bounds E[Z_{k+1}], a mean of ratios. The
  truth 1 − C(k) is a ratio of means (missed π-mass over total π-mass). The
  two agree only approximately. For both reasons, R-CS is scored against the
  true C like every other rule.
- **Tests.** `tests/test_stopping.py` checks:
  - the 27-run and 51-run thresholds;
  - coverage at a constant rate of 0.05;
  - that R-CS cannot fire at K = 16.

<!-- prereg:end -->

## 3. Contingencies

| If this happens | Then | Deviation? |
|---|---|---|
| A source experiment is missing | Evaluate on what exists and say so | Yes |
| R-lower never stops (bound too wide) | Report that. It is a usable negative: the budget is too small for the target | No |
| Li et al. revise their bound (a new arXiv version or code commit) before E13 freezes | Update R-CS to match, and note the version in §2a | No (before the freeze) |

## 4. Runs

<!-- runs:start -->
| Run | Title | Owner | Status | Started | Finished | Commit | Summary |
|---|---|---|---|---|---|---|---|
| E13-R001 | All rules x testbeds | Santosh | planned |  |  | 5d46498 |  |
| E13-R002 | Pilot (declared): rules on simulated campaigns | Santosh | failed | 2026-10-22 | 2026-10-22 | 5d46498+dirty | Bug: crashed before any campaign finished (stop_lower rejected a SeedSequence seed). Fixed with a test; re-run as E13-R003 |
| E13-R003 | Pilot (declared): rules on simulated campaigns (retry of E13-R002 after bug fix) | Santosh | succeeded | 2026-10-22 | 2026-10-22 | 5870a84+dirty | Pilot, 200 simulated campaigns x 6 worlds: R-lower (D-010 bound) success 0.93-0.985 where the target is reachable, median runs saved 19-69%; R-point 0.50-0.79; both fail with one shared family (0%); Zipf 0.5 never reaches 0.8 within K=16 (rules correctly do not stop) |
<!-- runs:end -->

## 5. Results

**R-lower's bound (D-010).** The "lower 95% bootstrap bound of Ĉ(k)" is the
one-sided lower bound of `crsafety.coverage_interval` (realized-coverage
bootstrap, B = 1,000), because E01 showed that the iNEXT interval
under-covers the realized coverage. Code: `crsafety.stopping`.

**Pilot (declared; simulated campaigns, not the E13 testbeds; not evidence
for H13a–H13d).** E13-R003 (E13-R002 crashed on a seeding bug before any
campaign finished, and was fixed and re-run). 200 fresh simulated campaigns
per world, K_max = 16 (12 for N = 20), B = 500.

| world | target | R-point success | R-lower success | R-lower median runs saved |
|---|---|---|---|---|
| homogeneous | 0.9 | 0.79 | 0.985 | 25% |
| logit-normal σ = 1 | 0.9 | 0.60 | 0.945 | 19% |
| logit-normal σ = 2 | 0.9 | 0.56 | 0.930 | 31% |
| N = 20, K = 12, p̄ = 0.4 | 0.9 | 0.50 | 0.965 | 33% |
| Zipf α = 0.5 | 0.8 / 0.9 | 0 | 0 (never stops; target unreachable by K = 16) | 0% |
| one shared family | 0.9 | 0 | 0 | 25% |

Full table: `results/E13/E13-R003/summary.md`. The pilot suggests R-lower
can meet H13a where runs are independent, and that shared-family
dependence breaks every rule, as H13d anticipates for adaptivity.

### Confirmatory

### Exploratory

## 6. Deviations

_None._
