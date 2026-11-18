# Generation order in diffusion tool calling: results summary

Branch `phase2`. Models: LLaDA-8B-Instruct (primary) and Dream-v0-Instruct-7B (replication), both at pinned revisions. Decoding commits one token per forward pass: greedy over the full vocabulary except the mask token, bf16, no KV cache, the whole canvas as one block, batch size 1. Intervals are 95% source-clustered bootstraps (10,000 resamples, seed 7331) unless noted. Each stage was preregistered (`experiments/<stage>/PREREG.md`) and committed before its test data was run. Every deviation is in that stage's `DECISIONS.md`.

## Verdicts at a glance

| Question | LLaDA | Dream | Verdict |
|---|---|---|---|
| **H1** (RQ1): under CF, output position shifts a field's commit rank after controlling for role and field | Small or absent at easy settings: +0.013 [−0.018, +0.043] at 8 rows; +0.017 to +0.052 with 2–3-token values. Large at 128 rows: +0.290 [+0.235, +0.345] | −0.052 [−0.090, −0.015] at 8 rows; +0.113 [+0.077, +0.147] at 16 rows (Exp 4); −0.010 to +0.071 with 2–3-token values | **Inconclusive.** Position effects are mostly smaller than the ±0.10 margin and change sign between settings. The one large effect comes with a field-identity effect of similar size. **Role** dominates everywhere: the dependent field is committed 0.37–0.63 later. |
| **H1b** (three-field study): the slot effect differs between prerequisite and dependent (role × slot) | Inconclusive at 8 rows (DiD +0.063 [0.017, 0.109]; PL −0.015 [−0.18, 0.15]) and at 128 rows (DiD +0.175 [0.105, 0.245]; PL +0.30 [−0.14, 0.68]) | Supported at 8 rows: DiD −0.045 [−0.085, −0.006]; PL −0.174 [−0.33, −0.03] | **No evidence that dependency role changes the slot effect.** The one-hop control, where roles are only labels, shows an interaction as large or larger (LLaDA DiD +0.19; Dream PL +0.38). The interaction most likely reflects where each value sits in the input, not the dependency. |
| **H2** (RQ2): PF beats DF on the dependent field for two-hop items, with a smaller gap on one-hop controls | +54.5 [49.7, 59.2] two-hop vs −1.0 [−2.8, 0.5] one-hop (Exp 4); +42 to +43 with 2–3-token values | +14.9 [11.8, 18.1] vs +8.6 [6.0, 11.2]; interaction +6.2 [2.4, 10.2] (Exp 4); +3 / +14 with 2–3-token values | **Supported** in 5 of 6 model × value-length cells. Dream at k=2 is partly supported: the interaction CI touches 0, near ceiling. **Dream's Exp 4 H2 is a near-ceiling result:** its calibrated size (16 rows) had 96% two-hop dev accuracy, outside the preregistered 40–80% band, so its PF − DF gap is compressed and not comparable to LLaDA's. |
| BFCL realism check: does order matter on real single-turn calls? | AST accuracy: CF 50.5, L2R 41.2, random 18.7, R2L 7.2 (original schema) | L2R 77.5, CF 66.0, random 15.0, R2L 6.2 | **Order matters a lot.** R2L and random collapse in both models. CF beats L2R for LLaDA under strict scoring (+9.2 [3.5, 15.0]), but **not under the lenient parse** (+0.8 [−5.5, 7.0]), so that advantage is about output format. CF loses to L2R for Dream under both scorings (about −12). Reversing the schema changes accuracy by at most 3.5 points. An autoregressive reference, Qwen2.5-7B-Instruct, scores 95.8%. |

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
- **Format and sizes:** V2 row format (`key=… | a=… | h=… | c=…` anchor rows, `a=… | b=…` mapping rows), not frozen by any gate. Sizes calibrated on dev to LLaDA 128 rows (100 sources) and Dream 16 rows (200 sources); this is a preregistration deviation from the Mission (`experiments/exp4/DECISIONS.md`). Dream used the fallback branch: no size put its one-hop accuracy at 90% or more, and at the chosen 16 rows its two-hop dev accuracy was **96%, outside the 40–80% band**. Dream's H2 result is therefore near ceiling: in the main run, two-hop dependent accuracy is 96.5% under PF (95.6% under CF, 81.6% under DF), so the ceiling caps how far PF can exceed DF.
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
- **Determinism check:** a full rerun on the same GPU type (rosetta15 A100; `results/stage3_rerun/`) reproduced all 9,600 rows bit for bit (same commits and probabilities), so every Stage 3 verdict reproduces. The intended A6000 rerun was not possible: rosetta21 was down and rosetta7's A6000s were all busy.
- **The preregistered role × position interaction is not identifiable.** In this two-field design the two field ranks in a trace always sum to a constant, so the contrast is exactly 0 for any k. The preregistration was wrong on this point; see `experiments/stage3/DECISIONS.md`.

### Three-field RQ1 study: role × slot (`results/rq1_3f/report.md`, A100 for the whole stage, CF only)

- **Design** (preregistered in `experiments/rq1_3f/PREREG.md`, frozen before any output): a third output field `h` is read straight from the anchor row and nothing depends on it, so it serves as a reference. All 6 output orders of a, b and h are used.
- **Arms:** 8 rows (200 sources per model) and LLaDA at 128 rows (100 sources). The dev validity check passed for every arm (98–100%).
- **Why it was needed:** with two fields, the role × slot interaction cannot be estimated (Stage 3). With three, it can, as the simulation in `experiments/rq1_3f/identifiability.py` confirms.

| Arm | Role × slot: DiD in P(committed before h) | Role × slot: Plackett–Luce | Slot effect, last − first (PL log-worth) | Same interaction on one-hop controls (DiD; PL) |
|---|---:|---:|---:|---:|
| LLaDA, 8 rows | +0.063 [+0.017, +0.109] | −0.015 [−0.179, +0.149] | −0.130 [−0.196, −0.067] | +0.189; +0.71 |
| Dream, 8 rows | −0.045 [−0.085, −0.006] | −0.174 [−0.325, −0.029] | −0.031 [−0.090, +0.028] | +0.021; +0.38 |
| LLaDA, 128 rows | +0.175 [+0.105, +0.245] | +0.295 [−0.136, +0.681] | −1.008 [−1.277, −0.791] | +0.195; +1.09 |

- **H1b (role × slot):** inconclusive for LLaDA at both sizes; supported for Dream at 8 rows, under the preregistered rule.
- **The one-hop control is not null,** although the PREREG expected it to be. The "prerequisite" field also sits before `h` in the anchor row, so the role labels encode input position. A two-hop interaction therefore cannot be attributed to the dependency. LLaDA's two-hop interaction is no larger than its one-hop control, and Dream's has the opposite sign to its one-hop PL interaction.
- **Slot effect (H1):** the preregistered model-free slot measure (POS) is contaminated by the reference field's own slot effect. This is a PREREG error, logged in `experiments/rq1_3f/DECISIONS.md`. By the Plackett–Luce slot effect:
  - Dream at 8 rows: none.
  - LLaDA at 8 rows: a small left-to-right tendency.
  - LLaDA at 128 rows: a strong left-to-right tendency (−1.01 log-worth). On two-hop items, the share of traces in which the prerequisite is committed before `h` falls from 69% in the first slot to 42% in the last.

  This matches Exp 4's large LLaDA position effect at 128 rows.
- **Prerequisite committed before the dependent:** 82% (LLaDA) and 79% (Dream) on two-hop items at 8 rows, vs 51% and 55% on one-hop items.
- **Near-ties:** all LLaDA two-hop traces at 8 rows have a CF margin below 0.02, so commit orders at that size are hardware-sensitive.

### Stage 4: BFCL realism check (`results/bfcl/report.md`)

**Setup.** 400 items: 200 `simple_python` and all 200 `multiple`. Each runs under the original and the reversed schema, with 6 orders, on a 64-token canvas. Prompts come from BFCL's own code and scoring from its official AST checker, with no output repair. All four blocks finished on the rosetta21 A6000s, giving 9,600 decodes. The harness check (Dream, CF, 100 `live_simple` items, JSON format) scored 77% against a team reference of about 64%, so no harness fix was needed.

| Model | Schema | L2R | R2L | random | CF | CF − L2R |
|---|---|---:|---:|---:|---:|---:|
| LLaDA | original | 41.2 | 7.2 | 18.7 | 50.5 | +9.2 [+3.5, +15.0] |
| LLaDA | reversed | 40.0 | 4.0 | 17.1 | 47.8 | +7.8 [+2.0, +13.2] |
| Dream | original | 77.5 | 6.2 | 15.0 | 66.0 | −11.5 [−17.0, −6.0] |
| Dream | reversed | 78.8 | 2.8 | 17.6 | 64.2 | −14.5 [−20.2, −8.8] |

Values are AST accuracy in %, with intervals clustered by item. Random is the mean of 3 seeds.

- **Error types differ by order** (`bfcl_errors.png`):
  - R2L fails mostly on format: LLaDA has 64% parse errors; Dream has 51–60% wrong call counts, as it commits trailing end tokens first and leaves only about 9–10 content tokens.
  - Random orders mostly produce parse and argument errors.
  - CF's extra losses in Dream are argument errors: 20–25% vs 7.5–8% under L2R.
  - Wrong-function errors are rare under every order (0–3%).
- **LLaDA's parse errors are format failures**, even under L2R (30%). It often writes JSON-style lists like `["name", {args}]` instead of Python calls, or adds a trailing period. Under the no-repair rule these count as errors.
- **Reversing the schema matters little:** every reversed − original contrast is within ±3.5 points. Only R2L's drops (−3.2 LLaDA, −3.5 Dream) and Dream's random gain (+2.6) exclude 0.
- **A late function-name commit goes with wrong-function errors.** This is an association only. Among parseable CF and random outputs, the name's normalized commit rank predicts a wrong-function error:
  - LLaDA: mixed logistic log-odds +4.28 [3.77, 4.78]; GEE +4.94 [3.31, 6.56].
  - Dream: +2.58 [1.91, 3.24]; GEE +3.22 [1.26, 5.19].
  - Base rates are low (2–3%).
- **Secondary lenient-parse score** (rules preregistered before scoring, `experiments/bfcl/lenient.py`): keep the first call or list, and rewrite JSON-style `["name", {args}]` structures as Python calls.

  | Model, original schema | L2R | R2L | random | CF | CF − L2R |
  |---|---:|---:|---:|---:|---:|
  | LLaDA, lenient | 55.2 | 25.0 | 27.6 | 56.0 | +0.8 [−5.5, +7.0] |
  | Dream, lenient | 79.8 | 12.2 | 18.2 | 67.8 | −12.0 [−17.5, −6.5] |

  - **LLaDA:** lenient parsing recovers 14 points under L2R but only 5.5 under CF, which erases CF's strict advantage. On the reversed schema, CF − L2R is −1.2 [−7.5, 4.8].
  - **Unchanged:** R2L and random still collapse, and Dream's CF deficit stays.
- **Autoregressive reference** (Qwen2.5-7B-Instruct, greedy, 64 new tokens, the same prompts; rosetta15 A100):
  - AST accuracy 95.8% [93.8, 97.8] on the original schema and 91.5% [88.8, 94.0] on the reversed; reversal costs 4.2 points [1.8, 6.8].
  - 99% of outputs parse, and the lenient rules change nothing.
  - Sanity set: 76%, against Dream CF's 77%.
  - The best diffusion setting (Dream L2R, 77.5% strict, 79.8% lenient) trails it by about 16–18 points. This is a descriptive comparison across models and hardware, not an order effect.
- **CF commit pattern** (`bfcl_commit_heatmap.png`): CF commits the trailing end-token padding and the opening tokens first, and the middle of the call (the arguments) last. The first end token is committed at a normalized step of 0.61 for LLaDA and 0.89 for Dream.

## Limitations

- **Synthetic tasks.** RQ1 and RQ2 use synthetic two-field lookup tables with a fixed JSON output scaffold; both value fields are masked. (Only the Phase 1/1.5 Exp 3 design prefilled field a.) The BFCL check probes the gap to real tool calls, but it does not test dependency order directly.
- **Unvalidated row format.** Exp 4 and Stage 3 use the V2 row format, which passed no gate: Phase 1.5 froze no format. Exp 4 sizes come from its own dev calibration, and Dream's size is outside the 40–80% band. See `experiments/exp4/DECISIONS.md`.
- **Two models, different table sizes.** Each model was tested at a size calibrated to it (LLaDA 128, Dream 16; Stage 3 used LLaDA 64), so between-model comparisons are descriptive. Dream's Exp 4 two-hop items sit near ceiling (96% on dev, outside the 40–80% band), which compresses its H2 gap. Read Dream's H2 as a near-ceiling result.
- **No frozen Phase 1.5 configuration.** The gate failed for both models. Exp 4 calibrated its own size on dev, and no Phase 1.5 test split exists.
- **GPU types.** RQ1, Exp 4 and BFCL ran on RTX A6000; Phase 1.5, Stage 3, the three-field study and the Qwen reference ran on A100-PCIE-40GB. Each stage uses one GPU type. Across GPU types, about 2–5% of row-level decisions flip, almost all where the margin is below 0.02. In Stage 3 that covers most LLaDA CF traces (94–100%), so compare Stage 3 with the other stages at the level of effects only.
- **Near-tied CF choices.** Many CF decisions in LLaDA are near-ties. CF commit orders are therefore deterministic for a fixed GPU and stack, but fragile across hardware.
- **Interaction not identifiable with two fields.** H1's role × position interaction cannot be estimated in a two-field design (see Stage 3). The three-field study can estimate it, but its one-hop control shows that role labels there also track input position.
- **Three-field PREREG error.** The preregistered model-free slot measure (POS) is contaminated by the reference field's own slot effect; use the Plackett–Luce slot effect instead.
- **Orders dropped for compute.** Stage 3 ran only CF, PF and DF.
- **Autoregressive reference on different hardware.** Qwen2.5-7B-Instruct ran on A100 while the diffusion BFCL runs used A6000; it is a descriptive reference only.
- **Lenient parse is secondary.** It is preregistered but post hoc relative to the strict analysis; the rules were chosen from failure types already observed.

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
# Three-field RQ1 study (rosetta15 A100)
.venv/bin/python -m experiments.rq1_3f.identifiability
.venv/bin/python -m experiments.rq1_3f.audit --config experiments/rq1_3f/config_main-n8.yaml
.venv/bin/python -m dlm.runner launch --exp experiments.rq1_3f.exp --config experiments/rq1_3f/config_main-n8.yaml   --stage rq1_3f --trace main-n8   --models llada,dream --gpus 2,3 --expect-gpu A100
.venv/bin/python -m dlm.runner launch --exp experiments.rq1_3f.exp --config experiments/rq1_3f/config_main-n128.yaml --stage rq1_3f --trace main-n128 --models llada --gpus 6,7 --expect-gpu A100
.venv/bin/python -m experiments.rq1_3f.dev_check
.venv/bin/python -m experiments.rq1_3f.analyze --traces main-n8,main-n128
# BFCL lenient score and AR reference
PYTHONNOUSERSITE=1 /data/rbg/users/linrui/venvs/bfcl-eval-2026.3.23/bin/python experiments/bfcl/score.py --stage bfcl --trace test-orig --lenient
.venv/bin/python -m experiments.bfcl.ar --config experiments/bfcl/config_ar.yaml --trace test-ar --gpu 0 --expect-gpu A100
PYTHONNOUSERSITE=1 /data/rbg/users/linrui/venvs/bfcl-eval-2026.3.23/bin/python experiments/bfcl/score.py --stage bfcl --trace test-ar --models qwen [--lenient]
.venv/bin/python -m experiments.bfcl.analyze --traces test-orig,test-rev --sanity sanity --ar test-ar --ar-sanity sanity-ar
# Stage 3 rerun (same configs, results/stage3_rerun)
.venv/bin/python -m experiments.stage3.analyze --stage stage3_rerun && .venv/bin/python -m experiments.stage3.compare_rerun
# Figures
MPLCONFIGDIR=/data/scratch/linrui/llada_home/.mpl .venv/bin/python -m experiments.figures
```
