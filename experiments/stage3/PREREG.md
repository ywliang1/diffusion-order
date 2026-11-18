# Stage 3 preregistration: multi-token values

Written and committed before any Stage 3 model output exists.

## Question

Do the single-token RQ1 and RQ2 results hold when each value spans 2 or 3 tokens? Under CF, are a field's tokens committed left to right, and in one block?

## Design

The Exp 4 items (`tasks/lookup.py`, `rl_*`), with every table value and both output fields exactly **k tokens**, k ∈ {2, 3}.

**Values.** Concatenations of k distinct words from the Phase 1.5 single-token pool, kept only if the value is exactly k tokens, with the same ids, bare, after a space, after `=` and inside quotes, and if it aligns in both output slots and both layouts. 3,000 values per model and k: `results/stage3/pool-k<k>-<model>.json`. Slot length therefore reveals neither the answer nor the field's role.

**Sizes.**
- LLaDA: 64 rows. Its Exp 4 size, 128, would exceed LLaDA's 4,096-token context with 3-token values; at 64 the longest canvas is 2,307 tokens.
- Dream: 16 rows (its Exp 4 size).

**Other settings:**
- **Sources:** 100 per model and k, seed 50001, 8 items each.
- **Orders:** CF, PF and DF only. L2R, R2L and random are dropped for compute; the contrasts below use CF, PF and DF only.
- **Rows:** 2,400 per model and k.
- **Hardware:** rosetta15, NVIDIA A100-PCIE-40GB, for the whole stage. The rosetta21 A6000s are fully booked by BFCL and Exp 4, and rosetta7 is saturated by other users.

**Task audit:** 0 token-count failures over 128,000 (LLaDA) and 32,000 (Dream) value checks for each k; equal prompt lengths; both layouts align (`results/stage3/task_audit-main-k*.json`).

## Analysis (`experiments/stage3/analyze.py`), per model and k

- **H1:** MixedLM `rank ~ role_c * pos_c + field_c` with a source intercept on two-hop CF traces, where a field's rank is the mean normalized rank of its k tokens among the 2k content tokens. With k ≥ 2 the role × position interaction is identifiable. Bootstrap contrasts and the verdict rule (±0.10 equivalence margin) are as in the RQ1 study.
- **H2:** PF − DF dependent-field accuracy (all k tokens right), paired by item, two-hop and one-hop, plus the hop × order interaction and McNemar. The verdict rule is as in Exp 4.
- **Within-field order under CF:**
  - the share of fields whose k tokens were committed strictly left to right, by role and hop;
  - the share of traces in which each field was committed as one uninterrupted block.
- **Descriptive:** accuracy by order, per-trace alignment (the prerequisite's first token before the dependent's), the CF margin distribution, and comparison with the single-token Exp 4 results.

Smoke: 2 sources, k = 3 (48 rows per model), to `results/stage3_smoke/`, excluded from analysis.
