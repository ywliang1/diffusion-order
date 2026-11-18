# RQ1 role × layout commit-rank study

## llada: H1 verdict

**contradicted (bootstrap CI of the position effect lies within ±0.1).** Rows: 1600; hosts/GPUs/commits: [('rosetta21.csail.mit.edu', 'NVIDIA RTX A6000', '450a96a2f15dafadd6b2e033d2f371f027aa48a0')].

## llada: two-hop effects on normalized CF rank (primary)

| Effect | Mixed model coef [95% CI] | p | Bootstrap contrast [95% CI] |
|---|---:|---:|---:|
| Position (right − left) | +0.013 [-0.028, +0.053] | 0.544 | +0.013 [-0.018, +0.043] |
| Role (dependent − prerequisite) | +0.568 [+0.527, +0.608] | 2.82e-167 | +0.568 [+0.505, +0.630] |
| Field (b − a) | +0.043 [+0.002, +0.083] | 0.039 | +0.043 [-0.043, +0.128] |
| Role × position | -0.000 [-0.081, +0.081] | 1 | +0.000 [+0.000, +0.000] |

Mixed model: 1600 field rows, 200 sources, optimizer powell, converged True, source variance 0.0000, residual variance 0.1695.

## llada: cells

| Hop | Query direction | Layout | n | Left field first | Prerequisite first | a correct | b correct | Both correct |
|---:|---|---|---:|---:|---:|---:|---:|---:|
| 2 | a | ab | 200 | 84.0 [79.0, 89.0] | 84.0 [79.0, 89.0] | 100.0 [100.0, 100.0] | 100.0 [100.0, 100.0] | 100.0 [100.0, 100.0] |
| 2 | a | ba | 200 | 23.0 [17.5, 29.0] | 77.0 [71.0, 82.5] | 100.0 [100.0, 100.0] | 100.0 [100.0, 100.0] | 100.0 [100.0, 100.0] |
| 2 | b | ab | 200 | 21.5 [16.0, 27.5] | 78.5 [72.5, 84.0] | 100.0 [100.0, 100.0] | 100.0 [100.0, 100.0] | 100.0 [100.0, 100.0] |
| 2 | b | ba | 200 | 74.0 [68.0, 80.0] | 74.0 [68.0, 80.0] | 100.0 [100.0, 100.0] | 100.0 [100.0, 100.0] | 100.0 [100.0, 100.0] |
| 1 | a | ab | 200 | 48.5 [41.5, 55.5] | 48.5 [41.5, 55.5] | 99.5 [98.5, 100.0] | 100.0 [100.0, 100.0] | 99.5 [98.5, 100.0] |
| 1 | a | ba | 200 | 35.0 [28.5, 41.5] | 65.0 [58.5, 71.5] | 100.0 [100.0, 100.0] | 100.0 [100.0, 100.0] | 100.0 [100.0, 100.0] |
| 1 | b | ab | 200 | 45.0 [38.0, 52.0] | 55.0 [48.0, 62.0] | 100.0 [100.0, 100.0] | 100.0 [100.0, 100.0] | 100.0 [100.0, 100.0] |
| 1 | b | ba | 200 | 36.0 [29.5, 42.5] | 36.0 [29.5, 42.5] | 100.0 [100.0, 100.0] | 100.0 [100.0, 100.0] | 100.0 [100.0, 100.0] |

## llada: alignment

Prerequisite field committed first: two-hop 78.4 [75.2, 81.5], one-hop (direction field) 51.1 [49.0, 53.2], difference 27.3 [23.6, 30.8] percentage points.

## llada: CF margins

Traces with a CF margin below 0.02: 91.1%. Position effect without them: +0.043 [-0.170, +0.255]; on fully correct two-hop traces only: +0.013 [-0.018, +0.043].

## llada: one-hop control effects (descriptive)

| Effect | Mixed model coef [95% CI] | p | Bootstrap contrast [95% CI] |
|---|---:|---:|---:|
| Position (right − left) | -0.177 [-0.225, -0.130] | 4.08e-13 | -0.177 [-0.223, -0.135] |
| Role (dependent − prerequisite) | +0.022 [-0.025, +0.070] | 0.358 | +0.022 [-0.020, +0.065] |
| Field (b − a) | +0.113 [+0.065, +0.160] | 4.29e-06 | +0.113 [-0.005, +0.228] |
| Role × position | -0.000 [-0.096, +0.096] | 1 | +0.000 [+0.000, +0.000] |

Mixed model: 1600 field rows, 200 sources, optimizer powell, converged True, source variance 0.0000, residual variance 0.2396.

## dream: H1 verdict

**supported (position effect excludes 0 in both the mixed model and the bootstrap).** Rows: 1600; hosts/GPUs/commits: [('rosetta21.csail.mit.edu', 'NVIDIA RTX A6000', '450a96a2f15dafadd6b2e033d2f371f027aa48a0')].

## dream: two-hop effects on normalized CF rank (primary)

| Effect | Mixed model coef [95% CI] | p | Bootstrap contrast [95% CI] |
|---|---:|---:|---:|
| Position (right − left) | -0.052 [-0.095, -0.010] | 0.0155 | -0.052 [-0.090, -0.015] |
| Role (dependent − prerequisite) | +0.378 [+0.335, +0.420] | 8.22e-68 | +0.378 [+0.318, +0.440] |
| Field (b − a) | +0.323 [+0.280, +0.365] | 5.55e-50 | +0.323 [+0.235, +0.412] |
| Role × position | -0.000 [-0.085, +0.085] | 1 | +0.000 [+0.000, +0.000] |

Mixed model: 1600 field rows, 200 sources, optimizer powell, converged True, source variance 0.0000, residual variance 0.1883.

## dream: cells

| Hop | Query direction | Layout | n | Left field first | Prerequisite first | a correct | b correct | Both correct |
|---:|---|---|---:|---:|---:|---:|---:|---:|
| 2 | a | ab | 200 | 82.5 [77.0, 87.5] | 82.5 [77.0, 87.5] | 99.5 [98.5, 100.0] | 96.0 [93.0, 98.5] | 95.5 [92.5, 98.0] |
| 2 | a | ba | 200 | 12.5 [8.0, 17.0] | 87.5 [83.0, 92.0] | 99.5 [98.5, 100.0] | 97.5 [95.0, 99.5] | 97.0 [94.5, 99.0] |
| 2 | b | ab | 200 | 44.5 [37.5, 51.5] | 55.5 [48.5, 62.5] | 99.5 [98.5, 100.0] | 98.0 [96.0, 99.5] | 97.5 [95.0, 99.5] |
| 2 | b | ba | 200 | 50.0 [43.0, 57.0] | 50.0 [43.0, 57.0] | 99.0 [97.5, 100.0] | 97.5 [95.0, 99.5] | 96.5 [93.5, 99.0] |
| 1 | a | ab | 200 | 54.5 [47.5, 61.0] | 54.5 [47.5, 61.0] | 94.0 [90.5, 97.0] | 96.5 [94.0, 99.0] | 90.5 [86.5, 94.5] |
| 1 | a | ba | 200 | 44.5 [37.5, 51.5] | 55.5 [48.5, 62.5] | 99.0 [97.5, 100.0] | 93.0 [89.5, 96.5] | 92.5 [88.5, 96.0] |
| 1 | b | ab | 200 | 67.5 [61.0, 74.0] | 32.5 [26.0, 39.0] | 65.0 [58.5, 71.5] | 65.5 [59.0, 72.0] | 53.5 [46.5, 60.5] |
| 1 | b | ba | 200 | 57.0 [50.0, 64.0] | 57.0 [50.0, 64.0] | 95.5 [92.5, 98.0] | 92.5 [88.5, 96.0] | 89.0 [84.5, 93.0] |

## dream: alignment

Prerequisite field committed first: two-hop 68.9 [65.9, 72.0], one-hop (direction field) 49.9 [47.0, 52.8], difference 19.0 [14.8, 23.4] percentage points.

## dream: CF margins

Traces with a CF margin below 0.02: 9.8%. Position effect without them: -0.081 [-0.124, -0.037]; on fully correct two-hop traces only: -0.054 [-0.092, -0.017].

## dream: one-hop control effects (descriptive)

| Effect | Mixed model coef [95% CI] | p | Bootstrap contrast [95% CI] |
|---|---:|---:|---:|
| Position (right − left) | +0.117 [+0.069, +0.166] | 2.03e-06 | +0.117 [+0.065, +0.170] |
| Role (dependent − prerequisite) | -0.002 [-0.051, +0.046] | 0.919 | -0.003 [-0.060, +0.055] |
| Field (b − a) | +0.102 [+0.054, +0.151] | 3.41e-05 | +0.102 [+0.003, +0.203] |
| Role × position | +0.000 [-0.097, +0.097] | 1 | +0.000 [+0.000, +0.000] |

Mixed model: 1600 field rows, 200 sources, optimizer powell, converged True, source variance 0.0000, residual variance 0.2447.

## Interpretation limits

- Size 8, V2 format, single-token values: with two content tokens a field rank is 0 (first) or 1 (second).
- Accuracy is near ceiling here by design (no 40–80% band); RQ2 is not addressed by this study.
- Ranks of a and b sum to 1 within a trace, so the per-source random intercept is expected to be near zero; the source-clustered bootstrap is reported beside every mixed-model estimate.
- Models are analysed separately; between-model differences are descriptive.

## Deviations

# RQ1 study decisions and deviations

- 2026-11-17: Study approved by the team to run in parallel with Phase 1.5b, V2 format, size 8, CF only.
- 2026-11-17: Main run complete on rosetta21 A6000 (1,600 CF traces per model, commit `450a96a`).
- 2026-11-17: Analysis note (not a change to the plan). With two single-token fields, the two ranks in a trace sum to 1, so the pre-registered role × position interaction is identically zero in the data (bootstrap [0, 0]); the mixed model's interval for it reflects only its standard error. The design is balanced, so refitting without the interaction gives identical main effects (LLaDA position +0.013 [−0.028, +0.053], role +0.568; Dream position −0.052 [−0.095, −0.010], role +0.378). The interaction becomes identifiable only with multi-token fields (Stage 3).
- 2026-11-17: Caveat. 91.1% of LLaDA traces (9.8% of Dream's) have a CF margin below 0.02, because both fields are near probability 1 at size 8. The role effect is systematic across 800 two-hop traces, but individual LLaDA commit orders are fragile (Stage 0: about 30% of decisions with margin < 0.01 flip between GPU types).
- 2026-11-18: Correction to the 2026-11-17 analysis note above. Multi-token fields do **not** make the role × position interaction identifiable. With two fields per trace, the field ranks sum to a constant for any k, and the contrast is exactly 0 in Stage 3 as well (`experiments/stage3/DECISIONS.md`). A design that can estimate it needs a third field; `experiments/rq1_3f/PREREG.md` is a draft for review.
