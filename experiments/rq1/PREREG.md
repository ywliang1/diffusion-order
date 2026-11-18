# RQ1 study preregistration: role × layout commit ranks under confidence-first decoding

Written and committed before any RQ1 model output exists. Approved by the team on 2026-11-17 to run in parallel with Phase 1.5b, on the V2 format at a size where Direct B is at least 90%. Unlike Phase 1.5 it does not need the 40–80% accuracy band, because it measures commit order, not accuracy.

## Question and hypothesis (from the proposal)

- **RQ1:** under CF decoding, how much do a field's dependency role (prerequisite vs dependent) and its output position (left vs right) each affect its normalized commit rank?
- **H1:** output position affects mean normalized field commit rank after controlling for dependency role and field identity.

## Setup

- **Models and decoding:** as in Phase 1.5 (pinned revisions, bf16, no KV cache, one commit per pass, greedy over the full vocabulary except the mask token, batch size 1). Only the **CF** order is run. CF ties are broken by `random.Random(seed + source_id + 1000 × size)`.
- **Hardware:** rosetta21, RTX A6000 (rosetta7 A6000 if rosetta21 is full; never A100 in this study).
- **Pools:** `results/phase1_5/pool-<model>.json` (Phase 1 sources, prompt words and chat-template words excluded; every value one token bare, after a space and after `=`).
- **Sources:** 200, table size 8, seed 20001, Phase 1 exclusion. V2 dev Direct B at size 8 was 100% (LLaDA) and 95–96% (Dream) under every order.

## Design: 2 × 2 × 2 per source, same target pair throughout

| Factor | Levels | What changes |
|---|---|---|
| Query direction (role) | a-prerequisite, b-prerequisite | The anchor gives `a=…` or `b=…` for each key |
| Output layout (position) | `{"a":…,"b":…}`, `{"b":…,"a":…}` | Only the output scaffold; the input text is identical |
| Hop | two-hop, matched one-hop | Two-hop: anchor `key | <p>=… | h=… | c=…` + mapping `a=… | b=…` (same mapping text in both directions). One-hop: anchor `key | <p>=… | h=… | <other>=…` + filler mapping `d=… | e=…` |

That is 8 items per source and 1,600 CF traces per model. All four inputs of a source have the same token length, and both layouts align (task audit: 0 failures over 32,000 value checks per model, `results/rq1/task_audit-main.json`).

## Measures

- **Normalized commit rank** of a field: the mean over its content tokens of (k − 1)/(n − 1), where k is the commit order among the n content tokens. EOS and padding are excluded (none exist on this canvas). With two single-token fields, a field's rank is 0 if committed first and 1 if second.
- **Field and full-answer accuracy:** whitespace-stripped exact match.
- **CF margin:** the top-1 minus top-2 slot confidence at each CF step. A trace is flip-sensitive if its smallest margin is below 0.02.

## Primary analysis (two-hop traces, per model)

1. **Mixed model:** `rank ~ role_c * pos_c + field_c` with a random intercept per source (statsmodels MixedLM, REML), one row per (trace, field). Codes are ±0.5 (role: dependent +0.5; position: right +0.5; field: b +0.5), so each main effect is a difference in mean rank. Wald 95% CIs.
2. **Bootstrap contrasts:** the same four effects as source-level differences in mean rank, 10,000 source-clustered resamples (seed 7331).

**H1 decision rule:**
- **Supported:** the position effect's 95% CI excludes 0 in both the mixed model and the bootstrap.
- **Contradicted:** the bootstrap CI of the position effect lies entirely within **±0.10** rank units (the pre-specified equivalence margin).
- **Inconclusive:** anything else.

Each verdict is reported per model. A role effect, by itself, does not rule out a position effect; both are reported with their uncertainty.

**Power.** 200 sources give 800 two-hop traces per model. A binary rank difference has a standard error of at most about 0.035, so the 95% CI half-width is at most about 0.07. That resolves any position effect of at least 0.07, and reaches the ±0.10 equivalence region only if the true effect is below about 0.03.

## Secondary and descriptive

- **Per-cell rates** (direction × layout × hop): left field committed first, prerequisite committed first, a/b/both accuracy.
- **Per-trace alignment:** the rate at which the prerequisite's first token is committed before the dependent's, two-hop vs the matched one-hop item (for one-hop, the field the anchor would query first), with a paired bootstrap difference.
- **Sensitivity:** the position effect excluding flip-sensitive traces, and on fully correct traces only.
- **One-hop items:** the same model, reported descriptively.
- **Between models:** comparisons are descriptive.

Smoke: 5 sources (40 traces per model) to `results/rq1_smoke/`, excluded from analysis. Deviations go in `experiments/rq1/DECISIONS.md`.
