# Generation order in diffusion tool calling: results summary

Branch `phase2`. Models: LLaDA-8B-Instruct (primary) and Dream-v0-Instruct-7B (replication), both at pinned revisions. Decoding commits one token per forward pass: greedy over the full vocabulary except the mask token, bf16, no KV cache, the whole canvas as one block, batch size 1. Intervals are 95% source-clustered bootstraps (10,000 resamples, seed 7331) unless noted. Each stage was preregistered (`experiments/<stage>/PREREG.md`) and committed before its test data was run. Every deviation is in that stage's `DECISIONS.md`.

## Verdicts at a glance

| Question | LLaDA | Dream | Verdict |
|---|---|---|---|
| **H1** (RQ1): under CF, output position shifts a field's commit rank after controlling for role and field | Small or absent at easy settings: +0.013 [−0.018, +0.043] at 8 rows; +0.017 to +0.052 with 2–3-token values. Large at 128 rows: +0.290 [+0.235, +0.345] | −0.052 [−0.090, −0.015] at 8 rows; +0.113 [+0.077, +0.147] at 16 rows (Exp 4); −0.010 to +0.071 with 2–3-token values | **Inconclusive.** Position effects are mostly smaller than the ±0.10 margin and change sign between settings. The one large effect comes with a field-identity effect of similar size. **Role** dominates everywhere: the dependent field is committed 0.37–0.63 later. |
| **H2** (RQ2): PF beats DF on the dependent field for two-hop items, with a smaller gap on one-hop controls | +54.5 [49.7, 59.2] two-hop vs −1.0 [−2.8, 0.5] one-hop (Exp 4); +42 to +43 with 2–3-token values | +14.9 [11.8, 18.1] vs +8.6 [6.0, 11.2]; interaction +6.2 [2.4, 10.2] (Exp 4); +3 / +14 with 2–3-token values | **Supported** in 5 of 6 model × value-length cells. Dream at k=2 is partly supported: the interaction CI touches 0, near ceiling. |
| BFCL realism check | see below | see below | see below |

Figures: `results/figures/rank_role_position.png`, `pf_df_gap.png`, `bfcl_errors.png`, `bfcl_commit_heatmap.png` (PDFs alongside).

## Finding carried from Phase 1.5: LLaDA's Phase 1 order effect may reflect format confusion

In Phase 1's space-separated table format, LLaDA's Shared-path B accuracy was 27–44 points higher under A-first than under B-first, and Direct B failed because the model copied the target row's H. In the explicit V2 and V3 formats (Phase 1.5 dev), LLaDA scores 100% on every condition and order up to 16 rows, with no A-first vs B-first gap. At least part of LLaDA's Phase 1 order effect may therefore come from misreading the table, not from the a→b dependency. Dream still shows a large gap when the task is hard (V3 at 16 rows: Shared-path B 93% A-first vs 62% B-first). Exp 4 and Stage 3 re-test the order effect in a format LLaDA reads correctly, and the PF/DF effect survives there (H2 above). Source: `experiments/phase1_5/DECISIONS.md`.

## Stage by stage

### Stage 0: equivalence (`results/equivalence/report.md`)
- The new `dlm` stack reproduces every Phase 1 row exactly on the A6000: 10,260/10,260 per model, with identical commits and probabilities.
- Batching changed decisions (149/150 for LLaDA and 139/150 for Dream unchanged), so all stages run at batch size 1.
- Replaying on an A100 flips 2.4% (LLaDA) and 4.8% (Dream) of row decisions, almost all at margins below 0.02. Cell accuracy moves by at most 1.3 points. Each stage therefore stays on one GPU type.

### Phase 1.5 and 1.5b: gate for a frozen task format (`results/phase1_5*/dev_report.md`)
- No variant (V1–V4, V3-nochat, V2 at 16–128 rows, V2 with decoys) met the gate for either model on dev.
- In LLaDA, Shared-path stays above 80% up to 128 rows.
- In Dream, one-hop and two-hop accuracy fall together as tables grow.
- Following the rule, no configuration was frozen and **no Phase 1.5 test split was run** (seeds 15002 and 15012 are unused).

### RQ1 study: role × layout commit rank at 8 rows (`results/rq1/report.md`, A6000, 200 sources)
- **LLaDA:** role +0.568 [0.505, 0.630]; position +0.013 [−0.018, +0.043]. H1 is contradicted under the preregistered ±0.10 equivalence rule.
- **Dream:** role +0.378 [0.318, 0.440]; position −0.052 [−0.090, −0.015]. H1 is supported, but the effect is small and the *right* field is committed earlier.
- **Prerequisite committed first:** LLaDA 78.4% on two-hop vs 51.1% on one-hop; Dream 68.9% vs 49.9%.
- **Margins:** 91% of LLaDA CF traces have a step with margin below 0.02; Dream 10%.

### Exp 4: role × layout × hop with all orders (`results/exp4/report.md`, A6000)
- **Sizes:** calibrated on dev to LLaDA 128 rows (100 sources) and Dream 16 rows (200 sources). Dream used the fallback branch: no size put its one-hop accuracy at 90% or more, so its two-hop items sit near ceiling.
- **H2:** as in the table above. LLaDA two-hop dependent accuracy is PF 89.5, CF 76.8, R2L 65.0, random 62.3, L2R 59.5 and DF 35.0. One-hop accuracy is 98–99 under every order.
- **H1:** position +0.290 (LLaDA) and +0.113 (Dream); field (b − a) +0.240 and +0.253; role +0.630 and +0.562. In LLaDA, most of the position and field effect comes from one cell, two-hop / query b / layout ab. There CF commits the prerequisite first in only 43% of traces and both fields are right in 42%.
- CF commits the prerequisite first in 81.5% (LLaDA) and 78.1% (Dream) of two-hop traces, compared with 58.2% and 64.9% for the one-hop direction field.

### Stage 3: 2- and 3-token values (`results/stage3/report.md`, A100 for the whole stage, CF/PF/DF only)

| Model, k | Rows | Position | Role | PF − DF two-hop | PF − DF one-hop | Hop × order |
|---|---:|---:|---:|---:|---:|---:|
| LLaDA, 2 | 64 | +0.052 [+0.023, +0.080] | +0.550 | +42.8 [38.5, 46.8] | +0.2 | +42.5 [38.2, 46.8] |
| LLaDA, 3 | 64 | +0.017 [+0.001, +0.034] | +0.541 | +42.0 [37.0, 47.0] | 0.0 | +42.0 [37.0, 47.0] |
| Dream, 2 | 16 | +0.071 [+0.046, +0.097] | +0.367 | +3.2 [1.2, 5.8] | +0.2 | +3.0 [0.0, 6.2] |
| Dream, 3 | 16 | −0.010 [−0.029, +0.007] | +0.373 | +14.5 [10.0, 19.2] | +1.5 | +13.0 [7.5, 18.8] |

- **Within a field, CF does not go left to right.** The share of fields committed strictly left to right is close to chance: about 50% at k=2 (chance 50%) and 14–28% at k=3 (chance 17%).
- **Fields are mostly committed as blocks.** 85–98% of traces commit each field as one uninterrupted block at k=2, and 68–93% at k=3.
- **The preregistered role × position interaction is not identifiable.** In this two-field design the two field ranks in a trace always sum to a constant, so the contrast is exactly 0 for any k. The preregistration was wrong on this point; see `experiments/stage3/DECISIONS.md`.

### Stage 4: BFCL realism check (`results/bfcl/report.md`)

_Pending: filled in when the BFCL blocks finish._

## Limitations

- **Synthetic tasks.** RQ1 and RQ2 use synthetic two-field lookup tables, in which field a is always prefilled inside a JSON scaffold. The gap from these to real tool calls is what the BFCL check probes, and it does not test dependency order directly.
- **Two models, different table sizes.** Each model was tested at a size calibrated to it (LLaDA 128, Dream 16; Stage 3 used LLaDA 64), so between-model comparisons are descriptive. Dream's Exp 4 two-hop items sit near ceiling, which compresses its H2 gap.
- **No frozen Phase 1.5 configuration.** The gate failed for both models. Exp 4 calibrated its own size on dev, and no Phase 1.5 test split exists.
- **GPU types.** RQ1, Exp 4 and BFCL ran on RTX A6000; Phase 1.5 and Stage 3 ran on A100-PCIE-40GB. Each stage uses one GPU type. Across GPU types, about 2–5% of row-level decisions flip, almost all where the margin is below 0.02. In Stage 3 that covers most LLaDA CF traces (94–100%), so compare Stage 3 with the other stages at the level of effects only.
- **Near-tied CF choices.** Many CF decisions in LLaDA are near-ties. CF commit orders are therefore deterministic for a fixed GPU and stack, but fragile across hardware.
- **Interaction not identifiable.** H1's role × position interaction cannot be estimated in a two-field design (see Stage 3).
- **Orders dropped for compute.** Stage 3 ran only CF, PF and DF.
- **No autoregressive reference.** The optional Qwen2.5-7B run was not done.

## Reproducibility

Environment: `.venv` (generation and analysis), `/data/rbg/users/linrui/venvs/bfcl-eval-2026.3.23` (BFCL data and scoring), `scripts/env.sh` (AFS-free environment for detached runs). Every trace row records host, GPU, torch and transformers versions, git commit, model revision and seed.

```sh
.venv/bin/python -m pytest tests/                                   # 47 tests
# Stage 0
.venv/bin/python -m experiments.equivalence.compare --stage equivalence --trace a6000 --exps 1,2,3
# RQ1 study / Exp 4 / Stage 3 (launch shards one GPU each; resume by run_id; merge refuses mixed GPU types)
.venv/bin/python -m dlm.runner launch --exp experiments.rq1.exp    --config experiments/rq1/config.yaml          --stage rq1    --trace main     --models llada,dream --gpus 0,1 --expect-gpu 'RTX A6000'
.venv/bin/python -m dlm.runner launch --exp experiments.exp4.exp   --config experiments/exp4/config_main.yaml    --stage exp4   --trace main     --models llada --gpus 0,1 --expect-gpu 'RTX A6000'
.venv/bin/python -m dlm.runner launch --exp experiments.exp4.exp   --config experiments/stage3/config_k2.yaml    --stage stage3 --trace main-k2  --models llada --gpus 0 --expect-gpu A100
.venv/bin/python -m experiments.rq1.analyze
.venv/bin/python -m experiments.exp4.analyze --stage exp4 --trace main
.venv/bin/python -m experiments.stage3.analyze
# BFCL
PYTHONNOUSERSITE=1 /data/rbg/users/linrui/venvs/bfcl-eval-2026.3.23/bin/python experiments/bfcl/prep.py
.venv/bin/python -m dlm.runner launch --exp experiments.bfcl.exp --config experiments/bfcl/config_orig.yaml --stage bfcl --trace test-orig --models llada --gpus 0,1,2 --expect-gpu 'RTX A6000'
PYTHONNOUSERSITE=1 /data/rbg/users/linrui/venvs/bfcl-eval-2026.3.23/bin/python experiments/bfcl/score.py --stage bfcl --trace test-orig
.venv/bin/python -m experiments.bfcl.analyze --traces test-orig,test-rev --sanity sanity
# Figures
MPLCONFIGDIR=/data/scratch/linrui/llada_home/.mpl .venv/bin/python -m experiments.figures
```
