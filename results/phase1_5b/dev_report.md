# Phase 1.5b dev report

## Run summary

- Split: dev; traces: dev; rows: 12600.
- Hosts / GPUs / commits: [('rosetta21.csail.mit.edu', 'NVIDIA RTX A6000', 'e7951397f6c46eddffcb0e602e32b3023b958f76')].
- Answers whose correctness changed under whitespace normalization: dream A: 15, dream B: 15, llada A: 0, llada B: 0.
- Each model is calibrated separately; comparisons between models are descriptive only.

## Selection

- llada: **none passed**
- dream: **none passed**

## Gate

| Model | Variant | Size | Direct A-first | Direct B-first | Direct CF | Shared (avg) | Separate (avg) | Pass |
|---|---|---:|---:|---:|---:|---:|---:|---|
| llada | V2 | 16 | 99.0 [97.0, 100.0] | 99.0 [97.0, 100.0] | 99.0 [97.0, 100.0] | ✗ 100.0 [100.0, 100.0] | 99.0 [97.0, 100.0] | no |
| llada | V2 | 32 | 100.0 [100.0, 100.0] | 100.0 [100.0, 100.0] | 100.0 [100.0, 100.0] | ✗ 100.0 [100.0, 100.0] | 97.3 [94.0, 100.0] | no |
| llada | V2 | 64 | 98.0 [95.0, 100.0] | 99.0 [97.0, 100.0] | 99.0 [97.0, 100.0] | ✗ 99.3 [98.3, 100.0] | 69.7 [61.7, 77.3] | no |
| llada | V2 | 128 | 96.0 [92.0, 99.0] | 100.0 [100.0, 100.0] | 97.0 [93.0, 100.0] | ✗ 88.3 [83.3, 92.7] | 19.7 [13.3, 26.3] | no |
| llada | V2d | 16 | 99.0 [97.0, 100.0] | 99.0 [97.0, 100.0] | 99.0 [97.0, 100.0] | ✗ 99.7 [99.0, 100.0] | ✗ 1.7 [0.0, 4.3] | no |
| llada | V2d | 32 | 100.0 [100.0, 100.0] | 100.0 [100.0, 100.0] | 100.0 [100.0, 100.0] | ✗ 98.7 [97.0, 100.0] | ✗ 1.7 [0.3, 3.3] | no |
| llada | V2d | 64 | 98.0 [95.0, 100.0] | 99.0 [97.0, 100.0] | 98.0 [95.0, 100.0] | ✗ 88.0 [82.3, 93.0] | ✗ 1.3 [0.0, 3.7] | no |
| dream | V2 | 16 | 96.0 [92.0, 99.0] | 94.0 [89.0, 98.0] | 96.0 [92.0, 99.0] | ✗ 91.0 [87.3, 94.3] | 69.3 [61.0, 77.0] | no |
| dream | V2 | 32 | ✗ 84.0 [77.0, 91.0] | ✗ 78.0 [70.0, 86.0] | ✗ 82.0 [74.0, 89.0] | 59.0 [52.0, 65.7] | 34.0 [26.0, 42.0] | no |
| dream | V2 | 64 | ✗ 77.0 [68.0, 85.0] | 91.0 [85.0, 96.0] | ✗ 80.0 [72.0, 87.0] | 42.7 [34.7, 50.7] | 20.7 [14.3, 27.7] | no |
| dream | V2 | 128 | ✗ 43.0 [33.0, 53.0] | ✗ 54.0 [44.0, 64.0] | ✗ 44.0 [34.0, 54.0] | ✗ 19.7 [13.7, 25.7] | 6.0 [2.3, 10.3] | no |
| dream | V2d | 16 | 94.0 [89.0, 98.0] | 90.0 [84.0, 95.0] | 95.0 [90.0, 99.0] | ✗ 83.7 [79.0, 88.0] | ✗ 4.7 [1.7, 8.7] | no |
| dream | V2d | 32 | ✗ 82.0 [74.0, 89.0] | ✗ 84.0 [77.0, 91.0] | ✗ 82.0 [74.0, 89.0] | 59.7 [53.7, 65.3] | ✗ 0.7 [0.0, 1.7] | no |
| dream | V2d | 64 | ✗ 72.0 [63.0, 81.0] | ✗ 79.0 [71.0, 87.0] | ✗ 74.0 [65.0, 82.0] | ✗ 32.7 [25.3, 40.7] | ✗ 1.3 [0.0, 3.7] | no |

## llada V2: accuracy

| Size | Condition | Order | A | B | Both |
|---:|---|---|---:|---:|---:|
| 16 | Direct | A-first | 100.0 [100.0, 100.0] | 99.0 [97.0, 100.0] | 99.0 [97.0, 100.0] |
| 16 | Direct | B-first | 100.0 [100.0, 100.0] | 99.0 [97.0, 100.0] | 99.0 [97.0, 100.0] |
| 16 | Direct | CF | 100.0 [100.0, 100.0] | 99.0 [97.0, 100.0] | 99.0 [97.0, 100.0] |
| 16 | Shared-path | A-first | 100.0 [100.0, 100.0] | 100.0 [100.0, 100.0] | 100.0 [100.0, 100.0] |
| 16 | Shared-path | B-first | 100.0 [100.0, 100.0] | 100.0 [100.0, 100.0] | 100.0 [100.0, 100.0] |
| 16 | Shared-path | CF | 100.0 [100.0, 100.0] | 100.0 [100.0, 100.0] | 100.0 [100.0, 100.0] |
| 16 | Separate-path | A-first | 100.0 [100.0, 100.0] | 99.0 [97.0, 100.0] | 99.0 [97.0, 100.0] |
| 16 | Separate-path | B-first | 100.0 [100.0, 100.0] | 99.0 [97.0, 100.0] | 99.0 [97.0, 100.0] |
| 16 | Separate-path | CF | 100.0 [100.0, 100.0] | 99.0 [97.0, 100.0] | 99.0 [97.0, 100.0] |
| 32 | Direct | A-first | 99.0 [97.0, 100.0] | 100.0 [100.0, 100.0] | 99.0 [97.0, 100.0] |
| 32 | Direct | B-first | 98.0 [95.0, 100.0] | 100.0 [100.0, 100.0] | 98.0 [95.0, 100.0] |
| 32 | Direct | CF | 98.0 [95.0, 100.0] | 100.0 [100.0, 100.0] | 98.0 [95.0, 100.0] |
| 32 | Shared-path | A-first | 100.0 [100.0, 100.0] | 100.0 [100.0, 100.0] | 100.0 [100.0, 100.0] |
| 32 | Shared-path | B-first | 100.0 [100.0, 100.0] | 100.0 [100.0, 100.0] | 100.0 [100.0, 100.0] |
| 32 | Shared-path | CF | 100.0 [100.0, 100.0] | 100.0 [100.0, 100.0] | 100.0 [100.0, 100.0] |
| 32 | Separate-path | A-first | 99.0 [97.0, 100.0] | 98.0 [95.0, 100.0] | 97.0 [93.0, 100.0] |
| 32 | Separate-path | B-first | 89.0 [83.0, 95.0] | 97.0 [93.0, 100.0] | 86.0 [79.0, 92.0] |
| 32 | Separate-path | CF | 92.0 [86.0, 97.0] | 97.0 [93.0, 100.0] | 89.0 [83.0, 95.0] |
| 64 | Direct | A-first | 99.0 [97.0, 100.0] | 98.0 [95.0, 100.0] | 97.0 [93.0, 100.0] |
| 64 | Direct | B-first | 92.0 [86.0, 97.0] | 99.0 [97.0, 100.0] | 91.0 [85.0, 96.0] |
| 64 | Direct | CF | 93.0 [88.0, 97.0] | 99.0 [97.0, 100.0] | 92.0 [86.0, 97.0] |
| 64 | Shared-path | A-first | 100.0 [100.0, 100.0] | 100.0 [100.0, 100.0] | 100.0 [100.0, 100.0] |
| 64 | Shared-path | B-first | 100.0 [100.0, 100.0] | 98.0 [95.0, 100.0] | 98.0 [95.0, 100.0] |
| 64 | Shared-path | CF | 100.0 [100.0, 100.0] | 100.0 [100.0, 100.0] | 100.0 [100.0, 100.0] |
| 64 | Separate-path | A-first | 96.0 [92.0, 99.0] | 73.0 [64.0, 81.0] | 69.0 [60.0, 78.0] |
| 64 | Separate-path | B-first | 82.0 [74.0, 89.0] | 65.0 [55.0, 74.0] | 47.0 [37.0, 57.0] |
| 64 | Separate-path | CF | 93.0 [88.0, 98.0] | 71.0 [62.0, 80.0] | 64.0 [54.0, 73.0] |
| 128 | Direct | A-first | 95.0 [90.0, 99.0] | 96.0 [92.0, 99.0] | 91.0 [85.0, 96.0] |
| 128 | Direct | B-first | 90.0 [84.0, 95.0] | 100.0 [100.0, 100.0] | 90.0 [84.0, 95.0] |
| 128 | Direct | CF | 91.0 [85.0, 96.0] | 97.0 [93.0, 100.0] | 88.0 [81.0, 94.0] |
| 128 | Shared-path | A-first | 100.0 [100.0, 100.0] | 95.0 [90.0, 99.0] | 95.0 [90.0, 99.0] |
| 128 | Shared-path | B-first | 100.0 [100.0, 100.0] | 75.0 [66.0, 83.0] | 75.0 [66.0, 83.0] |
| 128 | Shared-path | CF | 100.0 [100.0, 100.0] | 95.0 [90.0, 99.0] | 95.0 [90.0, 99.0] |
| 128 | Separate-path | A-first | 99.0 [97.0, 100.0] | 23.0 [15.0, 31.0] | 22.0 [14.0, 30.0] |
| 128 | Separate-path | B-first | 94.0 [89.0, 98.0] | 13.0 [7.0, 20.0] | 9.0 [4.0, 15.0] |
| 128 | Separate-path | CF | 99.0 [97.0, 100.0] | 23.0 [15.0, 31.0] | 22.0 [14.0, 30.0] |

## llada V2: B error taxonomy (all sizes)

| Condition | Order | n | correct | target_row_H | target_row_other | distractor_row_same_field | other_table_value | non_table |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| Direct | A-first | 400 | 393 | 6 | 0 | 0 | 0 | 1 |
| Direct | B-first | 400 | 398 | 1 | 0 | 0 | 0 | 1 |
| Direct | CF | 400 | 395 | 4 | 0 | 0 | 0 | 1 |
| Shared-path | A-first | 400 | 395 | 5 | 0 | 0 | 0 | 0 |
| Shared-path | B-first | 400 | 373 | 27 | 0 | 0 | 0 | 0 |
| Shared-path | CF | 400 | 395 | 5 | 0 | 0 | 0 | 0 |
| Separate-path | A-first | 400 | 293 | 102 | 4 | 0 | 0 | 1 |
| Separate-path | B-first | 400 | 274 | 117 | 8 | 0 | 0 | 1 |
| Separate-path | CF | 400 | 290 | 105 | 4 | 0 | 0 | 1 |

## llada V2: paired A-first vs B-first (B correct)

| Size | Condition | Both right | Both wrong | Only A-first right | Only B-first right | McNemar p | A-first − B-first B accuracy |
|---:|---|---:|---:|---:|---:|---:|---:|
| 16 | Direct | 99 | 1 | 0 | 0 | nan | 0.0 [0.0, 0.0] |
| 16 | Shared-path | 100 | 0 | 0 | 0 | nan | 0.0 [0.0, 0.0] |
| 16 | Separate-path | 99 | 1 | 0 | 0 | nan | 0.0 [0.0, 0.0] |
| 32 | Direct | 100 | 0 | 0 | 0 | nan | 0.0 [0.0, 0.0] |
| 32 | Shared-path | 100 | 0 | 0 | 0 | nan | 0.0 [0.0, 0.0] |
| 32 | Separate-path | 97 | 2 | 1 | 0 | 1 | 1.0 [0.0, 3.0] |
| 64 | Direct | 98 | 1 | 0 | 1 | 1 | -1.0 [-3.0, 0.0] |
| 64 | Shared-path | 98 | 0 | 2 | 0 | 0.5 | 2.0 [0.0, 5.0] |
| 64 | Separate-path | 59 | 21 | 14 | 6 | 0.115 | 8.0 [-1.0, 17.0] |
| 128 | Direct | 96 | 0 | 0 | 4 | 0.125 | -4.0 [-8.0, -1.0] |
| 128 | Shared-path | 74 | 4 | 21 | 1 | 1.1e-05 | 20.0 [12.0, 28.0] |
| 128 | Separate-path | 8 | 72 | 15 | 5 | 0.0414 | 10.0 [2.0, 19.0] |

## llada V2: order × path interaction

| Size | Shared A-first − B-first | Separate A-first − B-first | Shared − Separate |
|---:|---:|---:|---:|
| 16 | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] |
| 32 | 0.0 [0.0, 0.0] | 1.0 [0.0, 3.0] | -1.0 [-3.0, 0.0] |
| 64 | 2.0 [0.0, 5.0] | 8.0 [-1.0, 17.0] | -6.0 [-15.0, 3.0] |
| 128 | 20.0 [12.0, 28.0] | 10.0 [2.0, 19.0] | 10.0 [-2.0, 22.0] |

## llada V2: step-0 confidence and CF

| Size | Condition | Mean A top-1 | Mean B top-1 | CF commits A first | CF min margin < 0.02 |
|---:|---|---:|---:|---:|---:|
| 16 | Direct | 0.995 | 0.994 | 0.500 | 0.940 |
| 16 | Shared-path | 0.999 | 0.993 | 0.810 | 0.960 |
| 16 | Separate-path | 0.993 | 0.982 | 0.750 | 0.790 |
| 32 | Direct | 0.980 | 0.987 | 0.490 | 0.790 |
| 32 | Shared-path | 0.998 | 0.988 | 0.860 | 0.920 |
| 32 | Separate-path | 0.955 | 0.932 | 0.640 | 0.460 |
| 64 | Direct | 0.952 | 0.940 | 0.490 | 0.410 |
| 64 | Shared-path | 0.996 | 0.930 | 0.950 | 0.470 |
| 64 | Separate-path | 0.934 | 0.746 | 0.840 | 0.110 |
| 128 | Direct | 0.936 | 0.933 | 0.520 | 0.380 |
| 128 | Shared-path | 0.984 | 0.755 | 0.980 | 0.110 |
| 128 | Separate-path | 0.969 | 0.786 | 0.880 | 0.150 |

## llada V2d: accuracy

| Size | Condition | Order | A | B | Both |
|---:|---|---|---:|---:|---:|
| 16 | Direct | A-first | 100.0 [100.0, 100.0] | 99.0 [97.0, 100.0] | 99.0 [97.0, 100.0] |
| 16 | Direct | B-first | 99.0 [97.0, 100.0] | 99.0 [97.0, 100.0] | 98.0 [95.0, 100.0] |
| 16 | Direct | CF | 99.0 [97.0, 100.0] | 99.0 [97.0, 100.0] | 98.0 [95.0, 100.0] |
| 16 | Shared-path | A-first | 100.0 [100.0, 100.0] | 100.0 [100.0, 100.0] | 100.0 [100.0, 100.0] |
| 16 | Shared-path | B-first | 100.0 [100.0, 100.0] | 99.0 [97.0, 100.0] | 99.0 [97.0, 100.0] |
| 16 | Shared-path | CF | 100.0 [100.0, 100.0] | 100.0 [100.0, 100.0] | 100.0 [100.0, 100.0] |
| 16 | Separate-path | A-first | 100.0 [100.0, 100.0] | 1.0 [0.0, 3.0] | 1.0 [0.0, 3.0] |
| 16 | Separate-path | B-first | 100.0 [100.0, 100.0] | 3.0 [0.0, 7.0] | 3.0 [0.0, 7.0] |
| 16 | Separate-path | CF | 100.0 [100.0, 100.0] | 1.0 [0.0, 3.0] | 1.0 [0.0, 3.0] |
| 32 | Direct | A-first | 99.0 [97.0, 100.0] | 100.0 [100.0, 100.0] | 99.0 [97.0, 100.0] |
| 32 | Direct | B-first | 98.0 [95.0, 100.0] | 100.0 [100.0, 100.0] | 98.0 [95.0, 100.0] |
| 32 | Direct | CF | 98.0 [95.0, 100.0] | 100.0 [100.0, 100.0] | 98.0 [95.0, 100.0] |
| 32 | Shared-path | A-first | 99.0 [97.0, 100.0] | 99.0 [97.0, 100.0] | 99.0 [97.0, 100.0] |
| 32 | Shared-path | B-first | 99.0 [97.0, 100.0] | 98.0 [95.0, 100.0] | 98.0 [95.0, 100.0] |
| 32 | Shared-path | CF | 99.0 [97.0, 100.0] | 99.0 [97.0, 100.0] | 99.0 [97.0, 100.0] |
| 32 | Separate-path | A-first | 99.0 [97.0, 100.0] | 1.0 [0.0, 3.0] | 0.0 [0.0, 0.0] |
| 32 | Separate-path | B-first | 99.0 [97.0, 100.0] | 4.0 [1.0, 8.0] | 3.0 [0.0, 7.0] |
| 32 | Separate-path | CF | 100.0 [100.0, 100.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] |
| 64 | Direct | A-first | 99.0 [97.0, 100.0] | 98.0 [95.0, 100.0] | 97.0 [93.0, 100.0] |
| 64 | Direct | B-first | 95.0 [90.0, 99.0] | 99.0 [97.0, 100.0] | 94.0 [89.0, 98.0] |
| 64 | Direct | CF | 97.0 [93.0, 100.0] | 98.0 [95.0, 100.0] | 95.0 [90.0, 99.0] |
| 64 | Shared-path | A-first | 100.0 [100.0, 100.0] | 93.0 [88.0, 98.0] | 93.0 [88.0, 98.0] |
| 64 | Shared-path | B-first | 97.0 [93.0, 100.0] | 79.0 [71.0, 87.0] | 79.0 [71.0, 87.0] |
| 64 | Shared-path | CF | 100.0 [100.0, 100.0] | 92.0 [86.0, 97.0] | 92.0 [86.0, 97.0] |
| 64 | Separate-path | A-first | 100.0 [100.0, 100.0] | 1.0 [0.0, 3.0] | 1.0 [0.0, 3.0] |
| 64 | Separate-path | B-first | 99.0 [97.0, 100.0] | 2.0 [0.0, 5.0] | 1.0 [0.0, 3.0] |
| 64 | Separate-path | CF | 100.0 [100.0, 100.0] | 1.0 [0.0, 3.0] | 1.0 [0.0, 3.0] |

## llada V2d: B error taxonomy (all sizes)

| Condition | Order | n | correct | target_row_H | target_row_other | distractor_row_same_field | other_table_value | non_table |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| Direct | A-first | 300 | 297 | 2 | 0 | 0 | 0 | 1 |
| Direct | B-first | 300 | 298 | 1 | 0 | 0 | 0 | 1 |
| Direct | CF | 300 | 297 | 2 | 0 | 0 | 0 | 1 |
| Shared-path | A-first | 300 | 292 | 7 | 1 | 0 | 0 | 0 |
| Shared-path | B-first | 300 | 276 | 18 | 6 | 0 | 0 | 0 |
| Shared-path | CF | 300 | 291 | 8 | 1 | 0 | 0 | 0 |
| Separate-path | A-first | 300 | 3 | 3 | 294 | 0 | 0 | 0 |
| Separate-path | B-first | 300 | 9 | 15 | 276 | 0 | 0 | 0 |
| Separate-path | CF | 300 | 2 | 3 | 295 | 0 | 0 | 0 |

## llada V2d: paired A-first vs B-first (B correct)

| Size | Condition | Both right | Both wrong | Only A-first right | Only B-first right | McNemar p | A-first − B-first B accuracy |
|---:|---|---:|---:|---:|---:|---:|---:|
| 16 | Direct | 99 | 1 | 0 | 0 | nan | 0.0 [0.0, 0.0] |
| 16 | Shared-path | 99 | 0 | 1 | 0 | 1 | 1.0 [0.0, 3.0] |
| 16 | Separate-path | 1 | 97 | 0 | 2 | 0.5 | -2.0 [-5.0, 0.0] |
| 32 | Direct | 100 | 0 | 0 | 0 | nan | 0.0 [0.0, 0.0] |
| 32 | Shared-path | 97 | 0 | 2 | 1 | 1 | 1.0 [-2.0, 5.0] |
| 32 | Separate-path | 0 | 95 | 1 | 4 | 0.375 | -3.0 [-8.0, 1.0] |
| 64 | Direct | 97 | 0 | 1 | 2 | 1 | -1.0 [-5.0, 2.0] |
| 64 | Shared-path | 79 | 7 | 14 | 0 | 0.000122 | 14.0 [8.0, 21.0] |
| 64 | Separate-path | 1 | 98 | 0 | 1 | 1 | -1.0 [-3.0, 0.0] |

## llada V2d: order × path interaction

| Size | Shared A-first − B-first | Separate A-first − B-first | Shared − Separate |
|---:|---:|---:|---:|
| 16 | 1.0 [0.0, 3.0] | -2.0 [-5.0, 0.0] | 3.0 [0.0, 7.0] |
| 32 | 1.0 [-2.0, 5.0] | -3.0 [-8.0, 1.0] | 4.0 [-1.0, 10.0] |
| 64 | 14.0 [8.0, 21.0] | -1.0 [-3.0, 0.0] | 15.0 [9.0, 22.0] |

## llada V2d: step-0 confidence and CF

| Size | Condition | Mean A top-1 | Mean B top-1 | CF commits A first | CF min margin < 0.02 |
|---:|---|---:|---:|---:|---:|
| 16 | Direct | 0.992 | 0.992 | 0.540 | 0.900 |
| 16 | Shared-path | 0.993 | 0.959 | 0.810 | 0.690 |
| 16 | Separate-path | 0.990 | 0.944 | 0.840 | 0.600 |
| 32 | Direct | 0.981 | 0.988 | 0.490 | 0.840 |
| 32 | Shared-path | 0.982 | 0.936 | 0.780 | 0.510 |
| 32 | Separate-path | 0.980 | 0.934 | 0.800 | 0.550 |
| 64 | Direct | 0.959 | 0.956 | 0.470 | 0.490 |
| 64 | Shared-path | 0.981 | 0.801 | 0.910 | 0.180 |
| 64 | Separate-path | 0.983 | 0.783 | 0.940 | 0.160 |

## dream V2: accuracy

| Size | Condition | Order | A | B | Both |
|---:|---|---|---:|---:|---:|
| 16 | Direct | A-first | 99.0 [97.0, 100.0] | 96.0 [92.0, 99.0] | 95.0 [90.0, 99.0] |
| 16 | Direct | B-first | 94.0 [89.0, 98.0] | 94.0 [89.0, 98.0] | 89.0 [83.0, 95.0] |
| 16 | Direct | CF | 97.0 [93.0, 100.0] | 96.0 [92.0, 99.0] | 93.0 [88.0, 98.0] |
| 16 | Shared-path | A-first | 99.0 [97.0, 100.0] | 98.0 [95.0, 100.0] | 98.0 [95.0, 100.0] |
| 16 | Shared-path | B-first | 97.0 [93.0, 100.0] | 77.0 [68.0, 85.0] | 77.0 [68.0, 85.0] |
| 16 | Shared-path | CF | 99.0 [97.0, 100.0] | 98.0 [95.0, 100.0] | 98.0 [95.0, 100.0] |
| 16 | Separate-path | A-first | 100.0 [100.0, 100.0] | 73.0 [64.0, 81.0] | 73.0 [64.0, 81.0] |
| 16 | Separate-path | B-first | 100.0 [100.0, 100.0] | 62.0 [52.0, 71.0] | 62.0 [52.0, 71.0] |
| 16 | Separate-path | CF | 100.0 [100.0, 100.0] | 73.0 [64.0, 81.0] | 73.0 [64.0, 81.0] |
| 32 | Direct | A-first | 95.0 [90.0, 99.0] | 84.0 [77.0, 91.0] | 81.0 [73.0, 88.0] |
| 32 | Direct | B-first | 87.0 [80.0, 93.0] | 78.0 [70.0, 86.0] | 67.0 [58.0, 76.0] |
| 32 | Direct | CF | 92.0 [86.0, 97.0] | 82.0 [74.0, 89.0] | 76.0 [68.0, 84.0] |
| 32 | Shared-path | A-first | 99.0 [97.0, 100.0] | 78.0 [70.0, 86.0] | 77.0 [68.0, 85.0] |
| 32 | Shared-path | B-first | 97.0 [93.0, 100.0] | 23.0 [15.0, 31.0] | 22.0 [14.0, 30.0] |
| 32 | Shared-path | CF | 99.0 [97.0, 100.0] | 76.0 [67.0, 84.0] | 75.0 [66.0, 83.0] |
| 32 | Separate-path | A-first | 99.0 [97.0, 100.0] | 42.0 [32.0, 51.0] | 42.0 [32.0, 51.0] |
| 32 | Separate-path | B-first | 95.0 [90.0, 99.0] | 18.0 [11.0, 26.0] | 17.0 [10.0, 25.0] |
| 32 | Separate-path | CF | 99.0 [97.0, 100.0] | 42.0 [32.0, 51.0] | 42.0 [32.0, 51.0] |
| 64 | Direct | A-first | 96.0 [92.0, 99.0] | 77.0 [68.0, 85.0] | 75.0 [66.0, 83.0] |
| 64 | Direct | B-first | 89.0 [83.0, 95.0] | 91.0 [85.0, 96.0] | 81.0 [73.0, 88.0] |
| 64 | Direct | CF | 92.0 [86.0, 97.0] | 80.0 [72.0, 87.0] | 73.0 [64.0, 81.0] |
| 64 | Shared-path | A-first | 97.0 [93.0, 100.0] | 56.0 [46.0, 66.0] | 56.0 [46.0, 66.0] |
| 64 | Shared-path | B-first | 98.0 [95.0, 100.0] | 18.0 [11.0, 26.0] | 18.0 [11.0, 26.0] |
| 64 | Shared-path | CF | 97.0 [93.0, 100.0] | 54.0 [44.0, 64.0] | 54.0 [44.0, 64.0] |
| 64 | Separate-path | A-first | 97.0 [93.0, 100.0] | 24.0 [16.0, 32.0] | 21.0 [13.0, 29.0] |
| 64 | Separate-path | B-first | 93.0 [88.0, 98.0] | 15.0 [9.0, 22.0] | 14.0 [8.0, 21.0] |
| 64 | Separate-path | CF | 99.0 [97.0, 100.0] | 23.0 [15.0, 32.0] | 22.0 [14.0, 30.0] |
| 128 | Direct | A-first | 75.0 [66.0, 83.0] | 43.0 [33.0, 53.0] | 43.0 [33.0, 53.0] |
| 128 | Direct | B-first | 63.0 [53.0, 72.0] | 54.0 [44.0, 64.0] | 49.0 [39.0, 59.0] |
| 128 | Direct | CF | 75.0 [66.0, 83.0] | 44.0 [34.0, 54.0] | 44.0 [34.0, 54.0] |
| 128 | Shared-path | A-first | 50.0 [40.0, 60.0] | 29.0 [20.0, 38.0] | 29.0 [20.0, 38.0] |
| 128 | Shared-path | B-first | 52.0 [42.0, 62.0] | 3.0 [0.0, 7.0] | 3.0 [0.0, 7.0] |
| 128 | Shared-path | CF | 53.0 [43.0, 63.0] | 27.0 [18.0, 36.0] | 27.0 [18.0, 36.0] |
| 128 | Separate-path | A-first | 77.0 [68.0, 85.0] | 8.0 [3.0, 14.0] | 8.0 [3.0, 14.0] |
| 128 | Separate-path | B-first | 59.0 [49.0, 69.0] | 2.0 [0.0, 5.0] | 1.0 [0.0, 3.0] |
| 128 | Separate-path | CF | 77.0 [68.0, 85.0] | 8.0 [3.0, 14.0] | 8.0 [3.0, 14.0] |

## dream V2: B error taxonomy (all sizes)

| Condition | Order | n | correct | target_row_H | target_row_other | distractor_row_same_field | other_table_value | non_table |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| Direct | A-first | 400 | 300 | 55 | 2 | 12 | 26 | 5 |
| Direct | B-first | 400 | 317 | 31 | 7 | 16 | 17 | 12 |
| Direct | CF | 400 | 302 | 55 | 2 | 12 | 23 | 6 |
| Shared-path | A-first | 400 | 261 | 54 | 18 | 52 | 2 | 13 |
| Shared-path | B-first | 400 | 121 | 112 | 103 | 44 | 9 | 11 |
| Shared-path | CF | 400 | 255 | 56 | 26 | 47 | 3 | 13 |
| Separate-path | A-first | 400 | 147 | 17 | 58 | 143 | 12 | 23 |
| Separate-path | B-first | 400 | 97 | 9 | 187 | 80 | 15 | 12 |
| Separate-path | CF | 400 | 146 | 17 | 61 | 139 | 13 | 24 |

## dream V2: paired A-first vs B-first (B correct)

| Size | Condition | Both right | Both wrong | Only A-first right | Only B-first right | McNemar p | A-first − B-first B accuracy |
|---:|---|---:|---:|---:|---:|---:|---:|
| 16 | Direct | 91 | 1 | 5 | 3 | 0.727 | 2.0 [-3.0, 8.0] |
| 16 | Shared-path | 76 | 1 | 22 | 1 | 5.72e-06 | 21.0 [13.0, 30.0] |
| 16 | Separate-path | 56 | 21 | 17 | 6 | 0.0347 | 11.0 [2.0, 21.0] |
| 32 | Direct | 75 | 13 | 9 | 3 | 0.146 | 6.0 [0.0, 13.0] |
| 32 | Shared-path | 23 | 22 | 55 | 0 | 5.55e-17 | 55.0 [45.0, 64.0] |
| 32 | Separate-path | 16 | 56 | 26 | 2 | 3.03e-06 | 24.0 [15.0, 33.0] |
| 64 | Direct | 75 | 7 | 2 | 16 | 0.00131 | -14.0 [-22.0, -6.0] |
| 64 | Shared-path | 18 | 44 | 38 | 0 | 7.28e-12 | 38.0 [29.0, 48.0] |
| 64 | Separate-path | 10 | 71 | 14 | 5 | 0.0636 | 9.0 [1.0, 17.0] |
| 128 | Direct | 37 | 40 | 6 | 17 | 0.0347 | -11.0 [-20.0, -2.0] |
| 128 | Shared-path | 2 | 70 | 27 | 1 | 2.16e-07 | 26.0 [17.0, 35.0] |
| 128 | Separate-path | 2 | 92 | 6 | 0 | 0.0312 | 6.0 [2.0, 11.0] |

## dream V2: order × path interaction

| Size | Shared A-first − B-first | Separate A-first − B-first | Shared − Separate |
|---:|---:|---:|---:|
| 16 | 21.0 [13.0, 30.0] | 11.0 [2.0, 21.0] | 10.0 [-2.0, 22.0] |
| 32 | 55.0 [45.0, 64.0] | 24.0 [15.0, 33.0] | 31.0 [18.0, 43.0] |
| 64 | 38.0 [29.0, 48.0] | 9.0 [1.0, 17.0] | 29.0 [16.0, 41.0] |
| 128 | 26.0 [17.0, 35.0] | 6.0 [2.0, 11.0] | 20.0 [10.0, 30.0] |

## dream V2: step-0 confidence and CF

| Size | Condition | Mean A top-1 | Mean B top-1 | CF commits A first | CF min margin < 0.02 |
|---:|---|---:|---:|---:|---:|
| 16 | Direct | 0.777 | 0.611 | 0.740 | 0.040 |
| 16 | Shared-path | 0.868 | 0.474 | 0.910 | 0.030 |
| 16 | Separate-path | 0.909 | 0.356 | 0.990 | 0.000 |
| 32 | Direct | 0.815 | 0.629 | 0.780 | 0.080 |
| 32 | Shared-path | 0.838 | 0.361 | 0.940 | 0.000 |
| 32 | Separate-path | 0.875 | 0.231 | 0.980 | 0.000 |
| 64 | Direct | 0.849 | 0.663 | 0.770 | 0.100 |
| 64 | Shared-path | 0.813 | 0.399 | 0.940 | 0.000 |
| 64 | Separate-path | 0.885 | 0.308 | 0.960 | 0.010 |
| 128 | Direct | 0.567 | 0.322 | 0.780 | 0.070 |
| 128 | Shared-path | 0.272 | 0.145 | 0.760 | 0.100 |
| 128 | Separate-path | 0.592 | 0.210 | 0.900 | 0.080 |

## dream V2d: accuracy

| Size | Condition | Order | A | B | Both |
|---:|---|---|---:|---:|---:|
| 16 | Direct | A-first | 98.0 [95.0, 100.0] | 94.0 [89.0, 98.0] | 93.0 [88.0, 98.0] |
| 16 | Direct | B-first | 93.0 [88.0, 98.0] | 90.0 [84.0, 95.0] | 84.0 [77.0, 91.0] |
| 16 | Direct | CF | 96.0 [92.0, 99.0] | 95.0 [90.0, 99.0] | 92.0 [86.0, 97.0] |
| 16 | Shared-path | A-first | 100.0 [100.0, 100.0] | 97.0 [93.0, 100.0] | 97.0 [93.0, 100.0] |
| 16 | Shared-path | B-first | 96.0 [92.0, 99.0] | 59.0 [49.0, 68.0] | 59.0 [49.0, 68.0] |
| 16 | Shared-path | CF | 100.0 [100.0, 100.0] | 95.0 [90.0, 99.0] | 95.0 [90.0, 99.0] |
| 16 | Separate-path | A-first | 100.0 [100.0, 100.0] | 3.0 [0.0, 7.0] | 3.0 [0.0, 7.0] |
| 16 | Separate-path | B-first | 97.0 [93.0, 100.0] | 8.0 [3.0, 14.0] | 8.0 [3.0, 14.0] |
| 16 | Separate-path | CF | 100.0 [100.0, 100.0] | 3.0 [0.0, 7.0] | 3.0 [0.0, 7.0] |
| 32 | Direct | A-first | 98.0 [95.0, 100.0] | 82.0 [74.0, 89.0] | 80.0 [72.0, 88.0] |
| 32 | Direct | B-first | 83.0 [75.0, 90.0] | 84.0 [77.0, 91.0] | 68.0 [59.0, 77.0] |
| 32 | Direct | CF | 92.0 [86.0, 97.0] | 82.0 [74.0, 89.0] | 74.0 [65.0, 83.0] |
| 32 | Shared-path | A-first | 98.0 [95.0, 100.0] | 83.0 [76.0, 90.0] | 83.0 [76.0, 90.0] |
| 32 | Shared-path | B-first | 96.0 [92.0, 99.0] | 18.0 [11.0, 26.0] | 18.0 [11.0, 26.0] |
| 32 | Shared-path | CF | 99.0 [97.0, 100.0] | 78.0 [70.0, 86.0] | 78.0 [70.0, 86.0] |
| 32 | Separate-path | A-first | 99.0 [97.0, 100.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] |
| 32 | Separate-path | B-first | 99.0 [97.0, 100.0] | 2.0 [0.0, 5.0] | 2.0 [0.0, 5.0] |
| 32 | Separate-path | CF | 100.0 [100.0, 100.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] |
| 64 | Direct | A-first | 95.0 [90.0, 99.0] | 72.0 [63.0, 81.0] | 70.0 [61.0, 79.0] |
| 64 | Direct | B-first | 78.0 [70.0, 86.0] | 79.0 [71.0, 87.0] | 64.0 [55.0, 73.0] |
| 64 | Direct | CF | 88.0 [81.0, 94.0] | 74.0 [65.0, 82.0] | 64.0 [55.0, 73.0] |
| 64 | Shared-path | A-first | 88.0 [82.0, 94.0] | 41.0 [32.0, 51.0] | 40.0 [31.0, 50.0] |
| 64 | Shared-path | B-first | 90.0 [84.0, 95.0] | 18.0 [11.0, 26.0] | 18.0 [11.0, 26.0] |
| 64 | Shared-path | CF | 92.0 [86.0, 97.0] | 39.0 [30.0, 49.0] | 38.0 [29.0, 48.0] |
| 64 | Separate-path | A-first | 91.0 [85.0, 96.0] | 1.0 [0.0, 3.0] | 1.0 [0.0, 3.0] |
| 64 | Separate-path | B-first | 95.0 [90.0, 99.0] | 2.0 [0.0, 5.0] | 2.0 [0.0, 5.0] |
| 64 | Separate-path | CF | 94.0 [89.0, 98.0] | 1.0 [0.0, 3.0] | 1.0 [0.0, 3.0] |

## dream V2d: B error taxonomy (all sizes)

| Condition | Order | n | correct | target_row_H | target_row_other | distractor_row_same_field | other_table_value | non_table |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| Direct | A-first | 300 | 248 | 41 | 0 | 4 | 0 | 7 |
| Direct | B-first | 300 | 253 | 33 | 1 | 12 | 0 | 1 |
| Direct | CF | 300 | 251 | 39 | 0 | 3 | 0 | 7 |
| Shared-path | A-first | 300 | 221 | 2 | 52 | 7 | 11 | 7 |
| Shared-path | B-first | 300 | 95 | 4 | 168 | 16 | 7 | 10 |
| Shared-path | CF | 300 | 212 | 2 | 64 | 6 | 9 | 7 |
| Separate-path | A-first | 300 | 4 | 2 | 270 | 0 | 17 | 7 |
| Separate-path | B-first | 300 | 12 | 5 | 260 | 0 | 15 | 8 |
| Separate-path | CF | 300 | 4 | 2 | 273 | 0 | 15 | 6 |

## dream V2d: paired A-first vs B-first (B correct)

| Size | Condition | Both right | Both wrong | Only A-first right | Only B-first right | McNemar p | A-first − B-first B accuracy |
|---:|---|---:|---:|---:|---:|---:|---:|
| 16 | Direct | 87 | 3 | 7 | 3 | 0.344 | 4.0 [-2.0, 10.0] |
| 16 | Shared-path | 59 | 3 | 38 | 0 | 7.28e-12 | 38.0 [29.0, 48.0] |
| 16 | Separate-path | 3 | 92 | 0 | 5 | 0.0625 | -5.0 [-10.0, -1.0] |
| 32 | Direct | 78 | 12 | 4 | 6 | 0.754 | -2.0 [-8.0, 4.0] |
| 32 | Shared-path | 17 | 16 | 66 | 1 | 9.22e-19 | 65.0 [55.0, 74.0] |
| 32 | Separate-path | 0 | 98 | 0 | 2 | 0.5 | -2.0 [-5.0, 0.0] |
| 64 | Direct | 64 | 13 | 8 | 15 | 0.21 | -7.0 [-16.0, 2.0] |
| 64 | Shared-path | 14 | 55 | 27 | 4 | 3.4e-05 | 23.0 [13.0, 33.0] |
| 64 | Separate-path | 1 | 98 | 0 | 1 | 1 | -1.0 [-3.0, 0.0] |

## dream V2d: order × path interaction

| Size | Shared A-first − B-first | Separate A-first − B-first | Shared − Separate |
|---:|---:|---:|---:|
| 16 | 38.0 [29.0, 48.0] | -5.0 [-10.0, -1.0] | 43.0 [33.0, 53.0] |
| 32 | 65.0 [55.0, 74.0] | -2.0 [-5.0, 0.0] | 67.0 [57.0, 76.0] |
| 64 | 23.0 [13.0, 33.0] | -1.0 [-3.0, 0.0] | 24.0 [14.0, 34.0] |

## dream V2d: step-0 confidence and CF

| Size | Condition | Mean A top-1 | Mean B top-1 | CF commits A first | CF min margin < 0.02 |
|---:|---|---:|---:|---:|---:|
| 16 | Direct | 0.806 | 0.637 | 0.730 | 0.020 |
| 16 | Shared-path | 0.911 | 0.470 | 0.930 | 0.010 |
| 16 | Separate-path | 0.911 | 0.404 | 0.960 | 0.050 |
| 32 | Direct | 0.844 | 0.622 | 0.810 | 0.040 |
| 32 | Shared-path | 0.879 | 0.457 | 0.920 | 0.040 |
| 32 | Separate-path | 0.865 | 0.452 | 0.900 | 0.020 |
| 64 | Direct | 0.840 | 0.607 | 0.840 | 0.060 |
| 64 | Shared-path | 0.703 | 0.372 | 0.840 | 0.080 |
| 64 | Separate-path | 0.719 | 0.335 | 0.890 | 0.020 |

## Interpretation limits

- Table size is calibrated per model, so the two models are compared descriptively, not as a test.
- A is always left of B in this stage; position is studied separately (RQ1 study, Exp 4).
- Separate-path is held only to a chance-level gate (team decision B).

## Deviations

# Phase 1.5 decisions and deviations

- 2026-11-17: Team decision B on the gate. Separate-path B must only have a 95% lower bound above chance, not 40–80%. Direct ≥ 90% under each order and Shared-path at 40–80% (averaged over orders) are hard requirements.
- 2026-11-17: V4's instruction reads "Fill field a from a column labeled a and field b from a column labeled b.", with mapping columns labeled to match, so it is true in every condition. The original wording ("both values come from the target row") is false on the path conditions. Approved by the team.
- 2026-11-17: Pool. 17–25% of Phase 1 pool words merge with a preceding `=` (e.g. `=int`), so the pool requires each word to stay its own token after `=`. One pool serves every variant, keeping variants paired on identical sources.
- 2026-11-17: The first pool build excluded prompt words but not chat-template words; Dream's pool contained `assistant`, `system` and `you`, and LLaDA's `user`, `start`, `header` and `end`. Found by the dev task audit (76 extra value matches in Dream prompts) before any model run. The pool now also excludes each model's chat-template words: 4,015 words for LLaDA (was 4,019) and 4,759 for Dream (was 4,762). Dev audit rerun: 0 failures.
- 2026-11-17: Anchor and mapping row orders are shared across conditions within a source. Phase 1 drew a separate shuffle per condition. This makes condition and variant comparisons paired.
- 2026-11-17: Hardware deviation from the PREREG. At smoke time, another user's vLLM servers held 43–45 GB on all eight rosetta21 A6000s, and the smoke run ran out of memory while loading weights; no rows were written and the empty smoke directory was deleted. rosetta7's eight A6000s were all at 97–100% utilization. Following the fallback order, all of Phase 1.5 (smoke, dev, V5 arm, test) runs on rosetta15 (NVIDIA A100-PCIE-40GB); no Phase 1.5 split mixes GPU types. Stage 0 measured the A6000→A100 effect on Phase 1 Exp 2: 2.4% (LLaDA) and 4.8% (Dream) of individual decisions flip, and cell-level B accuracy moves by at most 1.3 points. Phase 1.5 numbers are therefore compared to Phase 1 only at the cell level.
- 2026-11-17: Dev V1–V4 complete (10,800 rows per model, rosetta15 A100). No variant passed. Per the selection rule, the closest variant is V3 (16/20 criteria): Direct passes for both models, but Shared-path B is above the 80% ceiling (LLaDA 100%, Dream 87–91%). V2 fails the same way; V1 and V4 fail Direct. The V5 arm runs V3-nochat on the same dev sources.
- 2026-11-17: V5 arm (V3-nochat, 2,700 rows per model) also failed: Shared-path above 80% for both models and Dream Direct CF at size 4 = 89%. Per the selection rule no variant is frozen and **no test run happens**. Test seed 15002 remains unused.
- 2026-11-17: Observation for the next round (dev data, not a selection): V2 and V3 put LLaDA at 100% on every condition and order up to size 16, so the path conditions are far too easy in explicit row formats. In V3, Dream writes the target's H into field a on Separate-path at size 16 (60 of 100 CF rows), while V2 keeps Dream's A at 98%.
- 2026-11-17: **Finding to carry into the write-up: LLaDA's Phase 1 order effect may reflect format confusion.** In Phase 1's space-separated format, LLaDA's Shared-path B was 27–44 points higher under A-first than B-first, and Direct B failed because the model copied the target row's H. Under the explicit V2/V3 formats (Phase 1.5 dev), LLaDA answers every condition at 100% up to size 16, with no A-first vs B-first gap. So at least part of LLaDA's Phase 1 order effect may come from misreading the table rather than from the a→b dependency. Dream still shows a large gap when the task is hard (V3, size 16: Shared-path B 93% A-first vs 62% B-first). Phase 1.5b and Exp 4 test the order effect under a format the model reads correctly.
- 2026-11-17: Team approved Phase 1.5b (`PREREG_1_5b.md`): V2 at sizes 16–128 with per-model sizes, decoy fallback V2d, cross-model comparisons descriptive only. In parallel, an RQ1 role × layout commit-rank study runs on V2 at size 8, where V2 dev Direct B was ≥ 90% for both models (`experiments/rq1/PREREG.md`).
- 2026-11-17: Phase 1.5b dev, LLaDA (6,300 rows, rosetta21 A6000): no cell passes. V2 keeps Direct at 96–100% at every size, but Shared-path stays above 80% (100% up to size 64; 88.3% [83.3, 92.7] at 128). V2d decoys leave Shared-path high and drive Separate-path to 1–2%: LLaDA follows the a-keyed decoy rows instead of the h-keyed path. Per the rule, LLaDA has no frozen cell and **no Phase 1.5b test run**; its closest cell is V2-32 (4/5 criteria, Direct 100% under every order). Applied to LLaDA rows only, before Dream's dev finished; the rule is per model.
