# BFCL: commitment order on single-turn tool calls

## llada: metrics by schema and order

Rows: 4800; schemas: ['original', 'reversed'].

| Schema | Order | Parse valid | AST accuracy | Wrong function | Argument error | Wrong count | AST among parseable | Hit length limit |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| original | L2R | 70.0 [65.5, 74.5] | 41.2 [36.5, 46.0] | 0.5 [0.0, 1.2] | 11.5 [8.5, 14.8] | 16.8 [13.2, 20.5] | 58.9 [53.2, 64.6] | 0.0 [0.0, 0.0] |
| original | R2L | 36.2 [31.5, 41.0] | 7.2 [4.8, 9.8] | 1.2 [0.2, 2.5] | 3.8 [2.0, 5.8] | 24.0 [19.8, 28.2] | 20.0 [13.8, 26.9] | 0.0 [0.0, 0.0] |
| original | random | 53.8 [50.2, 57.2] | 18.7 [16.1, 21.3] | 2.5 [1.7, 3.3] | 25.5 [22.8, 28.2] | 7.1 [5.5, 8.8] | 34.7 [30.6, 39.0] | 0.0 [0.0, 0.0] |
| original | CF | 78.0 [74.0, 82.0] | 50.5 [45.5, 55.2] | 2.2 [1.0, 3.8] | 10.8 [7.8, 14.0] | 14.5 [11.2, 18.0] | 64.7 [59.3, 69.9] | 0.0 [0.0, 0.0] |
| reversed | L2R | 66.2 [61.5, 70.8] | 40.0 [35.2, 44.8] | 0.5 [0.0, 1.2] | 11.5 [8.5, 14.8] | 14.2 [11.0, 17.8] | 60.4 [54.3, 66.0] | 0.0 [0.0, 0.0] |
| reversed | R2L | 34.0 [29.5, 38.5] | 4.0 [2.2, 6.0] | 2.5 [1.0, 4.2] | 3.8 [2.0, 5.8] | 23.8 [19.5, 28.0] | 11.8 [6.6, 17.6] | 0.0 [0.0, 0.0] |
| reversed | random | 55.2 [51.8, 58.5] | 17.1 [14.7, 19.7] | 2.0 [1.2, 2.8] | 26.8 [24.1, 29.8] | 9.2 [7.4, 11.2] | 31.0 [27.0, 34.9] | 0.0 [0.0, 0.0] |
| reversed | CF | 74.5 [70.2, 78.8] | 47.8 [42.8, 52.5] | 2.8 [1.2, 4.5] | 10.2 [7.5, 13.5] | 13.8 [10.5, 17.2] | 64.1 [58.7, 69.5] | 0.0 [0.0, 0.0] |

## llada: order and schema contrasts

| Contrast | Items | AST accuracy difference [95% CI] |
|---|---:|---:|
| original: R2L − L2R | 400 | -34.0 [-39.0, -29.0] |
| original: random − L2R | 400 | -22.6 [-27.6, -17.5] |
| original: CF − L2R | 400 | 9.2 [3.5, 15.0] |
| reversed: R2L − L2R | 400 | -36.0 [-41.0, -31.0] |
| reversed: random − L2R | 400 | -22.9 [-27.6, -18.1] |
| reversed: CF − L2R | 400 | 7.8 [2.0, 13.2] |
| L2R: reversed − original schema | 400 | -1.2 [-6.0, 3.5] |
| R2L: reversed − original schema | 400 | -3.2 [-5.2, -1.5] |
| random: reversed − original schema | 400 | -1.6 [-3.8, 0.7] |
| CF: reversed − original schema | 400 | -2.8 [-6.8, 1.5] |

## llada: by category

| Category | Schema | Order | AST accuracy | Wrong function |
|---|---|---|---:|---:|
| simple_python | original | L2R | 47.0 [40.0, 54.0] | 0.0 [0.0, 0.0] |
| simple_python | original | R2L | 9.5 [5.5, 13.5] | 2.0 [0.5, 4.0] |
| simple_python | original | random | 19.2 [15.3, 23.2] | 3.0 [1.7, 4.3] |
| simple_python | original | CF | 63.0 [56.5, 69.5] | 1.5 [0.0, 3.5] |
| simple_python | reversed | L2R | 48.0 [41.0, 55.0] | 0.0 [0.0, 0.0] |
| simple_python | reversed | R2L | 6.0 [3.0, 9.5] | 4.0 [1.5, 7.0] |
| simple_python | reversed | random | 18.2 [14.7, 22.0] | 1.7 [0.7, 2.7] |
| simple_python | reversed | CF | 60.0 [53.0, 66.5] | 2.5 [0.5, 5.0] |
| multiple | original | L2R | 35.5 [29.0, 42.5] | 1.0 [0.0, 2.5] |
| multiple | original | R2L | 5.0 [2.5, 8.5] | 0.5 [0.0, 1.5] |
| multiple | original | random | 18.2 [14.5, 22.0] | 2.0 [1.0, 3.2] |
| multiple | original | CF | 38.0 [31.5, 44.5] | 3.0 [1.0, 5.5] |
| multiple | reversed | L2R | 32.0 [26.0, 38.5] | 1.0 [0.0, 2.5] |
| multiple | reversed | R2L | 2.0 [0.5, 4.0] | 1.0 [0.0, 2.5] |
| multiple | reversed | random | 16.0 [12.7, 19.5] | 2.3 [1.2, 3.7] |
| multiple | reversed | CF | 35.5 [29.0, 42.5] | 3.0 [1.0, 5.5] |

## llada: EOS commit rank by order

| Schema | Order | First end token commit rank | Mean commit rank of non-content positions | Content tokens |
|---|---|---:|---:|---:|
| original | L2R | 0.616 [0.588, 0.643] | 0.808 [0.794, 0.822] | 38.8 |
| original | R2L | 0.304 [0.265, 0.344] | 0.152 [0.132, 0.172] | 43.8 |
| original | random | 0.528 [0.512, 0.544] | 0.502 [0.495, 0.510] | 39.3 |
| original | CF | 0.608 [0.565, 0.650] | 0.304 [0.281, 0.327] | 37.8 |
| reversed | L2R | 0.610 [0.582, 0.637] | 0.805 [0.791, 0.818] | 38.4 |
| reversed | R2L | 0.304 [0.265, 0.345] | 0.152 [0.133, 0.172] | 43.8 |
| reversed | random | 0.529 [0.513, 0.544] | 0.502 [0.495, 0.510] | 40.0 |
| reversed | CF | 0.579 [0.537, 0.621] | 0.287 [0.265, 0.308] | 38.8 |

## llada: function-name commit rank vs wrong-function errors

Rows: 1876 (CF and random orders, parseable, called name identified); wrong-function rate 0.029.
Mixed logistic (VB, random intercept per item): fn_rank log-odds +4.276 [+3.770, +4.783] (posterior mean ± 1.96 sd).
GEE logistic (exchangeable within item): fn_rank log-odds +4.937 [+3.312, +6.562], p = 2.59e-09.

## dream: metrics by schema and order

Rows: 4800; schemas: ['original', 'reversed'].

| Schema | Order | Parse valid | AST accuracy | Wrong function | Argument error | Wrong count | AST among parseable | Hit length limit |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| original | L2R | 87.0 [83.8, 90.2] | 77.5 [73.5, 81.5] | 0.0 [0.0, 0.0] | 7.5 [5.0, 10.2] | 2.0 [0.8, 3.5] | 89.1 [85.6, 92.2] | 0.2 [0.0, 0.8] |
| original | R2L | 60.2 [55.5, 65.0] | 6.2 [4.0, 8.8] | 1.5 [0.5, 2.8] | 1.2 [0.2, 2.5] | 51.2 [46.5, 56.2] | 10.4 [6.6, 14.1] | 0.0 [0.0, 0.0] |
| original | random | 44.2 [41.2, 47.2] | 15.0 [12.8, 17.2] | 2.2 [1.4, 3.2] | 26.5 [24.0, 29.0] | 0.5 [0.2, 0.9] | 33.9 [29.5, 38.3] | 0.2 [0.0, 0.4] |
| original | CF | 87.2 [84.0, 90.5] | 66.0 [61.3, 70.8] | 0.5 [0.0, 1.2] | 20.2 [16.2, 24.2] | 0.5 [0.0, 1.2] | 75.6 [71.1, 79.9] | 0.0 [0.0, 0.0] |
| reversed | L2R | 88.2 [85.0, 91.2] | 78.8 [74.8, 82.8] | 0.0 [0.0, 0.0] | 8.0 [5.5, 10.8] | 1.5 [0.5, 2.8] | 89.2 [85.8, 92.4] | 0.0 [0.0, 0.0] |
| reversed | R2L | 64.8 [60.0, 69.5] | 2.8 [1.2, 4.5] | 1.2 [0.2, 2.5] | 1.2 [0.2, 2.5] | 59.5 [54.8, 64.2] | 4.2 [1.9, 6.9] | 0.0 [0.0, 0.0] |
| reversed | random | 46.5 [43.2, 49.8] | 17.6 [15.0, 20.2] | 1.5 [0.8, 2.2] | 26.9 [24.2, 29.8] | 0.5 [0.2, 0.9] | 37.8 [33.2, 42.5] | 0.0 [0.0, 0.0] |
| reversed | CF | 89.8 [86.8, 92.5] | 64.2 [59.5, 69.0] | 0.5 [0.0, 1.2] | 24.5 [20.2, 28.7] | 0.5 [0.0, 1.2] | 71.6 [66.9, 76.3] | 0.0 [0.0, 0.0] |

## dream: order and schema contrasts

| Contrast | Items | AST accuracy difference [95% CI] |
|---|---:|---:|
| original: R2L − L2R | 400 | -71.2 [-75.8, -66.8] |
| original: random − L2R | 400 | -62.5 [-66.9, -58.0] |
| original: CF − L2R | 400 | -11.5 [-17.0, -6.0] |
| reversed: R2L − L2R | 400 | -76.0 [-80.0, -71.8] |
| reversed: random − L2R | 400 | -61.2 [-65.5, -56.7] |
| reversed: CF − L2R | 400 | -14.5 [-20.2, -8.8] |
| L2R: reversed − original schema | 400 | 1.2 [-1.5, 4.0] |
| R2L: reversed − original schema | 400 | -3.5 [-6.0, -1.0] |
| random: reversed − original schema | 400 | 2.6 [0.2, 5.0] |
| CF: reversed − original schema | 400 | -1.8 [-7.2, 3.5] |

## dream: by category

| Category | Schema | Order | AST accuracy | Wrong function |
|---|---|---|---:|---:|
| simple_python | original | L2R | 81.5 [76.0, 86.5] | 0.0 [0.0, 0.0] |
| simple_python | original | R2L | 6.0 [3.0, 9.5] | 2.0 [0.5, 4.0] |
| simple_python | original | random | 14.8 [11.8, 18.2] | 2.5 [1.2, 4.0] |
| simple_python | original | CF | 68.5 [62.0, 75.0] | 0.5 [0.0, 1.5] |
| simple_python | reversed | L2R | 80.0 [74.5, 85.5] | 0.0 [0.0, 0.0] |
| simple_python | reversed | R2L | 2.5 [0.5, 5.0] | 1.0 [0.0, 2.5] |
| simple_python | reversed | random | 18.3 [14.7, 22.2] | 1.2 [0.3, 2.0] |
| simple_python | reversed | CF | 64.0 [57.0, 70.5] | 0.5 [0.0, 1.5] |
| multiple | original | L2R | 73.5 [67.0, 79.5] | 0.0 [0.0, 0.0] |
| multiple | original | R2L | 6.5 [3.5, 10.0] | 1.0 [0.0, 2.5] |
| multiple | original | random | 15.2 [12.0, 18.3] | 2.0 [1.0, 3.2] |
| multiple | original | CF | 63.5 [57.0, 70.0] | 0.5 [0.0, 1.5] |
| multiple | reversed | L2R | 77.5 [71.5, 83.5] | 0.0 [0.0, 0.0] |
| multiple | reversed | R2L | 3.0 [1.0, 5.5] | 1.5 [0.0, 3.5] |
| multiple | reversed | random | 16.8 [13.5, 20.3] | 1.8 [0.8, 3.0] |
| multiple | reversed | CF | 64.5 [58.0, 71.0] | 0.5 [0.0, 1.5] |

## dream: EOS commit rank by order

| Schema | Order | First end token commit rank | Mean commit rank of non-content positions | Content tokens |
|---|---|---:|---:|---:|
| original | L2R | 0.375 [0.360, 0.391] | 0.688 [0.680, 0.696] | 23.8 |
| original | R2L | 0.835 [0.811, 0.858] | 0.417 [0.406, 0.429] | 10.4 |
| original | random | 0.452 [0.435, 0.469] | 0.504 [0.499, 0.509] | 26.1 |
| original | CF | 0.892 [0.877, 0.905] | 0.388 [0.380, 0.396] | 22.9 |
| reversed | L2R | 0.384 [0.368, 0.401] | 0.692 [0.684, 0.700] | 24.2 |
| reversed | R2L | 0.865 [0.841, 0.887] | 0.432 [0.420, 0.443] | 8.5 |
| reversed | random | 0.452 [0.435, 0.470] | 0.504 [0.499, 0.509] | 26.4 |
| reversed | CF | 0.895 [0.881, 0.907] | 0.398 [0.391, 0.405] | 20.7 |

## dream: function-name commit rank vs wrong-function errors

Rows: 1776 (CF and random orders, parseable, called name identified); wrong-function rate 0.021.
Mixed logistic (VB, random intercept per item): fn_rank log-odds +2.575 [+1.906, +3.243] (posterior mean ± 1.96 sd).
GEE logistic (exchangeable within item): fn_rank log-odds +3.224 [+1.262, +5.185], p = 0.00128.

## Harness sanity check

- dream, CF, 100 live_simple items, JSON format: AST accuracy 77.0 [68.0, 85.0], parse valid 100.0 [100.0, 100.0] (team reference for Dream greedy: about 64%).

## Interpretation limits

- One commit per forward pass on a 64-token canvas; results are not comparable to standard (multi-token-per-step) diffusion decoding.
- Function-name rank analyses are associations, not effects of the rank.
- Blocks not run before the session ended are listed as not run; there are no partial blocks.

## Deviations

# BFCL decisions and deviations

- 2026-11-17: bfcl-eval 2026.3.23 runs in an isolated venv (it pins numpy 1.26, which conflicts with the generation venv). A no-deps install failed because the AST checker imports every API model handler at load time, so the venv has the full dependency set plus `soundfile`.
- 2026-11-17: Smoke-run bug fixed before any full run: the function-name locator took the first word of prose outputs as the function name. It now takes the first identifier followed by `(` (or a JSON `"function"` value). Only the 24 smoke rows were affected.
- 2026-11-17: Scoring config `qwen3-8b` (a BFCL prompting config with `underscore_to_dot=False`); the first choice, `Qwen/Qwen2.5-7B-Instruct`, is not in this version's config table.
- 2026-11-17: Scorer validation: 790/800 rendered gold calls pass; the 10 failures come from rendering only the first acceptable value per parameter, not from the checker.
- 2026-11-18: Harness sanity check passed. Dream CF on 100 `live_simple` items with JSON output (A6000) scored 77/100 AST-correct (14 argument errors, 9 wrong call counts, 0 parse errors), above the 50% inspection threshold and the team's ~64% reference. No harness fix was needed.
- 2026-11-18: Observation from LLaDA's original-schema block (2,400 decodes), not a fix. 620 are AST-correct (CF 50.5%, L2R 41.2%, random 18.7%, R2L 7.2%). Most errors are parse errors (L2R 30%, R2L 64%). Inspected L2R parse errors are genuine format failures: JSON-style `["name", {args}]` lists instead of Python call syntax, or a trailing period after the call. Under the preregistered no-repair rule they stay parse errors.
- 2026-11-18: Analysis code fix. `import statsmodels.api` fails under pandas 3.0.2 (statsmodels.tsa calls `deprecate_kwarg` with an old signature). `fn_rank_models` now imports `BinomialBayesMixedGLM`, `GEE`, `families` and `cov_struct` directly from `statsmodels.genmod`. The models and formulas are unchanged. Impact: none on results; the first analysis call crashed before writing anything.
