# Research and scouting round (every 10 days, mandatory)

Every 10 days, one of us spends a fixed block (about 3 hours) looking
outward. The round has two jobs:
- catch a scoop early;
- find ideas from other fields that make the study stronger.

It replaces the weekly scoop check (RISKS.md R01), which lapsed after
2026-10-23. The scoop lane below is a superset of that check.

**Status:** proposed by Santosh on 2026-11-23 (D-018). Kushal to accept at
the next sync. It changes a shared duty in `TEAM.md`.

## The rule

- A round is due every 10 days, on the dates in the calendar below. It
  alternates between Santosh and Kushal.
- A round is done when its note is committed:
  `research/notes/scout-YYYY-MM-DD.md` (template below), plus a LOG entry.
  Searching without a note does not count.
- **A missed round is made up within 3 days.** If it can't be, log why in
  `LOG.md`. The next round's owner then covers both windows.
- At the Monday sync (TEAM.md, item 5): say whether the last round is done
  and who owns the next.
- **Every lead ends in exactly one outcome:**

  | Outcome | Where it goes |
  |---|---|
  | **ignore** | nowhere |
  | **read** | `research/reading-list.md` |
  | **question** | a new Q-ID in `OPEN-QUESTIONS.md` |
  | **risk** | a trigger in `RISKS.md` |
  | **decide** | a proposal in `DECISIONS.md` |
  | **act** | an experiment, run or paper edit, with an owner |

  Nothing stays as "interesting, maybe later".
- **A scoop is handled the same day, not at the next round.** That means a
  paper or repo that estimates unseen features, failures or audit coverage
  from repeated runs. Message the other person, add a LOG entry, and apply
  the R01 response in `RISKS.md`.

## The six lanes

Cover every lane, even if one gets five minutes. Lanes 1–2 protect the
project; lanes 3–6 grow it.

| # | Lane | What to look for | Where |
|---|---|---|---|
| 1 | **Scooping** | Capture-recapture, unseen-species or coverage estimates applied to SAEs, LLM audits, red teams or evals. New work by the near-miss authors (Gerasimov, Ghosh, Paulo and Belrose, Kansal). | arXiv (cs.LG, cs.CL, cs.CR, stat.ME), OpenReview, Alignment Forum / LessWrong, GitHub, Semantic Scholar citation alerts on our key refs |
| 2 | **Near competitors** | Adjacent work a reviewer will ask about. SAE seed stability and feature matching; audit benchmarks (AuditBench and successors); red-team coverage and diversity metrics; eval saturation; "how many failures are left" claims in model cards and system cards. | Same, plus lab blogs and model and system cards |
| 3 | **New leads** | Datasets, testbeds, model organisms, SAE zoos, tools, workshops and calls for papers we could use or submit to. | HF Hub, GitHub trending, workshop pages, Kaggle |
| 4 | **Old ML/NLP methods** | Classical techniques that fit our problems: vocabulary-growth and unseen-word estimation; entity resolution and record linkage (identity errors, E03–E05); annotation-agreement and active-learning stopping rules (E13); smoothing (Good-Turing family). | ACL Anthology, older JMLR/ICML, textbooks |
| 5 | **Math and statistics outside ML** | Ecology (mark-resight, open populations for Q-N3), epidemiology and multiple-systems estimation, species accumulation, extreme-value and heavy-tail theory, record-linkage error models. | stat.ME, Biometrics, JASA, Annals of Applied Statistics |
| 6 | **Cybersecurity and space research** | Cybersec: fuzzing saturation and residual risk, bug-bounty discovery curves, vulnerability-rediscovery rates, seeded-defect testing. Space: survey completeness and detection efficiency, e.g. exoplanet injection–recovery tests (planted signals, as in E15), near-Earth-object survey debiasing, debris catalogue completeness. | USENIX/CCS/S&P/FSE/ICSE, astro-ph.IM / astro-ph.EP, AJ, Icarus |

**Starting leads not yet in `research/notes/`** (already covered: STADS,
Efron–Thisted, Fellegi–Sunter, multiple-systems estimation):
- exoplanet injection–recovery completeness, for E15's planted marks;
- asteroid and NEO survey debiasing, for detection probability as a
  function of covariates (E07);
- space-debris catalogue completeness.

Check these before citing; they are pointers, not findings.

## Note template (`research/notes/scout-YYYY-MM-DD.md`)

```markdown
# Scouting round YYYY-MM-DD (<owner>)

Window covered: YYYY-MM-DD to YYYY-MM-DD. Time spent: N h.
Queries run (per lane): ...

## Scoop status
None / FOUND: <link>. Same-day response: ...

## Leads
| # | Lane | Lead (link) | Why it might matter to us | Outcome | Owner |
|---|---|---|---|---|---|

## Changes made
Reading list / OPEN-QUESTIONS Q-.. / RISKS / DECISIONS D-.. / experiment ...
```

## Calendar (to the NeurIPS deadline)

| Round | Due | Owner | Focus | Done (note) |
|---|---|---|---|---|
| 1 | 2026-11-23 | Santosh | | |
| 2 | 2026-12-03 | Kushal | | |
| 3 | 2026-12-13 | Santosh | before the preprint (M4): do lanes 1–2 in full | |
| 4 | 2026-12-23 | Kushal | | |
| 5 | 2027-01-02 | Santosh | | |
| 6 | 2027-01-12 | Kushal | | |
| 7 | 2027-01-22 | Santosh | before the ICLR workshop (M6): do lanes 1–2 in full | |
| 8 | 2027-02-01 | Kushal | | |
| 9 | 2027-02-11 | Santosh | | |
| 10 | 2027-02-21 | Kushal | | |
| 11 | 2027-03-03 | Santosh | | |
| 12 | 2027-03-13 | Kushal | | |
| 13 | 2027-03-23 | Santosh | | |
| 14 | 2027-04-02 | Kushal | | |
| 15 | 2027-04-12 | Santosh | | |
| 16 | 2027-04-22 | Kushal | before the writing freeze (M9): do lanes 1–2 in full | |
| 17 | 2027-05-02 | Santosh | | |
| 18 | 2027-05-12 | Kushal | before NeurIPS (M10): related work is final after this | |

When a round is done, put its note's filename in the last column.
