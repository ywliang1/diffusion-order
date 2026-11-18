# exp4: role × layout × hop with PF/DF

## llada: summary

Table size [128]; rows 6400; hosts/GPUs/commits [('rosetta21.csail.mit.edu', 'NVIDIA RTX A6000', 'e6dbb9ba49722736fb2e8fff94ad74a98b6ff091')].

- **H2: supported (two-hop PF − DF > 0 and larger than in one-hop controls).**
- **H1 at this size: supported.**
- CF traces with a margin below 0.02: 26.2%.

## llada: H2 (dependent-field accuracy, PF vs DF)

| Hop | Items | PF − DF dependent accuracy | Both right | Both wrong | Only PF right | Only DF right | McNemar p |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 2 | 400 | 54.5 [49.7, 59.2] | 137 | 39 | 221 | 3 | 1.39e-61 |
| 1 | 400 | -1.0 [-2.8, 0.5] | 391 | 1 | 2 | 6 | 0.289 |

Hop × order interaction, (PF − DF | two-hop) − (PF − DF | one-hop): 55.5 [50.7, 60.2] points.

## llada: accuracy by order

| Hop | Order | n items | Dependent correct | Prerequisite correct | Both correct |
|---:|---|---:|---:|---:|---:|
| 2 | CF | 400 | 76.8 [72.5, 80.8] | 86.0 [83.5, 88.5] | 76.8 [72.5, 80.8] |
| 2 | PF | 400 | 89.5 [85.2, 93.2] | 97.8 [96.2, 99.0] | 89.5 [85.2, 93.2] |
| 2 | DF | 400 | 35.0 [30.5, 39.5] | 72.0 [68.5, 75.0] | 35.0 [30.5, 39.5] |
| 2 | L2R | 400 | 59.5 [55.2, 63.5] | 76.2 [74.2, 78.2] | 59.5 [55.2, 63.5] |
| 2 | R2L | 400 | 65.0 [61.5, 68.2] | 93.5 [91.0, 95.8] | 65.0 [61.5, 68.2] |
| 2 | random | 400 | 62.3 [58.6, 65.8] | 84.5 [82.3, 86.5] | 62.3 [58.6, 65.8] |
| 1 | CF | 400 | 98.5 [96.8, 99.8] | 97.0 [95.2, 98.5] | 95.5 [93.0, 97.8] |
| 1 | PF | 400 | 98.2 [96.5, 99.8] | 98.5 [97.2, 99.5] | 96.8 [94.2, 98.8] |
| 1 | DF | 400 | 99.2 [98.2, 100.0] | 96.0 [93.8, 98.0] | 95.2 [92.8, 97.5] |
| 1 | L2R | 400 | 98.5 [97.2, 99.5] | 98.5 [97.2, 99.5] | 97.0 [95.0, 98.8] |
| 1 | R2L | 400 | 99.0 [98.0, 99.8] | 96.0 [93.8, 98.0] | 95.0 [92.2, 97.2] |
| 1 | random | 400 | 98.5 [97.3, 99.5] | 97.2 [95.4, 98.7] | 95.7 [93.1, 97.8] |

## llada: H1 (CF commit rank, two-hop)

| Effect | Mixed model coef [95% CI] | Bootstrap [95% CI] |
|---|---:|---:|
| Position (right − left) | +0.290 [+0.243, +0.337] | +0.290 [+0.235, +0.345] |
| Role (dependent − prerequisite) | +0.630 [+0.583, +0.677] | +0.630 [+0.560, +0.695] |
| Field (b − a) | +0.240 [+0.193, +0.287] | +0.240 [+0.170, +0.310] |

## llada: CF cells

| Hop | Query direction | Layout | n | Left field first | Prerequisite first | a correct | b correct | Both correct |
|---:|---|---|---:|---:|---:|---:|---:|---:|
| 2 | a | ab | 100 | 96.0 [92.0, 99.0] | 96.0 [92.0, 99.0] | 100.0 [100.0, 100.0] | 91.0 [85.0, 96.0] | 91.0 [85.0, 96.0] |
| 2 | a | ba | 100 | 9.0 [4.0, 15.0] | 91.0 [85.0, 96.0] | 100.0 [100.0, 100.0] | 95.0 [90.0, 99.0] | 95.0 [90.0, 99.0] |
| 2 | b | ab | 100 | 57.0 [47.0, 67.0] | 43.0 [33.0, 53.0] | 42.0 [33.0, 52.0] | 45.0 [35.0, 55.0] | 42.0 [33.0, 52.0] |
| 2 | b | ba | 100 | 96.0 [92.0, 99.0] | 96.0 [92.0, 99.0] | 79.0 [71.0, 87.0] | 99.0 [97.0, 100.0] | 79.0 [71.0, 87.0] |
| 1 | a | ab | 100 | 49.0 [39.0, 59.0] | 49.0 [39.0, 59.0] | 88.0 [81.0, 94.0] | 98.0 [95.0, 100.0] | 86.0 [79.0, 92.0] |
| 1 | a | ba | 100 | 55.0 [45.0, 65.0] | 45.0 [35.0, 55.0] | 100.0 [100.0, 100.0] | 99.0 [97.0, 100.0] | 99.0 [97.0, 100.0] |
| 1 | b | ab | 100 | 24.0 [16.0, 32.0] | 76.0 [68.0, 84.0] | 99.0 [97.0, 100.0] | 100.0 [100.0, 100.0] | 99.0 [97.0, 100.0] |
| 1 | b | ba | 100 | 63.0 [54.0, 72.0] | 63.0 [54.0, 72.0] | 98.0 [95.0, 100.0] | 100.0 [100.0, 100.0] | 98.0 [95.0, 100.0] |

## llada: alignment

Prerequisite field committed first: two-hop 81.5 [78.0, 84.8], one-hop (direction field) 58.2 [55.2, 61.5], difference 23.2 [18.8, 27.8] percentage points.

## dream: summary

Table size [16]; rows 12800; hosts/GPUs/commits [('rosetta21.csail.mit.edu', 'NVIDIA RTX A6000', 'e6dbb9ba49722736fb2e8fff94ad74a98b6ff091')].

- **H2: supported (two-hop PF − DF > 0 and larger than in one-hop controls).**
- **H1 at this size: supported.**
- CF traces with a margin below 0.02: 8.0%.

## dream: H2 (dependent-field accuracy, PF vs DF)

| Hop | Items | PF − DF dependent accuracy | Both right | Both wrong | Only PF right | Only DF right | McNemar p |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 2 | 800 | 14.9 [11.8, 18.1] | 649 | 24 | 123 | 4 | 1.25e-31 |
| 1 | 800 | 8.6 [6.0, 11.2] | 611 | 72 | 93 | 24 | 8.89e-11 |

Hop × order interaction, (PF − DF | two-hop) − (PF − DF | one-hop): 6.2 [2.4, 10.2] points.

## dream: accuracy by order

| Hop | Order | n items | Dependent correct | Prerequisite correct | Both correct |
|---:|---|---:|---:|---:|---:|
| 2 | CF | 800 | 95.6 [93.6, 97.4] | 98.4 [97.1, 99.4] | 95.1 [92.9, 97.1] |
| 2 | PF | 800 | 96.5 [94.8, 98.0] | 96.8 [95.0, 98.2] | 94.4 [92.0, 96.5] |
| 2 | DF | 800 | 81.6 [77.9, 85.1] | 96.0 [94.1, 97.6] | 81.6 [77.9, 85.1] |
| 2 | L2R | 800 | 88.8 [86.2, 91.1] | 96.2 [94.6, 97.8] | 88.0 [85.4, 90.5] |
| 2 | R2L | 800 | 89.4 [86.8, 91.8] | 96.5 [94.9, 97.9] | 88.0 [85.1, 90.8] |
| 2 | random | 800 | 89.2 [86.7, 91.5] | 96.6 [95.2, 97.9] | 88.1 [85.5, 90.7] |
| 1 | CF | 800 | 87.0 [84.2, 89.6] | 92.4 [90.2, 94.4] | 83.1 [80.0, 86.1] |
| 1 | PF | 800 | 88.0 [85.2, 90.6] | 93.0 [91.1, 94.8] | 83.0 [79.9, 86.0] |
| 1 | DF | 800 | 79.4 [76.2, 82.5] | 88.9 [86.4, 91.2] | 75.6 [72.1, 79.1] |
| 1 | L2R | 800 | 83.1 [80.5, 85.8] | 91.6 [89.6, 93.5] | 81.8 [78.8, 84.6] |
| 1 | R2L | 800 | 84.2 [81.1, 87.2] | 90.2 [87.9, 92.5] | 76.9 [73.1, 80.5] |
| 1 | random | 800 | 83.6 [80.9, 86.3] | 91.0 [89.0, 92.9] | 79.3 [76.2, 82.4] |

## dream: H1 (CF commit rank, two-hop)

| Effect | Mixed model coef [95% CI] | Bootstrap [95% CI] |
|---|---:|---:|
| Position (right − left) | +0.113 [+0.074, +0.151] | +0.113 [+0.077, +0.147] |
| Role (dependent − prerequisite) | +0.562 [+0.524, +0.601] | +0.562 [+0.500, +0.623] |
| Field (b − a) | +0.253 [+0.214, +0.291] | +0.253 [+0.180, +0.323] |

## dream: CF cells

| Hop | Query direction | Layout | n | Left field first | Prerequisite first | a correct | b correct | Both correct |
|---:|---|---|---:|---:|---:|---:|---:|---:|
| 2 | a | ab | 200 | 93.5 [90.0, 96.5] | 93.5 [90.0, 96.5] | 99.0 [97.5, 100.0] | 92.5 [88.5, 96.0] | 92.5 [88.5, 96.0] |
| 2 | a | ba | 200 | 12.0 [7.5, 16.5] | 88.0 [83.5, 92.5] | 99.0 [97.5, 100.0] | 93.5 [90.0, 96.5] | 93.5 [90.0, 96.5] |
| 2 | b | ab | 200 | 43.0 [36.0, 50.0] | 57.0 [50.0, 64.0] | 97.5 [95.0, 99.5] | 96.5 [94.0, 99.0] | 95.5 [92.5, 98.0] |
| 2 | b | ba | 200 | 74.0 [67.5, 80.0] | 74.0 [67.5, 80.0] | 99.0 [97.5, 100.0] | 99.0 [97.5, 100.0] | 99.0 [97.5, 100.0] |
| 1 | a | ab | 200 | 72.5 [66.0, 78.5] | 72.5 [66.0, 78.5] | 94.5 [91.0, 97.5] | 89.5 [85.0, 93.5] | 85.0 [80.0, 90.0] |
| 1 | a | ba | 200 | 48.5 [41.5, 55.5] | 51.5 [44.5, 58.5] | 99.5 [98.5, 100.0] | 98.0 [96.0, 99.5] | 97.5 [95.0, 99.5] |
| 1 | b | ab | 200 | 48.0 [41.0, 55.0] | 52.0 [45.0, 59.0] | 70.5 [64.0, 76.5] | 80.0 [74.5, 85.5] | 64.0 [57.5, 70.5] |
| 1 | b | ba | 200 | 83.5 [78.0, 88.5] | 83.5 [78.0, 88.5] | 90.0 [85.5, 94.0] | 95.5 [92.5, 98.0] | 86.0 [81.0, 90.5] |

## dream: alignment

Prerequisite field committed first: two-hop 78.1 [75.0, 81.1], one-hop (direction field) 64.9 [61.8, 68.1], difference 13.2 [8.8, 17.8] percentage points.

## Interpretation limits

- Table size is calibrated per model; between-model comparisons are descriptive.
- Single-token values: a field rank is 0 or 1, and the role × position interaction is not identifiable (see RQ1 study).
- Random orders are averaged over three seeds within each item before any comparison.

## Deviations

# Exp 4 decisions and deviations

- 2026-11-17: Exp 4 calibrates its own table size (`PREREG.md`), because LLaDA did not meet the Phase 1.5b gate at any size up to 128.
- 2026-11-17: Dev calibration (1,600 CF rows per model). LLaDA: size 128 (two-hop dependent 73.0%, one-hop 96.5%; in band). Dream: no size reached 90% one-hop (81.5% at 16, 57.5% at 32, 68.0% at 64, 42.5% at 128), so the fallback branch picks 16, where two-hop dependent accuracy is 96.0%, outside the 40–80% band. H2 for Dream is therefore tested near ceiling and is expected to be weak. Main run: LLaDA 100 sources at 128, Dream 200 sources at 16 (seed 40001; task audits clean).
- 2026-11-18 (after the main run): **H1 depends on table size for LLaDA.** At 128 rows, the CF position effect is +0.290 [+0.235, +0.345] (bootstrap), so H1 is supported. At 8 rows (RQ1 study), the same contrast was +0.013 [−0.018, +0.043], so H1 was contradicted. The field-identity effect (b − a) is also large at this size: +0.240 for LLaDA and +0.253 for Dream. In the two-hop direction-b × layout-ab cell, LLaDA commits the prerequisite first in only 43% of traces and gets 42% of both fields right. That cell drives most of both effects. Read H1 as "position and field identity matter once lookup is hard", not as a clean position effect. Dream's one-hop PF − DF gap is +8.6 points [6.0, 11.2], not near 0. Its hop × order interaction, +6.2 [2.4, 10.2], still meets the H2 rule.
- 2026-11-18: The first `analyze` call wrote an empty summary. The rerun a minute later, with identical inputs, produced the report above. No input changed between the two calls, the cause is unknown, and the rerun's results are the ones reported.
