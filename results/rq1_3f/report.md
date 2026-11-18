# Three-field RQ1 study: role × slot on CF commit order

## llada main-n8: summary

Table size 8; CF traces 4800; hosts/GPUs/commits [('rosetta15.csail.mit.edu', 'NVIDIA A100-PCIE-40GB', 'bfcc85ed03dc0c27a2999dd1f64dfd667d52883e')].

- **H1b (role × slot): inconclusive.** DiD +0.063 [+0.017, +0.109]; PL interaction -0.015 [-0.179, +0.149] log-worth; joint 4-df role × slot Wald 117.4, p = 1.94e-24.
- **H1 (slot main effect): contradicted.** POS +0.064 [+0.046, +0.082]; PL slot (last − first) -0.130 [-0.196, -0.067].
- Two-hop traces with a CF margin below 0.02: 100.0%. PL converged: True; non-converged bootstrap refits: 0.

## llada main-n8: contrasts

| Hop | Contrast | Model-free (share before h) | Plackett–Luce (log-worth) |
|---:|---|---:|---:|
| 2 | role × slot (DiD / interaction) | +0.063 [+0.017, +0.109] | -0.015 [-0.179, +0.149] |
| 2 | slot main effect (last − first) | +0.064 [+0.046, +0.082] | -0.130 [-0.196, -0.067] |
| 2 | prerequisite: last − first | +0.032 [+0.004, +0.061] | |
| 2 | dependent: last − first | +0.095 [+0.066, +0.125] | |
| 2 | field b − field a | | +0.302 [+0.116, +0.491] |
| 1 | role × slot (DiD / interaction) | +0.189 [+0.148, +0.231] | +0.708 [+0.567, +0.864] |
| 1 | slot main effect (last − first) | +0.068 [+0.046, +0.090] | +0.027 [-0.028, +0.082] |
| 1 | prerequisite: last − first | -0.026 [-0.054, +0.000] | |
| 1 | dependent: last − first | +0.163 [+0.130, +0.195] | |
| 1 | field b − field a | | +0.226 [+0.002, +0.451] |

## llada main-n8: share committed before h, two-hop

| Role | Slot | n traces | Committed before h |
|---|---|---:|---:|
| prerequisite | first | 800 | 56.4 [50.9, 61.8] |
| prerequisite | middle | 800 | 61.5 [56.2, 66.6] |
| prerequisite | last | 800 | 59.6 [54.4, 64.8] |
| dependent | first | 800 | 29.5 [24.4, 34.6] |
| dependent | middle | 800 | 35.1 [29.8, 40.6] |
| dependent | last | 800 | 39.0 [33.9, 44.2] |

## llada main-n8: share committed before h, one-hop

| Role | Slot | n traces | Committed before h |
|---|---|---:|---:|
| prerequisite | first | 800 | 48.1 [42.6, 53.6] |
| prerequisite | middle | 800 | 52.8 [47.4, 57.9] |
| prerequisite | last | 800 | 45.5 [40.0, 50.9] |
| dependent | first | 800 | 38.8 [33.4, 44.1] |
| dependent | middle | 800 | 47.9 [42.5, 53.1] |
| dependent | last | 800 | 55.0 [50.0, 59.9] |

## llada main-n8: sensitivity

| Subset | Two-hop traces | DiD | POS |
|---|---:|---:|---:|
| excluding flip-sensitive traces | 0 | n < 50 | n < 50 |
| fully correct traces only | 2400 | +0.063 [+0.017, +0.109] | +0.064 [+0.046, +0.082] |

## llada main-n8: mean-rank mixed model, two-hop

Mean normalized rank (0 = committed first). Caveat (PREREG): ranks in a trace still sum to a constant, so a nonzero interaction here reflects dependence on where the other fields sit; the DiD and PL rows are the interpretable ones.

| Term | Coef [95% CI] |
|---|---:|
| Intercept | +0.551 [+0.526, +0.576] |
| C(role, Treatment('independent'))[T.dependent] | +0.237 [+0.200, +0.274] |
| C(role, Treatment('independent'))[T.prerequisite] | -0.208 [-0.245, -0.171] |
| C(slot, Treatment('first'))[T.last] | -0.137 [-0.173, -0.102] |
| C(slot, Treatment('first'))[T.middle] | -0.109 [-0.144, -0.073] |
| C(role, Treatment('independent'))[T.dependent]:C(slot, Treatment('first'))[T.last] | +0.131 [+0.080, +0.181] |
| C(role, Treatment('independent'))[T.prerequisite]:C(slot, Treatment('first'))[T.last] | +0.136 [+0.085, +0.186] |
| C(role, Treatment('independent'))[T.dependent]:C(slot, Treatment('first'))[T.middle] | +0.087 [+0.037, +0.138] |
| C(role, Treatment('independent'))[T.prerequisite]:C(slot, Treatment('first'))[T.middle] | +0.087 [+0.037, +0.137] |
| is_b | -0.082 [-0.102, -0.061] |

## llada main-n8: alignment

Prerequisite committed before dependent: two-hop 82.0 [79.5, 84.5], one-hop (nominal roles) 50.9 [49.5, 52.3], difference 31.1 [28.2, 34.0] points.

## llada main-n8: accuracy

| Hop | a correct | b correct | h correct | All three correct |
|---:|---:|---:|---:|---:|
| 2 | 100.0 [100.0, 100.0] | 100.0 [100.0, 100.0] | 100.0 [100.0, 100.0] | 100.0 [100.0, 100.0] |
| 1 | 100.0 [100.0, 100.0] | 100.0 [100.0, 100.0] | 100.0 [100.0, 100.0] | 100.0 [100.0, 100.0] |

## dream main-n8: summary

Table size 8; CF traces 4800; hosts/GPUs/commits [('rosetta15.csail.mit.edu', 'NVIDIA A100-PCIE-40GB', 'bfcc85ed03dc0c27a2999dd1f64dfd667d52883e')].

- **H1b (role × slot): supported.** DiD -0.045 [-0.085, -0.006]; PL interaction -0.174 [-0.325, -0.029] log-worth; joint 4-df role × slot Wald 66.9, p = 1.03e-13.
- **H1 (slot main effect): contradicted.** POS +0.038 [+0.017, +0.059]; PL slot (last − first) -0.031 [-0.090, +0.028].
- Two-hop traces with a CF margin below 0.02: 61.3%. PL converged: True; non-converged bootstrap refits: 0.

## dream main-n8: contrasts

| Hop | Contrast | Model-free (share before h) | Plackett–Luce (log-worth) |
|---:|---|---:|---:|
| 2 | role × slot (DiD / interaction) | -0.045 [-0.085, -0.006] | -0.174 [-0.325, -0.029] |
| 2 | slot main effect (last − first) | +0.038 [+0.017, +0.059] | -0.031 [-0.090, +0.028] |
| 2 | prerequisite: last − first | +0.060 [+0.036, +0.085] | |
| 2 | dependent: last − first | +0.015 [-0.018, +0.048] | |
| 2 | field b − field a | | -0.232 [-0.456, -0.012] |
| 1 | role × slot (DiD / interaction) | +0.021 [-0.025, +0.068] | +0.380 [+0.223, +0.553] |
| 1 | slot main effect (last − first) | +0.073 [+0.044, +0.102] | -0.066 [-0.150, +0.017] |
| 1 | prerequisite: last − first | +0.062 [+0.024, +0.101] | |
| 1 | dependent: last − first | +0.084 [+0.050, +0.119] | |
| 1 | field b − field a | | +0.292 [+0.073, +0.519] |

## dream main-n8: share committed before h, two-hop

| Role | Slot | n traces | Committed before h |
|---|---|---:|---:|
| prerequisite | first | 800 | 69.4 [64.6, 74.0] |
| prerequisite | middle | 800 | 76.2 [71.9, 80.5] |
| prerequisite | last | 800 | 75.4 [70.8, 79.8] |
| dependent | first | 800 | 47.8 [42.5, 53.0] |
| dependent | middle | 800 | 48.9 [44.2, 53.6] |
| dependent | last | 800 | 49.2 [44.2, 54.2] |

## dream main-n8: share committed before h, one-hop

| Role | Slot | n traces | Committed before h |
|---|---|---:|---:|
| prerequisite | first | 800 | 47.1 [42.2, 52.2] |
| prerequisite | middle | 800 | 60.1 [55.5, 64.8] |
| prerequisite | last | 800 | 53.4 [48.6, 58.1] |
| dependent | first | 800 | 42.8 [38.0, 47.6] |
| dependent | middle | 800 | 53.5 [49.2, 57.8] |
| dependent | last | 800 | 51.1 [46.4, 55.8] |

## dream main-n8: sensitivity

| Subset | Two-hop traces | DiD | POS |
|---|---:|---:|---:|
| excluding flip-sensitive traces | 930 | -0.052 [-0.123, +0.019] | +0.065 [+0.032, +0.101] |
| fully correct traces only | 2256 | -0.050 [-0.094, -0.007] | +0.038 [+0.015, +0.060] |

## dream main-n8: mean-rank mixed model, two-hop

Mean normalized rank (0 = committed first). Caveat (PREREG): ranks in a trace still sum to a constant, so a nonzero interaction here reflects dependence on where the other fields sit; the DiD and PL rows are the interpretable ones.

| Term | Coef [95% CI] |
|---|---:|
| Intercept | +0.678 [+0.653, +0.703] |
| C(role, Treatment('independent'))[T.dependent] | -0.052 [-0.089, -0.015] |
| C(role, Treatment('independent'))[T.prerequisite] | -0.455 [-0.492, -0.418] |
| C(slot, Treatment('first'))[T.last] | -0.097 [-0.133, -0.062] |
| C(slot, Treatment('first'))[T.middle] | -0.102 [-0.138, -0.067] |
| C(role, Treatment('independent'))[T.dependent]:C(slot, Treatment('first'))[T.last] | +0.087 [+0.037, +0.137] |
| C(role, Treatment('independent'))[T.prerequisite]:C(slot, Treatment('first'))[T.last] | +0.070 [+0.020, +0.120] |
| C(role, Treatment('independent'))[T.dependent]:C(slot, Treatment('first'))[T.middle] | +0.073 [+0.023, +0.123] |
| C(role, Treatment('independent'))[T.prerequisite]:C(slot, Treatment('first'))[T.middle] | +0.066 [+0.016, +0.116] |
| is_b | +0.074 [+0.054, +0.095] |

## dream main-n8: alignment

Prerequisite committed before dependent: two-hop 78.6 [75.8, 81.4], one-hop (nominal roles) 55.0 [52.8, 57.2], difference 23.6 [20.2, 27.1] points.

## dream main-n8: accuracy

| Hop | a correct | b correct | h correct | All three correct |
|---:|---:|---:|---:|---:|
| 2 | 98.0 [96.0, 99.5] | 98.2 [96.3, 99.7] | 97.7 [96.1, 99.0] | 94.0 [91.0, 96.7] |
| 1 | 97.0 [94.8, 98.9] | 97.6 [95.5, 99.3] | 99.0 [97.8, 99.8] | 94.0 [91.0, 96.7] |

## llada main-n128: summary

Table size 128; CF traces 2400; hosts/GPUs/commits [('rosetta15.csail.mit.edu', 'NVIDIA A100-PCIE-40GB', 'bfcc85ed03dc0c27a2999dd1f64dfd667d52883e')].

- **H1b (role × slot): inconclusive.** DiD +0.175 [+0.105, +0.245]; PL interaction +0.295 [-0.136, +0.681] log-worth; joint 4-df role × slot Wald 63.3, p = 5.76e-13.
- **H1 (slot main effect): supported.** POS -0.185 [-0.215, -0.155]; PL slot (last − first) -1.008 [-1.277, -0.791].
- Two-hop traces with a CF margin below 0.02: 66.3%. PL converged: True; non-converged bootstrap refits: 0.

## llada main-n128: contrasts

| Hop | Contrast | Model-free (share before h) | Plackett–Luce (log-worth) |
|---:|---|---:|---:|
| 2 | role × slot (DiD / interaction) | +0.175 [+0.105, +0.245] | +0.295 [-0.136, +0.681] |
| 2 | slot main effect (last − first) | -0.185 [-0.215, -0.155] | -1.008 [-1.277, -0.791] |
| 2 | prerequisite: last − first | -0.273 [-0.323, -0.222] | |
| 2 | dependent: last − first | -0.097 [-0.138, -0.058] | |
| 2 | field b − field a | | -0.224 [-0.439, -0.025] |
| 1 | role × slot (DiD / interaction) | +0.195 [+0.145, +0.250] | +1.091 [+0.868, +1.346] |
| 1 | slot main effect (last − first) | +0.070 [+0.041, +0.099] | +0.002 [-0.077, +0.083] |
| 1 | prerequisite: last − first | -0.028 [-0.060, +0.005] | |
| 1 | dependent: last − first | +0.167 [+0.125, +0.213] | |
| 1 | field b − field a | | +0.255 [-0.032, +0.558] |

## llada main-n128: share committed before h, two-hop

| Role | Slot | n traces | Committed before h |
|---|---|---:|---:|
| prerequisite | first | 400 | 69.2 [63.5, 74.8] |
| prerequisite | middle | 400 | 51.2 [44.2, 58.2] |
| prerequisite | last | 400 | 42.0 [35.8, 48.2] |
| dependent | first | 400 | 18.0 [13.2, 23.2] |
| dependent | middle | 400 | 14.2 [10.2, 18.5] |
| dependent | last | 400 | 8.2 [5.0, 12.0] |

## llada main-n128: share committed before h, one-hop

| Role | Slot | n traces | Committed before h |
|---|---|---:|---:|
| prerequisite | first | 400 | 45.0 [37.5, 52.8] |
| prerequisite | middle | 400 | 49.8 [42.2, 57.5] |
| prerequisite | last | 400 | 42.2 [35.0, 49.8] |
| dependent | first | 400 | 32.8 [25.5, 40.0] |
| dependent | middle | 400 | 37.2 [30.5, 44.2] |
| dependent | last | 400 | 49.5 [42.5, 56.8] |

## llada main-n128: sensitivity

| Subset | Two-hop traces | DiD | POS |
|---|---:|---:|---:|
| excluding flip-sensitive traces | 404 | +0.428 [+0.305, +0.558] | -0.309 [-0.366, -0.246] |
| fully correct traces only | 712 | +0.245 [+0.152, +0.339] | -0.114 [-0.157, -0.072] |

## llada main-n128: mean-rank mixed model, two-hop

Mean normalized rank (0 = committed first). Caveat (PREREG): ranks in a trace still sum to a constant, so a nonzero interaction here reflects dependence on where the other fields sit; the DiD and PL rows are the interpretable ones.

| Term | Coef [95% CI] |
|---|---:|
| Intercept | +0.320 [+0.291, +0.349] |
| C(role, Treatment('independent'))[T.dependent] | +0.492 [+0.449, +0.534] |
| C(role, Treatment('independent'))[T.prerequisite] | -0.172 [-0.215, -0.130] |
| C(slot, Treatment('first'))[T.last] | +0.055 [+0.014, +0.096] |
| C(slot, Treatment('first'))[T.middle] | +0.000 [-0.041, +0.041] |
| C(role, Treatment('independent'))[T.dependent]:C(slot, Treatment('first'))[T.last] | +0.041 [-0.016, +0.099] |
| C(role, Treatment('independent'))[T.prerequisite]:C(slot, Treatment('first'))[T.last] | +0.141 [+0.084, +0.199] |
| C(role, Treatment('independent'))[T.dependent]:C(slot, Treatment('first'))[T.middle] | +0.061 [+0.004, +0.119] |
| C(role, Treatment('independent'))[T.prerequisite]:C(slot, Treatment('first'))[T.middle] | +0.097 [+0.040, +0.155] |
| is_b | +0.052 [+0.028, +0.075] |

## llada main-n128: alignment

Prerequisite committed before dependent: two-hop 91.5 [88.8, 93.8], one-hop (nominal roles) 54.6 [52.0, 57.2], difference 36.9 [33.2, 40.3] points.

## llada main-n128: accuracy

| Hop | a correct | b correct | h correct | All three correct |
|---:|---:|---:|---:|---:|
| 2 | 74.9 [71.9, 77.8] | 81.9 [78.4, 85.3] | 97.1 [95.6, 98.3] | 59.3 [54.5, 64.2] |
| 1 | 100.0 [100.0, 100.0] | 100.0 [100.0, 100.0] | 100.0 [100.0, 100.0] | 100.0 [100.0, 100.0] |

## Interpretation limits

- One commit per forward pass, CF only; three single-token fields; V2 row format (not validated by the Phase 1.5 gate).
- Between-model and between-size comparisons are descriptive.
- Hardware is one GPU type for the whole stage (see Deviations); rows are not comparable across GPU types, effects are.

## Deviations

# Three-field RQ1 study: decisions and deviations

- 2026-11-18: Design approved by the team, with LLaDA at 128 rows added, the independent field `h` kept, and the ±0.10 margin kept. PREREG frozen before any model output.
- 2026-11-18: Hardware: rosetta15 A100-PCIE-40GB for the whole stage, chosen before any output. rosetta21 was down (ssh timeout during the handshake since about 08:45 EST). All eight rosetta7 A6000s were in use by other users (97–100% utilization, 33–48 GB of 49 GB used). The team's instruction was: rosetta7 A6000s if free, otherwise the whole stage on rosetta15, logged here.
- 2026-11-18: Dev validity check passed for every arm (`results/rq1_3f/dev_check.json`, rosetta15 A100). One-hop all-three-correct and two-hop `h` correct: LLaDA at 8 rows, 100% and 100%; Dream at 8 rows, 99.6% and 99.6%; LLaDA at 128 rows, 100% and 98.3%. All three main arms run as preregistered.
- 2026-11-18 (after the main run): Main runs complete on rosetta15 A100 (`main-n8`: 4,800 CF traces per model; `main-n128`: 2,400 for LLaDA; commit `bfcc85e`). Analysis: `results/rq1_3f/report.md`. Preregistered verdicts:

  | Arm | H1b (role × slot) | H1 (slot) |
  |---|---|---|
  | LLaDA, 8 rows | inconclusive | contradicted |
  | Dream, 8 rows | supported | contradicted |
  | LLaDA, 128 rows | inconclusive | supported |

- 2026-11-18 (after the main run): **Error in the PREREG's H1 measure.** The PREREG says `h`'s position "cancels in the contrasts below". That is true for the DiD but not for POS.
  - **Why:** when a role field moves from the first slot to the last, `h` shifts from {middle, last} to {first, middle}. Under a pairwise (PL) model, POS = [θ_R(last) − θ_R(first)] + ½ [θ_h(last) − θ_h(first)], so it mixes in the reference field's own slot effect.
  - **Evidence:** for LLaDA at 8 rows, POS is +0.064 [+0.046, +0.082] while the PL slot effect is −0.130 [−0.196, −0.067]: opposite signs.
  - **Impact:** the H1 verdicts follow the preregistered rule, but the PL slot effect is the interpretable slot measure. By that measure:
    - LLaDA at 8 rows: −0.13 log-worth, a small left-to-right tendency (later slots committed later);
    - Dream at 8 rows: −0.03 [−0.09, +0.03], none;
    - LLaDA at 128 rows: −1.01 [−1.28, −0.79], a strong left-to-right tendency.
  - The DiD (H1b) is not affected.
- 2026-11-18 (after the main run): **The one-hop control is not null.** The PREREG expected the one-hop role × slot interaction to be near 0, because the roles there are nominal. It is not:
  - LLaDA: DiD +0.189 [+0.148, +0.231] at 8 rows and +0.195 [+0.145, +0.250] at 128 rows; PL +0.71 and +1.09.
  - Dream: PL +0.380 [+0.223, +0.553]; DiD +0.021 [−0.025, +0.068].
  - **Likely reason:** the "prerequisite" field always sits in the anchor row's second column, before `h`, and the "dependent" field (one-hop) after `h`. So the role labels also encode where the value sits in the input.
  - **Impact:** a two-hop role × slot interaction cannot be attributed to the dependency itself. For LLaDA, the two-hop DiD (+0.063 at 8 rows, +0.175 at 128 rows) is no larger than the one-hop control. Dream's two-hop interaction (−0.045, PL −0.17) has the opposite sign to its one-hop PL interaction.
  - **Interpretation:** there is no evidence that dependency role changes how output position affects commit order, beyond what input layout alone produces.
- 2026-11-18: All LLaDA two-hop traces at 8 rows (100%) have a CF margin below 0.02, so the "excluding flip-sensitive traces" sensitivity check has no data for that arm. The rate is 61% for Dream at 8 rows and 66% for LLaDA at 128 rows.
