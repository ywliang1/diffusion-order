# Team update: generation order in diffusion tool calling

For Linrui, Xiaoyang and Yeyin. Covers every experiment on branch `phase2` through commit `169be43` (2026-11-18). All numbers come from `results/SUMMARY.md`, the stage reports under `results/`, and each stage's `PREREG.md` and `DECISIONS.md`. Intervals are 95% bootstraps clustered by source (or by item for BFCL), 10,000 resamples, unless noted.

**Terms used below**
- **CF (confidence-first):** at each step, commit the masked position the model is most confident about. One token is committed per forward pass.
- **PF / DF (prerequisite-first / dependent-first):** commit every token of the prerequisite field (or the dependent field) first, using the CF rule inside each field.
- **L2R / R2L / random:** fixed left-to-right, right-to-left, or seeded random commit order (random is averaged over 3 seeds).
- **Normalized commit rank:** a token's commit position among the content tokens, scaled from 0 (first) to 1 (last). A field's rank is the mean over its tokens.
- **Prerequisite / dependent:** in a two-hop item, the dependent field can only be found by first looking up the prerequisite.
- **One-hop control:** the same item with both values read directly from the anchor row, so "prerequisite" and "dependent" are only labels.
- **Log-worth:** the Plackett–Luce (PL) model's score for how early a field is committed. Higher means earlier. A negative slot effect (last − first) means later output slots are committed later, i.e. a left-to-right tendency.
- **DiD:** the three-field study's difference-in-differences in the share of traces in which a field is committed before the reference field `h`.

## 1. TL;DR

- **H2 is supported.** PF beats DF on the dependent field for two-hop items, and the gap is larger than on one-hop controls. LLaDA: +54.5 [49.7, 59.2] points two-hop vs −1.0 [−2.8, 0.5] one-hop (Exp 4), and +42.0 to +42.8 with 2–3-token values. Dream's gap is smaller and near ceiling (+14.9 [11.8, 18.1] vs +8.6 [6.0, 11.2]). Verdict: supported in 5 of 6 model × value-length cells, partly supported in the sixth.
- **H1 is inconclusive.** Dependency role dominates CF commit order: the dependent field is committed 0.37–0.63 rank units later. Output position matters little at easy settings and strongly only for LLaDA at 128 rows (+0.290 [+0.235, +0.345]). The three-field study finds **no evidence that the dependency changes the slot effect**: the same interaction appears on one-hop controls, so it most likely reflects where values sit in the input.
- **BFCL: order matters a lot, but not in CF's favor once format is set aside.** R2L and random collapse in both models. LLaDA's CF advantage over L2R (+9.2 [3.5, 15.0] strict) disappears under lenient parsing (+0.8 [−5.5, 7.0]), so it was a format effect. Dream's CF trails L2R under both scorings (−11.5 [−17.0, −6.0] strict, −12.0 [−17.5, −6.5] lenient). An autoregressive reference, Qwen2.5-7B-Instruct, scores 95.8% (descriptive only).
- **LLaDA's Phase 1 order effect was at least partly format confusion.** In explicit row formats LLaDA scores 100% on every condition and order up to 16 rows, with no A-first vs B-first gap.
- **Main caveat:** every RQ1/RQ2 result after Phase 1.5 uses the V2 row format, which **passed no gate**, at table sizes calibrated separately per model. Dream's Exp 4 two-hop dev accuracy was 96%, outside the 40–80% band, so its H2 result is near ceiling. Conclusions hold for V2 at these sizes, not for a validated task.

Figures: [rank by role × position](figures/rank_role_position.png) · [PF − DF gap](figures/pf_df_gap.png) · [BFCL error types](figures/bfcl_errors.png) · [BFCL commit heatmap](figures/bfcl_commit_heatmap.png) (PDFs alongside).

## 2. What we ran, in order

| Stage | Question | Design and n | Host, GPU | Commit(s) |
|---|---|---|---|---|
| **Phase 1 pilot** | Do commit order and a prefilled value change answers on a tiny lookup task? | LLaDA and Dream; Exp 1 copy (20 instances), Exp 2 lookup (Direct / Shared-path / Separate-path × sizes 4, 8, 16 × A-first, B-first, CF; 200 sources), Exp 3 prefilled-A branches. 10,260 rows per model. | 8× RTX A6000 (environment matches rosetta7) | `181661f`, `605bfad`, `6ae2ccd`, `f739be2` (branch `phase1-pilot`) |
| **Code audit** | Is the Phase 1 code fit to extend? | Read-only audit plus a 5-row replay per model. | rosetta15 A100 | `03a4017` |
| **Stage 0 equivalence** | Does the new `dlm` stack reproduce Phase 1, and what does an A100 change? | Full replay of Phase 1 (10,260 rows per model); batching check (50 × 3); A100 replay of Exp 2 (5,400 rows per model). | rosetta21 A6000; replay on rosetta15 A100 | `75a8918` |
| **Phase 1.5 / 1.5b format fix** | Can a prompt format make Direct ≥ 90% while Shared-path stays at 40–80%? | 1.5: V1–V4 at sizes 4, 8, 16, 100 dev sources per size (10,800 rows per model) plus a V3-nochat arm (2,700 per model). 1.5b: V2 at 16–128 rows and V2-with-decoys at 16–64 (6,300 rows per model). Dev only; no test split was run. | 1.5: rosetta15 A100. 1.5b: rosetta21 A6000 | 1.5: `0525b72`, `7f49990`. 1.5b: `e795139` |
| **RQ1 study** | Under CF, do role and output position each shift commit rank? | V2, 8 rows, CF only; 2 query directions × 2 layouts × 2 hops; 200 sources, 1,600 traces per model. | rosetta21 A6000 | `450a96a` |
| **Exp 4** | H2 (PF vs DF) and H1 at a harder size | V2; sizes calibrated on dev: LLaDA 128 rows (100 sources), Dream 16 rows (200 sources); 8 items per source × 8 orders (CF, PF, DF, L2R, R2L, 3 random). 6,400 rows (LLaDA), 12,800 (Dream). | rosetta21 A6000 | `e6dbb9b` |
| **Stage 3** | Do H1/H2 hold with 2- and 3-token values? | Exp 4 design with k = 2, 3 tokens per value; LLaDA 64 rows, Dream 16; 100 sources; CF, PF, DF only; 2,400 rows per model × k. Full rerun to `results/stage3_rerun/`. | rosetta15 A100 (both runs) | `58d28a6`; rerun `5220168`, `bfcc85e` |
| **Three-field RQ1 study** | Can we estimate role × position (H1b), which two fields cannot identify? | Adds an independent reference field `h`; all 6 output orders; CF only. 8 rows: 200 sources, 4,800 traces per model. LLaDA 128 rows: 100 sources, 2,400 traces. | rosetta15 A100 | `bfcc85e` |
| **BFCL realism check** | Does order matter on real single-turn calls? | 400 items (200 `simple_python`, 200 `multiple`) × original/reversed schema × 6 orders, 64-token canvas, official AST checker, no repair. 2,400 decodes per model × schema. Plus a lenient-parse score and a Qwen2.5-7B-Instruct AR reference (800 generations + 100-item sanity set). | Diffusion: rosetta21 A6000. Qwen: rosetta15 A100 | LLaDA `976ebb8` / `811960e`; Dream `d9d8bfa` / `8bd8a31`; Qwen `7c450c7` |

Short notes per stage:

- **Phase 1:** both models passed G0 and G1. G2 failed at every size: Direct B was far below 90% because the model copied the target row's H. A-first beat B-first on Shared-path, and a prefilled wrong A dragged B along with it.
- **Audit and Stage 0:** the audit found that Direct B errors are column-choice errors, results flip across GPU types at near-ties, and unknown order names silently became B-first. The new `dlm` stack fixed these issues and reproduced Phase 1 exactly (10,260/10,260 rows per model). Because batching changed some decisions, every later stage runs at batch size 1 on one GPU type.
- **Phase 1.5 / 1.5b:** no variant passed the gate for either model. Explicit formats (V2, V3) made Direct easy but also made Shared-path too easy. Per the rule, nothing was frozen.
- **RQ1 study:** measures commit order only, so it needed no accuracy band.
- **Exp 4:** calibrated its own size because Phase 1.5 froze no format (a preregistration deviation, §5).
- **Stage 3 and three-field:** follow-ups to H1. Stage 3 showed that two fields cannot identify the role × position interaction for any k; the three-field design can.

## 3. Results by stage

### Phase 1 pilot (A6000)

| Measure | LLaDA | Dream |
|---|---|---|
| G2 gate | failed at sizes 4, 8, 16 | failed at sizes 4, 8, 16 |
| Direct B accuracy, A-first (sizes 4 / 8 / 16) | 23.0 / 28.5 / 24.0% | 33.0 / 36.5 / 39.5% |
| Shared-path B, A-first − B-first (sizes 4 / 8 / 16) | 27.5 [20.0, 35.0] / 43.5 [36.0, 51.0] / 38.0 [31.0, 45.0] | 31.0 [24.0, 38.0] / 34.5 [27.5, 41.5] / 38.5 [31.5, 46.0] |
| Exp 3 Shared-path, Gold − Masked B (sizes 4 / 8 / 16) | 37.0 / 46.0 / 40.0 | 32.5 / 36.0 / 40.5 |
| Wrong-A branch: B equals the wrong row's link, Shared vs Separate (size 8) | 93.5 vs 6.5% | 90.0 vs 26.0% |

The order effect is pilot evidence. Phase 1.5 later showed it was partly format confusion for LLaDA (§4). n = 200 sources per size; source: `results/phase1/report.md`.

### Audit and Stage 0

| Check | LLaDA | Dream |
|---|---:|---:|
| Replay matches Phase 1 exactly (A6000) | 10,260 / 10,260 | 10,260 / 10,260 |
| Batched = unbatched decisions | 149 / 150 | 139 / 150 |
| A100 replay of Exp 2: row decisions flipped | 130 / 5,400 (2.4%) | 261 / 5,400 (4.8%) |
| Largest change in cell-level B accuracy | 1.0 point | 1.3 points |

About half the flips (48% and 51%) are in rows with a margin below 0.02. Audit finding: when Direct B is wrong under A-first, the answer is the target row's H in 426 of 449 LLaDA errors and 267 of 382 Dream errors.

### Phase 1.5 / 1.5b (dev only)

**Primary hypothesis (some format passes the gate): not supported.**

| Variant (dev) | LLaDA | Dream |
|---|---|---|
| V1, V4 (space-separated) | Direct B fails (59–88%) | Direct B fails (23–70%) |
| V2, V3 (explicit `key=… \| a=…`) at sizes 4, 8 | Direct 100%, but Shared-path 100% (above 80%) | Direct 89–98%, but Shared-path 87.3–95.7% |
| V2 at 128 rows (1.5b) | Shared-path 88.3 [83.3, 92.7] | Shared-path 19.7%; Direct 43–54% |
| V2 at 32 rows (1.5b) | Shared-path 100% | Shared-path 59.0% (in band), but Direct 78–84% |
| V2 with decoys | Separate-path drops to 1–2% | Separate-path 1–5% |

The closest variant was V3 (16 of 20 criteria). Test seeds 15002 and 15012 are unused.

### RQ1 study (V2, 8 rows, CF, A6000; 200 sources, 800 two-hop traces per model)

| Effect on normalized rank (two-hop) | LLaDA | Dream |
|---|---:|---:|
| Position (right − left) | +0.013 [−0.018, +0.043] | −0.052 [−0.090, −0.015] |
| Role (dependent − prerequisite) | +0.568 [+0.505, +0.630] | +0.378 [+0.318, +0.440] |
| Field (b − a) | +0.043 [−0.043, +0.128] | +0.323 [+0.235, +0.412] |
| Prerequisite committed first: two-hop vs one-hop | 78.4 vs 51.1% | 68.9 vs 49.9% |
| CF traces with a margin below 0.02 | 91.1% | 9.8% |
| **H1** | **not supported** (contradicted: CI within ±0.10) | **supported** (small; the right field is committed *earlier*) |

### Exp 4 (V2; LLaDA 128 rows, 100 sources; Dream 16 rows, 200 sources; A6000)

| Measure | LLaDA | Dream |
|---|---:|---:|
| PF − DF dependent accuracy, two-hop | +54.5 [49.7, 59.2] (400 items) | +14.9 [11.8, 18.1] (800 items) |
| PF − DF, one-hop | −1.0 [−2.8, 0.5] | +8.6 [6.0, 11.2] |
| Hop × order interaction | +55.5 [50.7, 60.2] | +6.2 [2.4, 10.2] |
| Two-hop dependent accuracy: PF / CF / DF | 89.5 / 76.8 / 35.0 | 96.5 / 95.6 / 81.6 |
| **H2** | **supported** | **supported** (near ceiling) |
| Position (right − left), CF two-hop | +0.290 [+0.235, +0.345] | +0.113 [+0.077, +0.147] |
| Field (b − a) | +0.240 [+0.170, +0.310] | +0.253 [+0.180, +0.323] |
| Role (dependent − prerequisite) | +0.630 [+0.560, +0.695] | +0.562 [+0.500, +0.623] |
| **H1 at this size** | **supported**, but confounded with field identity | **supported** |
| CF commits prerequisite first: two-hop vs one-hop | 81.5 vs 58.2% | 78.1 vs 64.9% |

In LLaDA, most of the position and field effect comes from one cell (two-hop, query b, layout ab). There CF commits the prerequisite first in only 43% of traces and gets both fields right in 42%.

### Stage 3: 2- and 3-token values (CF/PF/DF; 100 sources; A100)

| Model, k | Position | Role | PF − DF two-hop | PF − DF one-hop | Hop × order | H1 | H2 |
|---|---:|---:|---:|---:|---:|---|---|
| LLaDA, 2 (64 rows) | +0.052 [+0.023, +0.080] | +0.550 | +42.8 [38.5, 46.8] | +0.2 | +42.5 [38.2, 46.8] | supported | supported |
| LLaDA, 3 (64 rows) | +0.017 [+0.001, +0.034] | +0.541 | +42.0 [37.0, 47.0] | 0.0 | +42.0 [37.0, 47.0] | supported | supported |
| Dream, 2 (16 rows) | +0.071 [+0.046, +0.097] | +0.367 | +3.2 [1.2, 5.8] | +0.2 | +3.0 [0.0, 6.2] | supported | partly supported |
| Dream, 3 (16 rows) | −0.010 [−0.029, +0.007] | +0.373 | +14.5 [10.0, 19.2] | +1.5 | +13.0 [7.5, 18.8] | not supported (contradicted) | supported |

- **Within a field, CF does not go left to right.** The share of fields committed strictly left to right is about 50% at k=2 (chance 50%) and 14–28% at k=3 (chance 17%).
- **Fields are committed as blocks** in 85–98% of traces at k=2 and 68–93% at k=3.
- **The rerun reproduced all 9,600 rows bit for bit.**
- The role × position rows in this table are exactly 0 by construction and carry no information (§5).

### Three-field RQ1 study (CF; A100)

| Arm | H1b: DiD | H1b: PL interaction | Slot effect, last − first (PL log-worth) | One-hop control (DiD; PL) | H1b verdict | H1 verdict (prereg rule) |
|---|---:|---:|---:|---:|---|---|
| LLaDA, 8 rows (4,800 traces) | +0.063 [+0.017, +0.109] | −0.015 [−0.179, +0.149] | −0.130 [−0.196, −0.067] | +0.189; +0.71 | inconclusive | not supported (contradicted) |
| Dream, 8 rows (4,800) | −0.045 [−0.085, −0.006] | −0.174 [−0.325, −0.029] | −0.031 [−0.090, +0.028] | +0.021; +0.38 | supported | not supported (contradicted) |
| LLaDA, 128 rows (2,400) | +0.175 [+0.105, +0.245] | +0.295 [−0.136, +0.681] | −1.008 [−1.277, −0.791] | +0.195; +1.09 | inconclusive | supported |

- **Dev validity check:** passed in every arm (98.3–100%).
- **Prerequisite committed before the dependent:** 82.0% (LLaDA) and 78.6% (Dream) on two-hop items at 8 rows, vs 50.9% and 55.0% on one-hop. At 128 rows, LLaDA is 91.5% vs 54.6%.
- **LLaDA at 128 rows** gets all three fields right in only 59.3% of two-hop items.
- **H1 verdicts here** use the preregistered measure (POS), which turned out to be flawed (§5). Read the PL slot column instead.

### BFCL realism check (A6000; Qwen on A100)

AST accuracy, %, original schema; random is the mean of 3 seeds:

| Model | Scoring | L2R | R2L | random | CF | CF − L2R |
|---|---|---:|---:|---:|---:|---:|
| LLaDA | strict | 41.2 | 7.2 | 18.7 | 50.5 | +9.2 [+3.5, +15.0] |
| LLaDA | lenient | 55.2 | 25.0 | 27.6 | 56.0 | +0.8 [−5.5, +7.0] |
| Dream | strict | 77.5 | 6.2 | 15.0 | 66.0 | −11.5 [−17.0, −6.0] |
| Dream | lenient | 79.8 | 12.2 | 18.2 | 67.8 | −12.0 [−17.5, −6.5] |
| Qwen2.5-7B (AR) | strict = lenient | 95.8 [93.8, 97.8] (one greedy order) | | | | |

- **Reversed schema:**
  - Every diffusion reversed − original contrast is within ±3.5 points.
  - LLaDA's strict CF − L2R is +7.8 [+2.0, +13.2], and its lenient one is −1.2 [−7.5, 4.8].
  - Qwen drops 4.2 points [1.8, 6.8], to 91.5%.
- **Error types:**
  - LLaDA's strict parse errors are 30% under L2R and 64% under R2L.
  - Dream's R2L outputs are mostly wrong call counts (51–60%).
  - Dream's extra CF losses are argument errors (20–25% vs 7.5–8% under L2R).
  - Wrong-function errors are 0–3% under every order.
- **Function-name commit rank vs wrong-function errors (association only):** among parseable CF and random outputs, the mixed logistic log-odds are +4.28 [3.77, 4.78] (LLaDA) and +2.58 [1.91, 3.24] (Dream), on base rates of 2–3%.
- **Harness sanity set** (100 `live_simple` items, JSON format): Dream CF 77.0 [68.0, 85.0]; Qwen 76.0 [67.0, 84.0].

## 4. Implications for the paper

**What we can claim**
- **H2: prerequisite-first helps more on two-hop items.** It holds for both models, for 1-, 2- and 3-token values, with matched one-hop controls. For LLaDA the effect is large and stable (+42.0 to +54.5 points two-hop). For Dream it is smaller and partly ceiling-limited, so the two models' effect sizes should not be compared.
- **CF tends to commit the prerequisite first on two-hop items** much more often than on one-hop items:

  | Model | Study | Two-hop | One-hop |
  |---|---|---:|---:|
  | LLaDA | RQ1 | 78.4% | 51.1% |
  | LLaDA | Exp 4 | 81.5% | 58.2% |
  | LLaDA | three-field, 128 rows | 91.5% | 54.6% |
  | Dream | RQ1 | 68.9% | 49.9% |
  | Dream | Exp 4 | 78.1% | 64.9% |

  Combined with H2, this suggests CF often lands on the better order, but not always. In Exp 4, LLaDA's two-hop dependent accuracy is 76.8% under CF vs 89.5% under PF.
- **Role dominates commit order. Position is secondary and depends on difficulty.** At 8 rows, position effects are within or near ±0.10 and change sign between models. For LLaDA at 128 rows there is a strong left-to-right tendency, confirmed by the three-field PL slot effect (−1.008 log-worth).
- **The format-confusion finding.** LLaDA's large A-first advantage in Phase 1 shrank to nothing once the table format was explicit. Part of what looked like a dependency effect was the model misreading columns. Order effects measured in V2 are the ones to report.
- **BFCL:**
  - Commit order strongly affects real tool-call accuracy: R2L and random collapse in both models.
  - LLaDA's strict CF > L2R result should be reported as a **format effect**, not a reasoning benefit: L2R gains 14.0 points from lenient parsing, CF only 5.5.
  - Dream's CF deficit is robust. It shows up as argument errors, consistent with CF committing the end-token padding and the call's opening first and the arguments last.

**What we cannot claim**
- **That the dependency changes how output position affects commit order (H1b).** The three-field one-hop control shows an interaction as large or larger. In our task, the role labels also encode the value's position in the input (the prerequisite always sits before `h` in the anchor row). The prerequisite-first alignment above is therefore an association with the two-hop structure, not proof that the model tracks the dependency.
- **A clean H1 position effect.** Position, field identity and difficulty move together (Exp 4). The two-field design cannot test the interaction, and the three-field model-free slot measure is contaminated.
- **Anything about a validated task format.** All post-Phase-1.5 results use the ungated V2 format.
- **Between-model comparisons.** Each model ran at its own table size. These are descriptive only.
- **That diffusion models are N points worse than AR at tool calling.** The Qwen gap (about 16–18 points over the best diffusion setting) compares different models on different hardware. It is descriptive. It does show that the diffusion models' BFCL accuracy is limited by more than output format.

**How it fits together.** On the synthetic task, getting the prerequisite committed before the dependent clearly matters for accuracy (H2), and CF usually, but not always, does that. Commit order is driven mainly by the field's role and by input layout, with output position mattering mostly when lookup is hard. On real calls, the simple fixed orders and CF differ mainly in format and argument errors. There is no sign there that CF's ordering helps once format is set aside.

## 5. Caveats and deviations

- **No Phase 1.5 variant passed the dev gate,** so no format was frozen and no Phase 1.5 test split was run. Exp 4 and Stage 3 used V2 anyway. This is logged as a preregistration deviation in `experiments/exp4/DECISIONS.md`.
- **Exp 4 sizes came from its own dev calibration:**
  - LLaDA 128 rows, two-hop dev accuracy 73%, in band.
  - Dream 16 rows via the fallback branch, because no size reached 90% one-hop accuracy. **Its two-hop dev accuracy was 96%, outside the 40–80% band**, so its H2 result is near ceiling.
  - LLaDA used 100 sources, not 200, per the compute rule at 128 rows.
- **The two-field role × position interaction is not identifiable.** The two field ranks in a trace sum to a constant, so the contrast is exactly 0 for any number of tokens. Both the RQ1 note (corrected) and the Stage 3 PREREG wrongly said multi-token values would fix this.
- **The three-field slot measure (POS) was a preregistration error.** `h`'s position does not cancel in POS, so POS mixes in `h`'s own slot effect. For LLaDA at 8 rows, POS (+0.064) and the PL slot effect (−0.130) have opposite signs. The H1 verdicts follow the preregistered rule, but the PL slot effect is the interpretable measure. The DiD is unaffected.
- **The three-field one-hop control was expected to be null and is not** (see §4).
- **GPU types differ by stage.** Each stage stays on one GPU type:

  | GPU type | Stages |
  |---|---|
  | RTX A6000 | Phase 1, Stage 0 equivalence, Phase 1.5b, RQ1 study, Exp 4, BFCL diffusion runs |
  | A100-PCIE-40GB | Phase 1.5, Stage 3 and its rerun, the three-field study, the Qwen reference |

  Across GPU types, 2–5% of row decisions flip, almost all at margins below 0.02. Compare A100 stages with A6000 stages only at the level of effects. The Stage 3 rerun was meant to run on A6000s but ran on A100s: rosetta21 was down and rosetta7 was busy. It is a determinism check, not a hardware comparison.
- **Near-tied CF choices** are common in LLaDA: 91–100% of traces in several arms have a margin below 0.02. Its commit orders are deterministic on a fixed stack but fragile across hardware.
- **Exp 4's first analysis call wrote an empty summary.** The cause was not established; a stale-NFS-cache hypothesis was tested and not supported. The failure mode is now removed: `dlm.report.read_required` makes a missing or empty trace an error. All analyses were rerun, and every `summary.json` is byte-identical. There is no impact on results.
- **LLaDA's BFCL parse failures:**
  - Many outputs are JSON-style `["name", {args}]` lists or calls with a trailing period, so strict scoring counts them as parse errors (30% under L2R).
  - The lenient score handles these. It is preregistered but secondary, and its rules were chosen after seeing these failure types.
- **Other logged deviations:**
  - **Phase 1.5:** ran on A100, not the preregistered A6000.
  - **Stage 3:** ran only CF, PF and DF, for compute. LLaDA used 64 rows, not 128, because of its context limit.
  - **BFCL:** the Qwen reference ran on a different GPU type from the diffusion runs.
  - **Phase 1:** the handoff's LLaDA repo name was wrong (`ML-GSAI`); the run used `GSAI-ML/LLaDA-8B-Instruct`.

**Places where the sources disagree** (the newer file is used unless noted):
- **Qwen gap:** `experiments/bfcl/DECISIONS.md` says the AR model beats the best diffusion order by "about 18 points"; the newer `SUMMARY.md` says 16–18 (strict vs lenient). This update uses 16–18.
- **Best lenient diffusion score:** `SUMMARY.md` cites Dream L2R at 79.8% lenient. That is the original schema; on the reversed schema it is 80.2% (`results/bfcl/report.md`).
- **Dream RQ1 margin rate:** `SUMMARY.md` rounds it to 10%; the report gives 9.8%, used here.
- **Test count:** `SUMMARY.md` says 47 tests; `experiments/exp4/DECISIONS.md` (newer) says 50, and tests were added after both. No count is given here.
- **Multi-token identifiability:** the RQ1 DECISIONS note and the Stage 3 PREREG both said multi-token values would identify the interaction; later entries correct both.

## 6. Open questions and proposed next steps

| # | Question / step | Why | Owner |
|---|---|---|---|
| 1 | Redesign the one-hop control so that a value's input position is counterbalanced against its role (e.g. the prerequisite after `h` in half the sources) | Needed before we can say anything about H1b | |
| 2 | Find a harder task variant for Dream that puts two-hop accuracy in the 40–80% band | Dream's H2 is near ceiling | |
| 3 | Rerun the three-field study (and optionally Stage 3) on A6000s when rosetta21 is back | Cross-hardware check of the A100-only stages | |
| 4 | Decide whether we still need a gated, frozen format, or accept V2 and state it as a limitation | Phase 1.5 test seeds 15002 and 15012 are unused | |
| 5 | BFCL: test a schema-guided order (e.g. function name first, then arguments) and constrained output format | Separate format from ordering; Dream's CF argument errors | |
| 6 | Run the Qwen reference on A6000 if we want a same-hardware comparison | Descriptive gap currently crosses GPU types | |
| 7 | Retest the empty-summary bug with rosetta21 as the writing host | The only untested hypothesis | |
| 8 | Update the proposal text (RQ2, H2, Section 2) for the Direct / Shared-path / Separate-path and one-hop designs | `phase1_scope.md` "Proposal impact" | |

## 7. Reproducibility

- **Branch and commit:** `phase2`, results as of `169be43`. This file is the only change in the commit that adds it. The repo has no git remote yet.
- **Environments:** `.venv` for generation and analysis; `/data/rbg/users/linrui/venvs/bfcl-eval-2026.3.23` for BFCL data and scoring; `scripts/env.sh` for detached runs.
- **Row metadata:** every trace row records host, GPU, torch and transformers versions, git commit, model revision and seed.
- **Traces:** gitignored, on disk under `results/*/traces/`, except the two Qwen trace files.

```sh
.venv/bin/python -m pytest tests/
# Phase 1 (frozen; do not rerun). Check the report against its hash:
sha256sum -c results/phase1/report.sha256
# Stage 0
.venv/bin/python -m experiments.equivalence.compare --stage equivalence --trace a6000 --exps 1,2,3
# Phase 1.5 / 1.5b dev reports
.venv/bin/python -m experiments.phase1_5.analyze   --split dev --traces dev,dev-nochat
.venv/bin/python -m experiments.phase1_5.analyze_b --split dev --traces dev
# RQ1 study, Exp 4 (and its dev calibration), Stage 3 and its rerun
.venv/bin/python -m experiments.rq1.analyze --trace main
.venv/bin/python -m experiments.exp4.calibrate --trace dev
.venv/bin/python -m experiments.exp4.analyze --stage exp4 --trace main
.venv/bin/python -m experiments.stage3.analyze
.venv/bin/python -m experiments.stage3.analyze --stage stage3_rerun && .venv/bin/python -m experiments.stage3.compare_rerun
# Three-field study
.venv/bin/python -m experiments.rq1_3f.identifiability
.venv/bin/python -m experiments.rq1_3f.dev_check
.venv/bin/python -m experiments.rq1_3f.analyze --traces main-n8,main-n128
# BFCL: strict and lenient scoring (diffusion and Qwen), then the report
B=/data/rbg/users/linrui/venvs/bfcl-eval-2026.3.23/bin/python
PYTHONNOUSERSITE=1 $B experiments/bfcl/score.py --stage bfcl --trace test-orig [--lenient]
PYTHONNOUSERSITE=1 $B experiments/bfcl/score.py --stage bfcl --trace test-ar --models qwen [--lenient]
.venv/bin/python -m experiments.bfcl.analyze --traces test-orig,test-rev --sanity sanity --ar test-ar --ar-sanity sanity-ar
# Figures (results/figures/*.png, *.pdf)
MPLCONFIGDIR=/data/scratch/linrui/llada_home/.mpl .venv/bin/python -m experiments.figures
```

The launch commands that regenerate the traces themselves are in `results/SUMMARY.md` (Reproducibility) and in each stage's config files. The reports above are rebuilt from the traces on disk.
