# Phase 1 report



# Phase 1 pilot: llada

## Run summary

- Environment: 8 NVIDIA RTX A6000 GPUs (49140 MiB each); used GPU 0; PyTorch 2.5.1+cu121, CUDA 12.1, Transformers 4.46.3.
- Revision: `08b83a6feb34df1a6011b80c3c00c7563e963b07`; code commit in each trace row.
- Rows: Exp 1 60/60, Exp 2 5400/5400, Exp 3 4800/4800.
- G0: pass; G1: pass.

- G0 speed: {'4': 0.06622767448425293, '8': 0.08051252365112305, '16': 0.12382936477661133} s per two-pass run; projected 0.21 h at 200 sources; peak allocated VRAM 16.22 GB.

- Actual measured run time: 0.22 GPU-hours across Exp 1–3; peak allocated VRAM 16.16 GB.

## Exp 1 and G1

| Order | A accuracy | B accuracy |
|---|---:|---:|
| A-first | 100.0% [100.0, 100.0] | 100.0% [100.0, 100.0] |
| B-first | 100.0% [100.0, 100.0] | 100.0% [100.0, 100.0] |
| CF | 100.0% [100.0, 100.0] | 100.0% [100.0, 100.0] |

## Exp 2 accuracy

| Size | Condition | Order | A | B | Both |
|---:|---|---|---:|---:|---:|
| 4 | Direct | A-first | 84.0% [79.0, 89.0] | 23.0% [17.5, 29.0] | 13.5% [9.0, 18.5] |
| 4 | Direct | B-first | 64.0% [57.5, 70.5] | 58.5% [52.0, 65.5] | 26.5% [20.5, 32.5] |
| 4 | Direct | CF | 77.0% [71.0, 82.5] | 32.5% [26.0, 39.0] | 10.5% [6.5, 15.0] |
| 4 | Shared-path | A-first | 84.0% [79.0, 89.0] | 74.5% [68.5, 80.5] | 72.0% [65.5, 78.0] |
| 4 | Shared-path | B-first | 70.5% [64.0, 76.5] | 47.0% [40.5, 54.0] | 47.0% [40.5, 54.0] |
| 4 | Shared-path | CF | 80.5% [75.0, 85.5] | 66.5% [60.0, 73.0] | 66.5% [60.0, 73.0] |
| 4 | Separate-path | A-first | 68.5% [62.0, 75.0] | 45.0% [38.0, 52.0] | 23.0% [17.0, 29.0] |
| 4 | Separate-path | B-first | 31.5% [25.0, 38.0] | 33.5% [27.0, 40.0] | 2.0% [0.5, 4.0] |
| 4 | Separate-path | CF | 46.5% [39.5, 53.5] | 40.5% [34.0, 47.5] | 13.0% [8.5, 18.0] |
| 8 | Direct | A-first | 91.5% [87.5, 95.0] | 28.5% [22.5, 35.0] | 21.5% [16.0, 27.0] |
| 8 | Direct | B-first | 56.5% [49.5, 63.5] | 69.5% [63.0, 76.0] | 26.5% [20.5, 32.5] |
| 8 | Direct | CF | 78.0% [72.5, 83.5] | 36.5% [30.0, 43.0] | 15.5% [10.5, 20.5] |
| 8 | Shared-path | A-first | 93.5% [90.0, 96.5] | 75.5% [69.5, 81.5] | 75.5% [69.5, 81.5] |
| 8 | Shared-path | B-first | 64.0% [57.5, 70.5] | 32.0% [25.5, 38.5] | 32.0% [25.5, 38.5] |
| 8 | Shared-path | CF | 83.0% [77.5, 88.0] | 63.5% [56.5, 70.5] | 63.5% [56.5, 70.5] |
| 8 | Separate-path | A-first | 64.0% [57.5, 70.5] | 18.5% [13.5, 24.0] | 1.5% [0.0, 3.5] |
| 8 | Separate-path | B-first | 22.5% [17.0, 28.5] | 18.0% [13.0, 23.5] | 0.0% [0.0, 0.0] |
| 8 | Separate-path | CF | 47.0% [40.0, 54.0] | 15.0% [10.5, 20.0] | 1.0% [0.0, 2.5] |
| 16 | Direct | A-first | 90.5% [86.5, 94.5] | 24.0% [18.0, 30.0] | 15.5% [10.5, 20.5] |
| 16 | Direct | B-first | 59.0% [52.0, 66.0] | 59.5% [52.5, 66.0] | 18.5% [13.0, 24.0] |
| 16 | Direct | CF | 87.5% [83.0, 92.0] | 25.0% [19.0, 31.0] | 12.5% [8.0, 17.0] |
| 16 | Shared-path | A-first | 92.0% [88.0, 95.5] | 49.5% [42.5, 56.0] | 49.5% [42.5, 56.0] |
| 16 | Shared-path | B-first | 53.5% [46.5, 60.5] | 11.5% [7.0, 16.0] | 11.5% [7.0, 16.0] |
| 16 | Shared-path | CF | 81.0% [75.5, 86.0] | 42.0% [35.0, 48.5] | 42.0% [35.0, 48.5] |
| 16 | Separate-path | A-first | 57.5% [50.5, 64.0] | 12.5% [8.0, 17.0] | 0.0% [0.0, 0.0] |
| 16 | Separate-path | B-first | 35.0% [28.5, 41.5] | 2.5% [0.5, 5.0] | 0.0% [0.0, 0.0] |
| 16 | Separate-path | CF | 45.0% [38.0, 52.0] | 8.0% [4.5, 12.0] | 0.0% [0.0, 0.0] |

## Exp 2 paired order outcomes

| Size | Condition | Both right | Both wrong | Only A-first right | Only B-first right | McNemar p | CF chose successful first field |
|---:|---|---:|---:|---:|---:|---:|---:|
| 4 | Direct | 13 | 133 | 14 | 40 | 0.0005354 | 8/54 |
| 4 | Shared-path | 81 | 43 | 63 | 13 | 5.045e-09 | 52/76 |
| 4 | Separate-path | 4 | 154 | 42 | 0 | 4.547e-13 | 22/42 |
| 8 | Direct | 24 | 128 | 19 | 29 | 0.1934 | 7/48 |
| 8 | Shared-path | 59 | 44 | 92 | 5 | 8.591e-22 | 68/97 |
| 8 | Separate-path | 0 | 197 | 3 | 0 | 0.25 | 2/3 |
| 16 | Direct | 15 | 147 | 16 | 22 | 0.4177 | 10/38 |
| 16 | Shared-path | 22 | 100 | 77 | 1 | 5.228e-22 | 62/78 |
| 16 | Separate-path | 0 | 200 | 0 | 0 | nan | 0/0 |

## Exp 2 order interactions

| Size | Shared A-first minus B-first B accuracy | Separate gap | Shared minus Separate |
|---:|---:|---:|---:|
| 4 | 27.5% [20.0, 35.0] | 11.5% [4.5, 18.5] | 16.0% [6.5, 25.5] |
| 8 | 43.5% [36.0, 51.0] | 0.5% [-6.0, 7.0] | 43.0% [33.5, 52.5] |
| 16 | 38.0% [31.0, 45.0] | 10.0% [5.5, 15.0] | 28.0% [19.5, 36.5] |

## Exp 3 prefilled A intervention

| Size | Condition | Gold minus Masked | Predicted minus Masked | Wrong minus Masked | Wrong B matches alternative |
|---:|---|---:|---:|---:|---:|
| 4 | Shared-path | 37.0% [30.0, 44.0] | 27.5% [20.0, 35.0] | -46.0% [-53.0, -39.5] | 96.0% [93.0, 98.5] |
| 4 | Separate-path | -1.5% [-7.0, 4.0] | 11.5% [4.5, 18.5] | -29.5% [-36.0, -23.0] | 27.5% [21.5, 34.0] |
| 8 | Shared-path | 46.0% [39.0, 53.5] | 43.5% [36.0, 51.0] | -32.0% [-38.5, -25.5] | 93.5% [90.0, 96.5] |
| 8 | Separate-path | -16.5% [-22.0, -11.5] | 0.5% [-6.0, 7.0] | -17.5% [-23.0, -12.5] | 6.5% [3.5, 10.0] |
| 16 | Shared-path | 40.0% [33.0, 47.0] | 38.0% [31.0, 45.0] | -11.5% [-16.0, -7.0] | 92.5% [89.0, 96.0] |
| 16 | Separate-path | -2.5% [-5.0, -0.5] | 10.0% [5.5, 15.0] | -2.5% [-5.0, -0.5] | 3.5% [1.5, 6.0] |

### Shared-path minus Separate-path Exp 3 gaps

| Size | Gold gap interaction | Predicted gap interaction | Wrong gap interaction | Wrong alternative match difference |
|---:|---:|---:|---:|---:|
| 4 | 38.5% [30.5, 46.5] | 16.0% [6.5, 25.5] | -16.5% [-23.5, -9.5] | 68.5% [62.0, 75.0] |
| 8 | 62.5% [54.5, 70.5] | 43.0% [33.5, 52.5] | -14.5% [-21.0, -8.0] | 87.0% [82.0, 91.5] |
| 16 | 42.5% [35.5, 49.5] | 28.0% [19.5, 36.5] | -9.0% [-13.5, -5.0] | 89.0% [84.5, 93.0] |

## Step-0 confidence and CF choice

| Size | Condition | Mean A top-1 | Mean B top-1 | CF first A |
|---:|---|---:|---:|---:|
| 4 | Direct | 0.693 | 0.592 | 0.630 |
| 4 | Shared-path | 0.713 | 0.625 | 0.625 |
| 4 | Separate-path | 0.653 | 0.626 | 0.510 |
| 8 | Direct | 0.793 | 0.683 | 0.700 |
| 8 | Shared-path | 0.813 | 0.669 | 0.790 |
| 8 | Separate-path | 0.694 | 0.648 | 0.575 |
| 16 | Direct | 0.787 | 0.701 | 0.735 |
| 16 | Shared-path | 0.819 | 0.677 | 0.725 |
| 16 | Separate-path | 0.722 | 0.701 | 0.545 |

Step-0 top-1 confidence predicts CF first-field choice in 1800/1800 runs (ties use a seeded draw).

## G2

- Size 4: fail; Direct B by order {'A-first': 0.23, 'B-first': 0.585, 'CF': 0.325}; path B with intervals {'Shared-path': (0.6266666666666667, 0.5733333333333334, 0.6766666666666667), 'Separate-path': (0.39666666666666667, 0.3383333333333334, 0.455)}; discordant pairs {'Direct': 54, 'Shared-path': 76, 'Separate-path': 42}.
- Size 8: fail; Direct B by order {'A-first': 0.285, 'B-first': 0.695, 'CF': 0.365}; path B with intervals {'Shared-path': (0.57, 0.5183333333333333, 0.6216666666666667), 'Separate-path': (0.17166666666666663, 0.13166666666666665, 0.21499999999999997)}; discordant pairs {'Direct': 48, 'Shared-path': 97, 'Separate-path': 3}.
- Size 16: fail; Direct B by order {'A-first': 0.24, 'B-first': 0.595, 'CF': 0.25}; path B with intervals {'Shared-path': (0.34333333333333327, 0.2933333333333333, 0.395), 'Separate-path': (0.07666666666666666, 0.05, 0.10666666666666666)}; discordant pairs {'Direct': 38, 'Shared-path': 78, 'Separate-path': 0}.

## Interpretation limits

- A stays left of B throughout Phase 1, so CF preference cannot yet be separated from position. Exp 4 tests that.
- Gold beating Wrong does not show that the correct value helps; Masked is the relevant baseline.
- Exp 3 measures conditional response in a fixed context, not an equal-compute method comparison.
- Results are pilot evidence; these sources must stay out of any final test set.


## Exp 4 recommendation

Awaiting human review: lock no Exp 4 configuration from this pilot; no table size both passed G2 and showed a positive 95% lower bound for the Shared-path A-first B-accuracy gap.


# Phase 1 pilot: dream

## Run summary

- Environment: 8 NVIDIA RTX A6000 GPUs (49140 MiB each); used GPU 1; PyTorch 2.5.1+cu121, CUDA 12.1, Transformers 4.46.3.
- Revision: `05334cb9faaf763692dcf9d8737c642be2b2a6ae`; code commit in each trace row.
- Rows: Exp 1 60/60, Exp 2 5400/5400, Exp 3 4800/4800.
- G0: pass; G1: pass.

- G0 speed: {'4': 0.06685233116149902, '8': 0.09345674514770508, '16': 0.09447479248046875} s per two-pass run; projected 0.20 h at 200 sources; peak allocated VRAM 15.57 GB.

- Actual measured run time: 0.21 GPU-hours across Exp 1–3; peak allocated VRAM 15.50 GB.

## Exp 1 and G1

| Order | A accuracy | B accuracy |
|---|---:|---:|
| A-first | 95.0% [85.0, 100.0] | 95.0% [85.0, 100.0] |
| B-first | 100.0% [100.0, 100.0] | 95.0% [85.0, 100.0] |
| CF | 100.0% [100.0, 100.0] | 95.0% [85.0, 100.0] |

## Exp 2 accuracy

| Size | Condition | Order | A | B | Both |
|---:|---|---|---:|---:|---:|
| 4 | Direct | A-first | 92.5% [88.5, 96.0] | 33.0% [26.5, 39.5] | 31.5% [25.0, 38.0] |
| 4 | Direct | B-first | 74.5% [68.5, 80.5] | 59.0% [52.0, 65.5] | 40.0% [33.5, 46.5] |
| 4 | Direct | CF | 87.5% [83.0, 92.0] | 37.5% [31.0, 44.5] | 28.5% [22.0, 35.0] |
| 4 | Shared-path | A-first | 97.0% [94.5, 99.0] | 73.0% [66.5, 79.0] | 73.0% [66.5, 79.0] |
| 4 | Shared-path | B-first | 82.0% [76.5, 87.0] | 42.0% [35.0, 49.0] | 42.0% [35.0, 49.0] |
| 4 | Shared-path | CF | 94.0% [90.5, 97.0] | 68.0% [61.5, 74.0] | 68.0% [61.5, 74.0] |
| 4 | Separate-path | A-first | 92.0% [88.0, 95.5] | 42.5% [35.5, 49.5] | 37.0% [30.5, 44.0] |
| 4 | Separate-path | B-first | 48.5% [41.5, 55.5] | 38.5% [32.0, 45.5] | 7.0% [3.5, 11.0] |
| 4 | Separate-path | CF | 80.5% [75.0, 86.0] | 42.5% [35.5, 49.5] | 30.0% [24.0, 36.5] |
| 8 | Direct | A-first | 93.5% [90.0, 96.5] | 36.5% [30.0, 43.5] | 34.0% [27.5, 40.5] |
| 8 | Direct | B-first | 56.0% [49.0, 62.5] | 63.0% [56.5, 69.5] | 34.0% [27.5, 40.5] |
| 8 | Direct | CF | 86.0% [81.0, 90.5] | 42.0% [35.0, 49.0] | 31.5% [25.0, 38.0] |
| 8 | Shared-path | A-first | 98.0% [96.0, 99.5] | 78.0% [72.0, 83.5] | 78.0% [72.0, 83.5] |
| 8 | Shared-path | B-first | 82.5% [77.0, 87.5] | 43.5% [37.0, 50.5] | 42.0% [35.5, 49.0] |
| 8 | Shared-path | CF | 96.5% [94.0, 99.0] | 77.5% [71.5, 83.0] | 76.5% [70.5, 82.5] |
| 8 | Separate-path | A-first | 86.0% [81.0, 90.5] | 43.5% [36.5, 50.5] | 31.5% [25.5, 38.0] |
| 8 | Separate-path | B-first | 30.0% [23.5, 36.5] | 29.0% [23.0, 35.5] | 1.0% [0.0, 2.5] |
| 8 | Separate-path | CF | 75.5% [69.5, 81.5] | 41.0% [34.5, 48.0] | 26.5% [20.5, 32.5] |
| 16 | Direct | A-first | 94.5% [91.0, 97.5] | 39.5% [33.0, 46.5] | 38.5% [32.0, 45.5] |
| 16 | Direct | B-first | 54.0% [47.5, 61.0] | 79.5% [73.5, 85.0] | 38.0% [31.5, 45.0] |
| 16 | Direct | CF | 82.0% [76.5, 87.0] | 47.5% [40.5, 54.5] | 32.0% [25.5, 38.5] |
| 16 | Shared-path | A-first | 95.5% [92.5, 98.0] | 71.0% [64.5, 77.0] | 70.0% [63.5, 76.0] |
| 16 | Shared-path | B-first | 73.0% [67.0, 79.0] | 32.5% [26.0, 39.0] | 31.5% [25.0, 38.0] |
| 16 | Shared-path | CF | 88.5% [84.0, 93.0] | 66.5% [60.0, 73.0] | 65.5% [59.0, 72.0] |
| 16 | Separate-path | A-first | 76.5% [70.5, 82.5] | 33.0% [26.5, 39.5] | 13.0% [8.5, 17.5] |
| 16 | Separate-path | B-first | 25.0% [19.0, 31.0] | 23.0% [17.5, 29.0] | 1.5% [0.0, 3.5] |
| 16 | Separate-path | CF | 63.0% [56.0, 69.5] | 30.0% [24.0, 36.5] | 10.0% [6.0, 14.0] |

## Exp 2 paired order outcomes

| Size | Condition | Both right | Both wrong | Only A-first right | Only B-first right | McNemar p | CF chose successful first field |
|---:|---|---:|---:|---:|---:|---:|---:|
| 4 | Direct | 42 | 99 | 21 | 38 | 0.03634 | 15/59 |
| 4 | Shared-path | 79 | 49 | 67 | 5 | 6.388e-15 | 57/72 |
| 4 | Separate-path | 11 | 123 | 63 | 3 | 1.3e-15 | 49/66 |
| 8 | Direct | 38 | 102 | 30 | 30 | 1 | 25/60 |
| 8 | Shared-path | 83 | 43 | 73 | 1 | 7.941e-21 | 70/74 |
| 8 | Separate-path | 1 | 136 | 62 | 1 | 1.388e-17 | 52/63 |
| 16 | Direct | 39 | 86 | 38 | 37 | 1 | 25/75 |
| 16 | Shared-path | 60 | 57 | 80 | 3 | 1.972e-20 | 71/83 |
| 16 | Separate-path | 2 | 173 | 24 | 1 | 1.55e-06 | 18/25 |

## Exp 2 order interactions

| Size | Shared A-first minus B-first B accuracy | Separate gap | Shared minus Separate |
|---:|---:|---:|---:|
| 4 | 31.0% [24.0, 38.0] | 4.0% [-2.5, 11.0] | 27.0% [17.5, 36.5] |
| 8 | 34.5% [27.5, 41.5] | 14.5% [7.0, 22.0] | 20.0% [10.0, 30.0] |
| 16 | 38.5% [31.5, 46.0] | 10.0% [3.0, 17.0] | 28.5% [19.5, 37.5] |

## Exp 3 prefilled A intervention

| Size | Condition | Gold minus Masked | Predicted minus Masked | Wrong minus Masked | Wrong B matches alternative |
|---:|---|---:|---:|---:|---:|
| 4 | Shared-path | 32.5% [25.5, 39.5] | 31.0% [24.0, 38.0] | -41.0% [-48.0, -34.0] | 82.0% [76.5, 87.0] |
| 4 | Separate-path | 0.5% [-6.0, 7.0] | 4.0% [-2.5, 11.0] | -29.0% [-36.0, -22.0] | 17.0% [12.0, 22.5] |
| 8 | Shared-path | 36.0% [29.5, 42.5] | 34.5% [27.5, 41.5] | -42.5% [-49.5, -35.5] | 90.0% [86.0, 94.0] |
| 8 | Separate-path | 5.0% [-2.0, 12.0] | 14.5% [7.0, 22.0] | -19.5% [-25.5, -13.5] | 26.0% [20.0, 32.5] |
| 16 | Shared-path | 40.5% [33.5, 47.5] | 38.5% [31.5, 46.0] | -32.0% [-38.5, -25.5] | 89.0% [84.5, 93.0] |
| 16 | Separate-path | -3.0% [-9.0, 3.0] | 10.0% [3.0, 17.0] | -18.5% [-24.5, -13.0] | 28.0% [22.0, 34.5] |

### Shared-path minus Separate-path Exp 3 gaps

| Size | Gold gap interaction | Predicted gap interaction | Wrong gap interaction | Wrong alternative match difference |
|---:|---:|---:|---:|---:|
| 4 | 32.0% [22.5, 41.0] | 27.0% [17.5, 36.5] | -12.0% [-21.0, -3.0] | 65.0% [58.5, 71.5] |
| 8 | 31.0% [22.0, 40.0] | 20.0% [10.0, 30.0] | -23.0% [-31.0, -15.0] | 64.0% [57.0, 70.5] |
| 16 | 43.5% [35.0, 52.0] | 28.5% [19.5, 37.5] | -13.5% [-20.0, -6.5] | 61.0% [54.0, 67.5] |

## Step-0 confidence and CF choice

| Size | Condition | Mean A top-1 | Mean B top-1 | CF first A |
|---:|---|---:|---:|---:|
| 4 | Direct | 0.544 | 0.342 | 0.730 |
| 4 | Shared-path | 0.684 | 0.413 | 0.785 |
| 4 | Separate-path | 0.598 | 0.365 | 0.760 |
| 8 | Direct | 0.694 | 0.403 | 0.830 |
| 8 | Shared-path | 0.790 | 0.383 | 0.915 |
| 8 | Separate-path | 0.645 | 0.391 | 0.800 |
| 16 | Direct | 0.711 | 0.496 | 0.765 |
| 16 | Shared-path | 0.767 | 0.461 | 0.810 |
| 16 | Separate-path | 0.654 | 0.423 | 0.735 |

Step-0 top-1 confidence predicts CF first-field choice in 1800/1800 runs (ties use a seeded draw).

## G2

- Size 4: fail; Direct B by order {'A-first': 0.33, 'B-first': 0.59, 'CF': 0.375}; path B with intervals {'Shared-path': (0.6099999999999999, 0.5533333333333333, 0.665), 'Separate-path': (0.4116666666666666, 0.3516666666666666, 0.4733333333333333)}; discordant pairs {'Direct': 59, 'Shared-path': 72, 'Separate-path': 66}.
- Size 8: fail; Direct B by order {'A-first': 0.365, 'B-first': 0.63, 'CF': 0.42}; path B with intervals {'Shared-path': (0.6633333333333333, 0.6116666666666667, 0.7133333333333334), 'Separate-path': (0.3783333333333333, 0.3216666666666667, 0.435)}; discordant pairs {'Direct': 60, 'Shared-path': 74, 'Separate-path': 63}.
- Size 16: fail; Direct B by order {'A-first': 0.395, 'B-first': 0.795, 'CF': 0.475}; path B with intervals {'Shared-path': (0.5666666666666667, 0.5116666666666667, 0.62), 'Separate-path': (0.2866666666666666, 0.235, 0.3383333333333334)}; discordant pairs {'Direct': 75, 'Shared-path': 83, 'Separate-path': 25}.

## Interpretation limits

- A stays left of B throughout Phase 1, so CF preference cannot yet be separated from position. Exp 4 tests that.
- Gold beating Wrong does not show that the correct value helps; Masked is the relevant baseline.
- Exp 3 measures conditional response in a fixed context, not an equal-compute method comparison.
- Results are pilot evidence; these sources must stay out of any final test set.


## Exp 4 recommendation

Awaiting human review: lock no Exp 4 configuration from this pilot; no table size both passed G2 and showed a positive 95% lower bound for the Shared-path A-first B-accuracy gap.


## Deviations, failed checks, and fixes



# Decisions and deviations

- 2026-11-05: The handoff's `ML-GSAI/LLaDA-8B-Instruct` returned HTTP 401. The public model is `GSAI-ML/LLaDA-8B-Instruct` at revision `08b83a6feb34df1a6011b80c3c00c7563e963b07`. Use the corrected namespace. Dream is pinned at `05334cb9faaf763692dcf9d8737c642be2b2a6ae`.
- 2026-11-05: Eight idle NVIDIA RTX A6000 GPUs (48 GiB each); use GPUs 0 and 1 only. Disk has 9.3 TiB free, RAM 503 GiB total. No active scheduler allocation is apparent; `tmux` is available. System Python 3.13 lacks PyTorch; use a virtual environment based on the existing qwen3 Python environment with PyTorch 2.5.1 CUDA 12.1 and pin Transformers 4.46.3 to match model configs.
- 2026-11-05: Before Exp 1, moved the JSON output template from the user instruction to the assistant continuation. This gives one unambiguous answer location while keeping the same requested JSON format. Config and preregistration record this change.
- 2026-11-05: Direct uses inert mapping keys D, which never occur in its anchor; E is an inert value. Path anchors use C as a filler field. This keeps four anchor tokens and two mapping tokens per row across conditions while preserving one correct target B.
- 2026-11-05: Candidate values require one tokenizer token both bare (for output and mapping keys) and with a preceding space (for table values), then pass full-template output-slot alignment. This checks the two contexts used by the task.
- 2026-11-05: Added the exact Exp 1 copy instruction to the config before Exp 1, alongside the lookup and output templates.
- 2026-11-05: Initial G0 failed on both models because the batching check compared every bf16 logit at a tight tolerance; the top-1 predictions already agreed. The full vectors vary slightly with batch shape. Fix 1: compare the two actual decoding decisions (chosen field and committed token) in batched and single runs, with a regression test showing irrelevant logit drift. Rerun G0 before Exp 1.
- 2026-11-05: G0 fix 1 exposed a local variable collision in the LLaDA smoke test: a predicted token ID overwrote the tokenizer variable before the size-8 test. Fix 2: rename that local variable. The subsequent size-8 and size-16 smoke passes exercise the regression path.
- 2026-11-05: Dream's two-step batched decode produced a different second token from single-run bf16 decoding, despite identical input rows. This is a real G0 batching mismatch. Investigate the attention kernel before deciding Dream readiness; no experiment traces were produced.
- 2026-11-05: Dream G0 fix 2: force PyTorch's math scaled-dot-product attention kernel for both G0 and all Dream runs, to test whether batch-shape-sensitive fused-kernel arithmetic caused the second-token mismatch. Keep bf16 weights and full-vocabulary decoding. Rerun G0.
- 2026-11-05: Root cause in Dream's own generation_utils.py: it shifts the model's next-token logits right by one before evaluating masks. The shared decoder had used logits at the same position, which caused nonsensical Dream predictions and a G0 batching mismatch. Fix 3: apply this shift only for Dream in both normal decoding and batched G0, with a regression test. Rerun G0; Dream still has no experiment traces.
- 2026-11-05: Before Exp 2, completed the G0 slot-alignment gate by adding model recovery of a known copied value with exactly one output field masked; the earlier check verified token positions only. Rerun G0 for both models. This is a check completion, not a gate threshold change.
- 2026-11-05: Final G0 passed for both models. Measured two-pass speed projected about 0.2 GPU-hours per model for the planned source count, with peak allocated VRAM below 17 GB. Keep 200 sources per table size; no source reduction.
- 2026-11-05: Exp 1 completed with 60 rows per model. G1 passed: LLaDA had 20/20 A and B under each order; Dream had at least 19/20 for every field/order. Freeze code and config before Exp 2; no prompt retuning was needed.
- 2026-11-05: Post-freeze report-only bug shown by code inspection: report generation omitted the Exp 4 recommendation and deviations/failed checks. Restore those sections and test them. No model trace was affected, so no trace invalidation or experimental rerun is required.
- 2026-11-05: Independent task audit over all 600 sources per model found zero token-length mismatches across Direct, Shared-path, and Separate-path. Exp 2 completed with 5,400 unique rows per model; proceed to Exp 3 without retuning, regardless of pending G2 analysis.
- 2026-11-05: Exp 3 completed with 4,800 unique rows per model. Supervisors made no restarts or hang recoveries. G2 failed at table sizes 4, 8, and 16 for both models: Direct B accuracy was below 90% under every order. Continue reporting the planned analyses without retuning.
- 2026-11-05: Exported the exact per-tokenizer usable word pools as local artifacts. A separate scorer reconstructed source targets from seeds and those pools and checked 20 random rows from each experiment for each model (120 rows total); every check passed. The export and scorer are validation-only additions and did not change experiment code or traces.

