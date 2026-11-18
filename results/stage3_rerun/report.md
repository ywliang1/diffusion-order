# Stage 3: multi-token values

## llada k=2: summary

Table size 64; rows 2400; hosts/GPUs/commits [('rosetta15.csail.mit.edu', 'NVIDIA A100-PCIE-40GB', '5220168ab1055e22dfbb187db57468f20f37634d')].

- **H1: supported (position effect excludes 0 in both the mixed model and the bootstrap).**
- **H2: supported (two-hop PF − DF > 0 and larger than in one-hop controls).**
- CF traces with a margin below 0.02: 94.1%.

## llada k=2: H1 (CF commit rank, two-hop, with role × position)

| Effect | Mixed model coef [95% CI] | p | Bootstrap contrast [95% CI] |
|---|---:|---:|---:|
| Position (right − left) | +0.052 [+0.029, +0.075] | 1.22e-05 | +0.052 [+0.023, +0.080] |
| Role (dependent − prerequisite) | +0.550 [+0.527, +0.573] | 0 | +0.550 [+0.516, +0.582] |
| Field (b − a) | +0.023 [+0.000, +0.046] | 0.0483 | +0.023 [-0.016, +0.063] |
| Role × position | +0.000 [-0.046, +0.046] | 1 | +0.000 [+0.000, +0.000] |

Mixed model: 800 field rows, 100 sources, optimizer powell, converged True, source variance 0.0000, residual variance 0.0279.

## llada k=2: within-field commit order under CF

| Hop | Field role | Fields committed left to right inside the field | Traces with each field committed as one block |
|---:|---|---:|---:|
| 2 | prerequisite | 51.0 [44.2, 57.8] | 93.5 [90.5, 96.2] |
| 2 | dependent | 49.5 [42.8, 56.5] | 93.5 [90.5, 96.2] |
| 1 | prerequisite | 48.8 [42.0, 55.5] | 97.8 [95.8, 99.2] |
| 1 | dependent | 50.7 [44.0, 57.5] | 97.8 [95.8, 99.2] |

## llada k=2: H2 (PF vs DF)

| Hop | Items | PF − DF dependent accuracy | Both right | Both wrong | Only PF right | Only DF right | McNemar p |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 2 | 400 | 42.8 [38.5, 46.8] | 226 | 1 | 172 | 1 | 2.91e-50 |
| 1 | 400 | 0.2 [0.0, 0.8] | 398 | 1 | 1 | 0 | 1 |

Hop × order interaction, (PF − DF | two-hop) − (PF − DF | one-hop): 42.5 [38.2, 46.8] points.

## llada k=2: accuracy by order

| Hop | Order | n items | Dependent correct | Prerequisite correct | Both correct |
|---:|---|---:|---:|---:|---:|
| 2 | CF | 400 | 96.5 [94.5, 98.2] | 97.5 [96.0, 98.8] | 96.5 [94.5, 98.2] |
| 2 | PF | 400 | 99.5 [98.8, 100.0] | 99.5 [98.8, 100.0] | 99.5 [98.8, 100.0] |
| 2 | DF | 400 | 56.8 [52.8, 60.8] | 83.5 [81.0, 85.8] | 56.8 [52.8, 60.8] |
| 1 | CF | 400 | 99.8 [99.2, 100.0] | 98.5 [97.2, 99.5] | 98.2 [96.8, 99.5] |
| 1 | PF | 400 | 99.8 [99.2, 100.0] | 99.5 [98.5, 100.0] | 99.2 [97.8, 100.0] |
| 1 | DF | 400 | 99.5 [98.8, 100.0] | 98.2 [97.0, 99.2] | 97.8 [96.0, 99.2] |

## llada k=2: alignment

Prerequisite field committed first: two-hop 93.2 [90.8, 95.8], one-hop (direction field) 57.2 [53.5, 61.0], difference 36.0 [31.2, 40.5] percentage points.

## llada k=3: summary

Table size 64; rows 2400; hosts/GPUs/commits [('rosetta15.csail.mit.edu', 'NVIDIA A100-PCIE-40GB', 'bfcc85ed03dc0c27a2999dd1f64dfd667d52883e')].

- **H1: supported (position effect excludes 0 in both the mixed model and the bootstrap).**
- **H2: supported (two-hop PF − DF > 0 and larger than in one-hop controls).**
- CF traces with a margin below 0.02: 100.0%.

## llada k=3: H1 (CF commit rank, two-hop, with role × position)

| Effect | Mixed model coef [95% CI] | p | Bootstrap contrast [95% CI] |
|---|---:|---:|---:|
| Position (right − left) | +0.017 [+0.002, +0.032] | 0.0223 | +0.017 [+0.001, +0.034] |
| Role (dependent − prerequisite) | +0.541 [+0.526, +0.556] | 0 | +0.541 [+0.516, +0.563] |
| Field (b − a) | -0.004 [-0.018, +0.011] | 0.622 | -0.004 [-0.029, +0.021] |
| Role × position | -0.000 [-0.029, +0.029] | 1 | +0.000 [-0.000, +0.000] |

Mixed model: 800 field rows, 100 sources, optimizer powell, converged True, source variance 0.0000, residual variance 0.0111.

## llada k=3: within-field commit order under CF

| Hop | Field role | Fields committed left to right inside the field | Traces with each field committed as one block |
|---:|---|---:|---:|
| 2 | prerequisite | 20.2 [15.2, 25.5] | 92.5 [89.5, 95.2] |
| 2 | dependent | 23.2 [18.0, 28.7] | 92.5 [89.5, 95.2] |
| 1 | prerequisite | 24.8 [18.8, 31.0] | 89.5 [85.0, 93.5] |
| 1 | dependent | 28.0 [22.2, 34.2] | 89.5 [85.0, 93.5] |

## llada k=3: H2 (PF vs DF)

| Hop | Items | PF − DF dependent accuracy | Both right | Both wrong | Only PF right | Only DF right | McNemar p |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 2 | 400 | 42.0 [37.0, 47.0] | 232 | 0 | 168 | 0 | 5.35e-51 |
| 1 | 400 | 0.0 [0.0, 0.0] | 400 | 0 | 0 | 0 | nan |

Hop × order interaction, (PF − DF | two-hop) − (PF − DF | one-hop): 42.0 [37.0, 47.0] points.

## llada k=3: accuracy by order

| Hop | Order | n items | Dependent correct | Prerequisite correct | Both correct |
|---:|---|---:|---:|---:|---:|
| 2 | CF | 400 | 98.8 [97.5, 99.8] | 99.2 [98.2, 100.0] | 98.8 [97.5, 99.8] |
| 2 | PF | 400 | 100.0 [100.0, 100.0] | 100.0 [100.0, 100.0] | 100.0 [100.0, 100.0] |
| 2 | DF | 400 | 58.0 [53.0, 63.0] | 85.8 [83.2, 88.2] | 58.0 [53.0, 63.0] |
| 1 | CF | 400 | 100.0 [100.0, 100.0] | 98.8 [97.2, 99.8] | 98.8 [97.2, 99.8] |
| 1 | PF | 400 | 100.0 [100.0, 100.0] | 100.0 [100.0, 100.0] | 100.0 [100.0, 100.0] |
| 1 | DF | 400 | 100.0 [100.0, 100.0] | 98.5 [97.0, 99.8] | 98.5 [97.0, 99.8] |

## llada k=3: alignment

Prerequisite field committed first: two-hop 96.5 [94.5, 98.2], one-hop (direction field) 46.5 [42.2, 50.5], difference 50.0 [45.2, 54.8] percentage points.

## dream k=2: summary

Table size 16; rows 2400; hosts/GPUs/commits [('rosetta15.csail.mit.edu', 'NVIDIA A100-PCIE-40GB', '5220168ab1055e22dfbb187db57468f20f37634d')].

- **H1: supported (position effect excludes 0 in both the mixed model and the bootstrap).**
- **H2: partly supported (two-hop PF − DF > 0, but the hop × order interaction CI includes 0).**
- CF traces with a margin below 0.02: 61.3%.

## dream k=2: H1 (CF commit rank, two-hop, with role × position)

| Effect | Mixed model coef [95% CI] | p | Bootstrap contrast [95% CI] |
|---|---:|---:|---:|
| Position (right − left) | +0.071 [+0.037, +0.105] | 4.6e-05 | +0.071 [+0.046, +0.097] |
| Role (dependent − prerequisite) | +0.367 [+0.333, +0.402] | 3.15e-99 | +0.367 [+0.315, +0.420] |
| Field (b − a) | -0.006 [-0.040, +0.028] | 0.737 | -0.006 [-0.078, +0.066] |
| Role × position | +0.000 [-0.068, +0.068] | 1 | +0.000 [-0.000, +0.000] |

Mixed model: 800 field rows, 100 sources, optimizer powell, converged True, source variance 0.0000, residual variance 0.0604.

## dream k=2: within-field commit order under CF

| Hop | Field role | Fields committed left to right inside the field | Traces with each field committed as one block |
|---:|---|---:|---:|
| 2 | prerequisite | 43.2 [36.2, 50.5] | 84.8 [80.2, 89.0] |
| 2 | dependent | 42.2 [35.5, 49.2] | 84.8 [80.2, 89.0] |
| 1 | prerequisite | 44.2 [37.8, 50.7] | 92.0 [88.5, 95.0] |
| 1 | dependent | 41.8 [35.2, 48.5] | 92.0 [88.5, 95.0] |

## dream k=2: H2 (PF vs DF)

| Hop | Items | PF − DF dependent accuracy | Both right | Both wrong | Only PF right | Only DF right | McNemar p |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 2 | 400 | 3.2 [1.2, 5.8] | 384 | 3 | 13 | 0 | 0.000244 |
| 1 | 400 | 0.2 [-2.2, 2.5] | 373 | 8 | 10 | 9 | 1 |

Hop × order interaction, (PF − DF | two-hop) − (PF − DF | one-hop): 3.0 [0.0, 6.2] points.

## dream k=2: accuracy by order

| Hop | Order | n items | Dependent correct | Prerequisite correct | Both correct |
|---:|---|---:|---:|---:|---:|
| 2 | CF | 400 | 98.8 [97.2, 100.0] | 100.0 [100.0, 100.0] | 98.8 [97.2, 100.0] |
| 2 | PF | 400 | 99.2 [98.0, 100.0] | 100.0 [100.0, 100.0] | 99.2 [98.0, 100.0] |
| 2 | DF | 400 | 96.0 [93.2, 98.2] | 99.0 [98.0, 99.8] | 96.0 [93.2, 98.2] |
| 1 | CF | 400 | 96.0 [93.8, 97.8] | 99.2 [98.2, 100.0] | 95.2 [92.8, 97.2] |
| 1 | PF | 400 | 95.8 [93.5, 97.8] | 99.0 [97.8, 100.0] | 94.8 [92.2, 97.0] |
| 1 | DF | 400 | 95.5 [93.2, 97.5] | 96.0 [93.8, 98.0] | 94.8 [92.2, 97.0] |

## dream k=2: alignment

Prerequisite field committed first: two-hop 79.8 [75.8, 83.8], one-hop (direction field) 64.5 [60.5, 68.5], difference 15.2 [9.5, 20.8] percentage points.

## dream k=3: summary

Table size 16; rows 2400; hosts/GPUs/commits [('rosetta15.csail.mit.edu', 'NVIDIA A100-PCIE-40GB', '5220168ab1055e22dfbb187db57468f20f37634d')].

- **H1: contradicted (bootstrap CI of the position effect lies within ±0.1).**
- **H2: supported (two-hop PF − DF > 0 and larger than in one-hop controls).**
- CF traces with a margin below 0.02: 98.5%.

## dream k=3: H1 (CF commit rank, two-hop, with role × position)

| Effect | Mixed model coef [95% CI] | p | Bootstrap contrast [95% CI] |
|---|---:|---:|---:|
| Position (right − left) | -0.010 [-0.035, +0.014] | 0.409 | -0.010 [-0.029, +0.007] |
| Role (dependent − prerequisite) | +0.373 [+0.348, +0.398] | 2.3e-195 | +0.373 [+0.333, +0.411] |
| Field (b − a) | +0.010 [-0.015, +0.034] | 0.44 | +0.010 [-0.042, +0.061] |
| Role × position | -0.000 [-0.049, +0.049] | 1 | -0.000 [-0.000, +0.000] |

Mixed model: 800 field rows, 100 sources, optimizer powell, converged True, source variance 0.0000, residual variance 0.0313.

## dream k=3: within-field commit order under CF

| Hop | Field role | Fields committed left to right inside the field | Traces with each field committed as one block |
|---:|---|---:|---:|
| 2 | prerequisite | 14.0 [9.8, 18.5] | 68.2 [62.3, 74.2] |
| 2 | dependent | 15.0 [10.5, 20.0] | 68.2 [62.3, 74.2] |
| 1 | prerequisite | 17.0 [12.2, 22.0] | 76.0 [70.5, 81.5] |
| 1 | dependent | 13.5 [8.8, 19.0] | 76.0 [70.5, 81.5] |

## dream k=3: H2 (PF vs DF)

| Hop | Items | PF − DF dependent accuracy | Both right | Both wrong | Only PF right | Only DF right | McNemar p |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 2 | 400 | 14.5 [10.0, 19.2] | 322 | 8 | 64 | 6 | 2.44e-13 |
| 1 | 400 | 1.5 [-1.2, 4.2] | 352 | 12 | 21 | 15 | 0.405 |

Hop × order interaction, (PF − DF | two-hop) − (PF − DF | one-hop): 13.0 [7.5, 18.8] points.

## dream k=3: accuracy by order

| Hop | Order | n items | Dependent correct | Prerequisite correct | Both correct |
|---:|---|---:|---:|---:|---:|
| 2 | CF | 400 | 96.5 [94.5, 98.2] | 99.2 [98.0, 100.0] | 96.0 [93.2, 98.2] |
| 2 | PF | 400 | 96.5 [94.5, 98.2] | 99.2 [98.0, 100.0] | 96.0 [93.2, 98.2] |
| 2 | DF | 400 | 82.0 [77.5, 86.5] | 97.5 [95.5, 99.0] | 81.5 [76.8, 86.0] |
| 1 | CF | 400 | 94.0 [91.0, 96.5] | 97.8 [96.0, 99.2] | 91.8 [88.0, 95.0] |
| 1 | PF | 400 | 93.2 [90.2, 95.8] | 96.2 [93.8, 98.5] | 89.8 [85.5, 93.5] |
| 1 | DF | 400 | 91.8 [88.8, 94.5] | 96.0 [93.8, 98.0] | 89.5 [85.5, 93.0] |

## dream k=3: alignment

Prerequisite field committed first: two-hop 90.2 [86.8, 93.8], one-hop (direction field) 79.5 [75.5, 83.5], difference 10.8 [5.5, 16.0] percentage points.

## Interpretation limits

- Results directory: results/stage3_rerun. Run on rosetta15 A100s (whole stage); compare with A6000 stages at the level of effects, not rows.
- Orders limited to CF, PF and DF (compute); L2R, R2L and random were not run in this stage.
- Table sizes: LLaDA 64 (128 exceeds its context with 3-token values), Dream 16 (its Exp 4 size).

## Deviations

# Stage 3 decisions and deviations

- 2026-11-18: Whole stage on rosetta15 A100s: rosetta21 A6000s are booked by BFCL and Exp 4 until morning and rosetta7 is saturated by other users. Orders limited to CF, PF and DF for compute. LLaDA at 64 rows because 128 rows exceed its 4,096-token context with 3-token values.
- 2026-11-18 (after the run): **The preregistered role × position interaction is not identifiable, for any k.** The prereg said k ≥ 2 makes it identifiable; that was wrong. Each trace has exactly two fields, one per role and one per position, and a field's rank is the mean normalized rank of its tokens among the 2k content tokens, so the two field ranks in a trace always sum to the same constant. The interaction contrast (dep-right − pre-right) − (dep-left − pre-left) equals (dep-right + pre-left) − (dep-left + pre-right), and each bracket is a within-trace sum, so the contrast is exactly 0. The report shows this: estimate 0 to 1e-17 in all four model × k cells. Impact: the interaction rows in `results/stage3/report.md` carry no information and are not interpreted. H1 main effects and H2 are unaffected. Testing the interaction would need a design in which field ranks do not sum to a constant, for example more than two output fields or a first-token rank. Neither was preregistered, and none was run.
- 2026-11-18 (after the run): Margin note. CF traces with a top-1 − top-2 margin below 0.02 at some step: LLaDA 94% (k=2) and 100% (k=3); Dream 61% (k=2) and 98.5% (k=3). Given the Stage 0 A100 replay, which flipped decisions mainly below this margin, row-level CF commit orders in this stage are hardware-sensitive. Compare effects with the A6000 stages, not individual rows.
- 2026-11-18 (before the rerun): **Stage 3 rerun, as the team requested.** The configs are unchanged (`config_k2.yaml`, `config_k3.yaml`: same seeds, sources, sizes and orders); outputs go to `results/stage3_rerun/`. The team asked for rosetta21 A6000s, so the rerun would match the RQ1, Exp 4 and BFCL hardware. rosetta21 is down and rosetta7's A6000s are all in use, so following the team's instruction ("steps 4 and 5 on the same GPU type" as the three-field stage), the rerun uses rosetta15 A100-PCIE-40GB, the same GPU type as the original Stage 3 run. It is therefore a same-hardware replication (a determinism check), not the A6000 comparison it was meant to be. Reported: the row-level match rate against `results/stage3/traces/`, and whether every Stage 3 verdict reproduces.
- 2026-11-18 (after the rerun): **The Stage 3 rerun is bit-identical to the original.** All 9,600 rows (4 model × k traces of 2,400) match the original exactly: same commit sequence, same probabilities, same correctness (`results/stage3_rerun/compare.json`). Both runs were on rosetta15 A100-PCIE-40GB; the rerun used commits `5220168` and `bfcc85e`. Every verdict and effect size reproduces (`results/stage3_rerun/report.md`). This confirms the stack is deterministic on a fixed GPU type. It does not test the A6000 comparison the rerun was meant for, because no A6000 was available.
