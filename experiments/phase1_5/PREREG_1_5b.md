# Phase 1.5b preregistration: per-model table size for the V2 format

Written and committed before any Phase 1.5b model output exists. Phase 1.5 (`PREREG.md`) ended with no frozen variant: V2 (explicit `key=… | a=… | h=… | b=…` rows) solved Direct but put Shared-path above 80% at sizes 4 and 8. The team approved this follow-up on 2026-11-17: V2, larger tables, a separate size per model, and a decoy fallback.

## What stays the same as Phase 1.5

Models and revisions, decoding (`dlm`, batch size 1, CF tie seed `seed + source_id + 1000 × size`), the three conditions, the value pools (`results/phase1_5/pool-<model>.json`), Phase 1 exclusion, the task audit, scoring (whitespace-stripped exact match, raw kept), the error taxonomy, 95% source-clustered bootstrap intervals (10,000 resamples, seed 7331), exact McNemar, and the Exp 3 design.

## What changes

- **Format:** V2 only, plus the fallback V2d (V2 with n decoy mapping rows keyed by the other key column: `h=<H> | b=<F>` on Shared-path, `a=<A> | b=<F>` on Separate-path, and filler `d=<G> | e=<F>` on Direct). V2d makes the model match the key's label, not only its value. Every source draws 8 value columns (A, H, B, C, D, E, F, G), so V2 and V2d run on identical sources.
- **Sizes:** V2 at 16, 32, 64 and 128 rows; V2d at 16, 32 and 64 (V2d at 128 would exceed LLaDA's 4,096-token context; V2 at 128 is about 3,300 tokens).
- **Seeds:** dev 15011, test 15012.
- **Hardware:** rosetta21, RTX A6000, for both dev and test. If rosetta21 fills up mid-stage, rosetta7 (A6000) may be used; A100s are not used in this stage.

## Dev

100 sources per (variant, size) cell, 3 conditions × A-first, B-first, CF, both models: 6,300 rows per model. Dev audit: 0 failures over 595,200 value checks per model (`results/phase1_5b/task_audit-dev.json`).

### Gate (unchanged, team decision B), applied to one (variant, size) cell for one model

1. Direct B at least 90% under each of A-first, B-first and CF (point estimate).
2. Shared-path B, averaged over the three orders, in [40%, 80%] with its 95% lower bound above 1/n.
3. Separate-path B, averaged over the three orders, with its 95% lower bound above 1/n.

### Selection rule (per model, independently)

Freeze the first passing cell in the order V2-16, V2-32, V2-64, V2-128, V2d-16, V2d-32, V2d-64. A model with no passing cell gets no test run; we report its closest cell (most criteria met, ties to higher minimum Direct B). V2d is run alongside V2 for wall-clock reasons only; it can be chosen only if no V2 cell passes for that model.

**Cross-model comparisons are descriptive.** Because each model can end up at a different variant or size, no test compares the two models; their numbers are reported side by side only.

## Test

For each model with a frozen cell: 200 fresh sources (seed 15012) at that cell, with the Exp 2 design (3 conditions × 3 orders) and the Exp 3 design (Shared-path and Separate-path × Masked, Gold, Predicted, Wrong). That is 3,400 rows per model. The task audit runs first. The gate is re-evaluated on test and reported whether it passes or not; test results never change the frozen cell.

## Analysis

As in Phase 1.5: A, B and both-correct accuracy; the B error taxonomy (with V2d decoy hits counted as "target row other"); paired A-first vs B-first outcomes with exact McNemar; the A-first − B-first gap and its Shared − Separate interaction; step-0 confidence; CF first field; the fraction of CF rows with a CF margin below 0.02; Exp 3 branch gaps against Masked; and the Wrong branch's match to the wrong row's B. Implemented in `experiments/phase1_5/analyze_b.py`.

Smoke: 5 sources at size 64, V2 and V2d, Exp 2 and Exp 3, to `results/phase1_5b_smoke/` (excluded from analysis).
