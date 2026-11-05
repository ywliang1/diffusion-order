# Phase 1 Scope: Overnight Order and Injection Pilot

**Goal:** find out whether commitment order and prefilled values affect answers on a tiny, fully controlled task, before spending time on the full study.

**Status:** planned, nothing has been run. Runtime figures are estimates from the proposal's cost formula, so replace them with the timing from the smoke test.

## Recommendation

- **Run tonight:** Exp 1, 2 and 3 on LLaDA-8B-Instruct and, if its code path is ready, Dream-7B-Instruct.
- **Run after review:** Exp 4. It is cheap enough for the same night, but it needs a human to lock the configuration from Exp 2 first.
- **Real constraint:** engineering, not GPUs. Budget about a day for the task generator, decoder and tests. Compute is about 1 GPU-hour, or about 5 with a 5× safety margin.

If Dream isn't ready, launch LLaDA alone. It still gives a complete Phase 1 result.

## Experiments

Each field is one token, so an order is just "which field first", and each run takes 2 forward passes. Orders: A-first, B-first and confidence-first (CF).

| Exp | Purpose | Conditions | Size | Passes per model |
|---|---|---|---|---|
| **1. Copy two values** | Validate the pipeline | 3 orders | 20 instances × 3 orders × 2 passes | 120 |
| **2. Single-token lookup** | Find workable difficulty; measure order effects | Direct, Shared-path, Separate-path × table size 4, 8, 16 × 3 orders | 200 sources × 3 × 3 × 3 × 2 passes | 10,800 |
| **3. Prefilled-field intervention** | Test whether a filled-in A changes B | Shared-path, Separate-path × Masked, Gold, Predicted, Wrong × table size 4, 8, 16 | 200 sources × 2 × 5 passes × 3 | 6,000 |
| **Total tonight** | | | | **16,920** (33,840 for both models) |
| *4. Swap role and layout (next run)* | Separate position from dependency | Role × layout × 3 task conditions × CF, PF, DF | 100 new sources × 2 × 2 × 3 × 3 orders × 2 passes | *7,200* |

Exp 2 and 3 use 200 sources rather than the 50 in the draft plan. The extra compute is trivial, and paired comparisons only gain information from instances where the two orders disagree. Exp 3 runs at all three table sizes so it doesn't have to wait for a config decision.

## Additions to the draft plan

Log these for every run:

- **Step-0 confidence and top-5 tokens for each field**, to separate "easier" from "dependency-related".
- **Whether B matches the link of the wrong A** in Exp 3. For Separate-path, compute the same match as a baseline.
- **Per-source outcome pairs:** both orders right, both wrong, only A-first right, only B-first right.
- **CF's first field and the tie-break used.** Fix a tie-break rule that doesn't favor the left field.

Randomize word pairings across sources, so real-world associations such as `red` and `oak` can't leak the answer.

## Resources

| Resource | Need | Notes |
|---|---|---|
| **GPUs** | 2 A6000s recommended, 1 is enough | One per model is simplest. All eight would only shorten an already short run. |
| **VRAM** | About 16 GB for model weights, plus batch memory | A 48 GB card should fit a batch of 32. Confirm in the smoke test. |
| **Disk** | About 30 GB for weights, under 1 GB for traces | Save top-k values, not full logits. |
| **People** | 1–2 for code, 1 for morning analysis | |
| **Software** | PyTorch, Transformers, released LLaDA and Dream code | Pin model revisions. Both models use custom inference code, so check their mask handling and interfaces first. |

### Runtime estimate

- **Per pass:** with about 400 prompt tokens, 20 output tokens and 8B parameters, the proposal's formula gives `2 × 8e9 × 420 ≈ 6.7e12` FLOPs. At the proposal's implied throughput of about 8e13 FLOPs/s, that is about 0.1 s.
- **Tonight:** 33,840 passes × 0.1 s ≈ 1 GPU-hour. With a 5× margin, about 5 GPU-hours.
- **Worst case for prompt length:** a 1,000-token prompt scales this by about 2.4×, which still fits overnight.
- **Exp 4 later:** 14,400 passes for both models, about 0.4 GPU-hours before any margin.

## Gates

These thresholds are suggestions. Finalize them before launch.

| Gate | When | Pass condition | If it fails |
|---|---|---|---|
| **G0: Before launch** | Smoke test | Single-mask recovery works; reruns give identical traces; committed tokens never change; batched and single runs match; values are exactly 1 token in context; at least 200 usable values per model; speed fits the night | Don't launch |
| **G1: Exp 1** | Automatic at start of run | At least 95% accuracy per field under every order | Abort the run and debug the template or decoder |
| **G2: Exp 2** | Morning | Direct at least 90%; B accuracy on a path condition is clearly above chance (1 / table size) and below about 90%; at least 20 discordant pairs per condition | See below |

## Reading the results

| Morning result | Meaning | Next step |
|---|---|---|
| Direct is high but both path conditions sit near chance | The two-hop task is too hard | Try smaller tables, a clearer prompt, or an autoregressive baseline |
| All conditions are near ceiling | The task is too easy | Use larger tables |
| Few discordant pairs | Order barely changes answers | Treat the order direction as weak, and look at Exp 3 before continuing |
| A-first beats B-first more on Shared-path than Separate-path | Evidence that the benefit relates to the shared path | Lock the config and run Exp 4 |
| Gold beats Masked, but Predicted doesn't | The model's own A is too unreliable to deliver the benefit | Study prerequisite accuracy before building a scheduler |
| Gold doesn't beat Masked | No sign yet that a filled-in A helps B | Don't claim a scheduling benefit |
| B follows the wrong A on Shared-path more than the Separate-path baseline | Filled-in values propagate through the path | Strong support for the mechanism behind H2 |

Gold beating Wrong does not show that the correct value helps. Always compare against Masked.

## Out of scope

- BFCL and the schema-guided method
- Multi-token fields and mean-rank analysis
- Single-block decoding on free-form output
- Claims about the final test set. Keep Phase 1 sources separate, and treat results as evidence of promise.

## Run setup

- Run under `tmux` or a job scheduler, with one model per GPU.
- Write one JSONL file per shard, so an interrupted run can resume.
- Record the seed, model revision, code commit, table size, condition and order on every row.
- Run G1 first and stop automatically if it fails.
- Do a 30-minute smoke test before leaving it unattended.

## Deliverables by morning

1. Trace files and a run log with actual GPU time and peak VRAM
2. Gate results for G0–G2
3. Accuracy table by model, condition, table size and order
4. Paired outcome counts for Exp 2, plus how often CF picks the successful order
5. Exp 3 branch comparisons, with paired bootstrap intervals
6. A recommendation on which configuration to lock for Exp 4

## Proposal impact

If Direct, Shared-path and Separate-path become the main design, update RQ2, H2 and Section 2, which all describe one-hop controls. The dataset count in the Evaluation section changes from 800 to 1,200.
