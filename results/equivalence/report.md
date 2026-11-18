# Stage 0: equivalence and GPU-fallback cost

Code: branch `phase2`, commit `75a8918`. All rows run at batch size 1 with `scripts/env.sh`.

## Equivalence with Phase 1 (rosetta21, RTX A6000)

The new `dlm` stack replayed every Phase 1 row (Exp 1–3, 10,260 rows per model) with the Phase 1 config, sources, prompts and tie seeds.

| Model | Rows | Exact match | Same decisions | Max probability difference |
|---|---:|---:|---:|---:|
| LLaDA | 10,260 | 10,260 | 10,260 | 0 |
| Dream | 10,260 | 10,260 | 10,260 | 0 |

An exact match means the same committed (slot, token, probability) sequence, the same step-0 top-5 tokens and probabilities, the same raw predictions, the same first field and the same tie flag. rosetta21 runs driver 535 (CUDA 12.2); Phase 1 ran on a CUDA 12.4 driver. The replay took 7.5 min on 2 GPUs per model, with peak allocated VRAM of 16.2 GB (LLaDA) and 15.5 GB (Dream).

## Batched vs. unbatched decisions (rosetta21)

| Model | Instances × orders | Same decisions | Bit-identical probabilities | Verdict |
|---|---:|---:|---:|---|
| LLaDA | 50 × 3 | 149/150 | 0/150 | batch size 1 |
| Dream | 50 × 3 | 139/150 | 0/150 | batch size 1 |

The batch held the three orders of one instance: equal length, no padding. All later stages run at batch size 1 and get their parallelism from data-parallel sharding across GPUs.

## Cost of an A100 fallback (rosetta15, A100-PCIE-40GB)

This replays Phase 1 Exp 2 (5,400 rows per model) and compares each row with the original A6000 trace. A row's margin is the smallest decision margin over its steps on the A100: the token margin (top-1 minus top-2 token probability) and, where the schedule had a choice, the CF choice margin.

| Margin | LLaDA rows | LLaDA decision flips | LLaDA B correctness changed | Dream rows | Dream decision flips | Dream B correctness changed |
|---|---:|---:|---:|---:|---:|---:|
| < 0.01 | 138 | 41 (30%) | 19 | 306 | 90 (29%) | 43 |
| 0.01–0.02 | 73 | 21 (29%) | 8 | 256 | 44 (17%) | 28 |
| 0.02–0.05 | 332 | 41 (12%) | 18 | 590 | 77 (13%) | 34 |
| 0.05–0.10 | 549 | 24 (4.4%) | 14 | 691 | 33 (4.8%) | 17 |
| ≥ 0.10 | 4,308 | 3 (0.07%) | 3 | 3,557 | 17 (0.5%) | 8 |
| **All** | 5,400 | **130 (2.4%)** | 62 | 5,400 | **261 (4.8%)** | 130 |

- Flips are concentrated at small margins. Rows with margin < 0.02 are 3.9% (LLaDA) and 10.4% (Dream) of rows, but hold 48% and 51% of the flips.
- Aggregate accuracy barely moves. Across the 27 size × condition × order cells, B accuracy changes by at most 1.0 point for LLaDA (mean absolute change 0.4) and 1.3 points for Dream (mean 0.7). These are well inside the Phase 1 bootstrap intervals, which are about ±6 points.
- So an A100 fallback would leave cell-level conclusions intact but would not reproduce individual rows. Each stage therefore stays on one GPU type.
