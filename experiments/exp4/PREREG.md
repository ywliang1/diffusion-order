# Exp 4 preregistration: role × layout × hop with CF, PF, DF and baseline orders (RQ1 and RQ2)

Written and committed before any Exp 4 model output exists.

## Questions (from the proposal)

- **RQ2 / H2:** prerequisite-first (PF) gives higher dependent-field accuracy than dependent-first (DF) on two-hop tasks, and the gap is smaller on matched one-hop controls.
- **RQ1 / H1 at the calibrated size:** under CF, output position affects a field's normalized commit rank after controlling for role and field identity. The RQ1 study already tested this at size 8; here it is re-estimated where the task is harder.

## Items

The same generator as the RQ1 study (`tasks/lookup.py`, `rl_*`), in the V2 row format. Per source there are 2 query directions × 2 output layouts × 2 hops, all with the same target pair. The input text never depends on layout, and all four inputs of a source have equal token length. Pools, Phase 1 exclusion, scoring and the task audit are as in the RQ1 study.

**Orders:** CF, PF, DF, L2R, R2L, random-s0, random-s1, random-s2. PF and DF use the CF rule inside each field. The three random seeds are averaged within each item before any comparison.

## Why Exp 4 calibrates its own size

The Phase 1.5b gate (Direct at least 90%, Shared-path at 40–80%) was not met by LLaDA at any size up to 128 rows: its a→b lookup stays at 88% or higher. Exp 4 therefore calibrates size directly on its own items with the rule below. The rule always returns a size, and whether that size falls inside the 40–80% band is reported, not used as a gate.

## Dev calibration

- 50 sources (seed 40011) at sizes 16, 32, 64 and 128, CF only, all 8 items per source: 1,600 rows per model.
- **Rule, per model** (`experiments/exp4/calibrate.py`):
  1. Among sizes whose one-hop CF full-answer accuracy (averaged over direction × layout) is at least 90%, take the size whose two-hop CF dependent-field accuracy is closest to 60%; ties go to the smaller size.
  2. If no size reaches 90% one-hop, take the size with the highest one-hop accuracy.

Each model can end up at a different size, so between-model comparisons are descriptive.

## Main run

- Fresh sources (seed 40001) at each model's calibrated size.
- **200 sources** if the calibrated size is at most 64, and **100 sources** (the proposal's N: 400 two-hop + 400 one-hop items) if it is 128, where a row takes about 4–5 s on an A6000.
- Total: sources × 8 items × 8 orders.
- **Hardware:** rosetta21 RTX A6000 (rosetta7 A6000 allowed).

**Power (H2).** With 100 sources there are 400 paired two-hop items per order pair. A PF − DF gap of 5 points with about 15% discordant pairs gives a paired-difference standard error near 1.9 points, so gaps of 5 points or more are detectable. With 200 sources the standard error is about 1.4 points.

## Primary analysis, per model (`experiments/exp4/analyze.py`)

**H2.** Dependent-field accuracy for PF minus DF, paired by item, with a 95% bootstrap clustered by source, separately for two-hop and one-hop. The hop × order interaction is (PF − DF | two-hop) − (PF − DF | one-hop), paired by (source, direction, layout). Exact McNemar on discordant PF/DF pairs per hop.
- **Supported:** the two-hop PF − DF lower bound is above 0 and the interaction lower bound is above 0.
- **Partly supported:** the two-hop gap's lower bound is above 0 but the interaction CI includes 0.
- **Contradicted:** the two-hop gap's upper bound is at most 0.
- **Inconclusive:** otherwise.

**H1.** MixedLM `rank ~ role_c + pos_c + field_c` with a source random intercept, on two-hop CF traces, plus source-bootstrap contrasts. The role × position interaction is omitted because it is not identifiable with two single-token fields (RQ1 study, `experiments/rq1/DECISIONS.md`). The verdict rule and the ±0.10 equivalence margin are the same as in the RQ1 study.

## Secondary and descriptive

- Accuracy (dependent, prerequisite, both) for every order and hop.
- Per-trace alignment (prerequisite first), two-hop vs one-hop.
- The CF margin distribution and the flip-sensitive fraction (margin below 0.02).
- Between-model differences.
