# Handoff: Phase 1 Overnight Pilot

You are implementing and running a small research pilot on a remote GPU machine. This file is self-contained. Nothing has been built or run yet.

**You are running unattended.** No one will answer questions while you work. Carry out every step yourself until Exp 1, 2 and 3 are finished, following "Autonomous operation" below. Don't pause for approval, and don't end your turn while work remains.

## Objective

Test, on a tiny controlled task, whether commitment order and prefilled values affect the answers of masked diffusion language models.

Run **Exp 1–3 only**, on LLaDA-8B-Instruct and, if ready, Dream-7B-Instruct. Finish with traces, gate results and a report in `results/phase1/`.

**Background:** diffusion models fill masked positions in a flexible order. Confidence-first (CF) decoding commits the most confident masked position next. The project asks whether that order follows dependencies between tool-call fields, and whether order affects correctness.

## Hard constraints

- Do not run Exp 4, BFCL, multi-token fields or any training.
- Do not invent results or relax a gate to continue.
- Do not change gate thresholds after seeing Exp 2 or Exp 3 results.
- Do not constrain predictions to the candidate vocabulary. The only exclusion is the mask token.
- Do not drop instances based on correctness in any branch.
- Do not add experiments, or rerun anything to improve a result.
- Do not use more than 2 GPUs, or any GPU in use by others.
- Do not push, publish or upload anything. Make local commits only, on a branch named `phase1-pilot`, so that `code_commit` is meaningful. Create a local repository if none exists, and leave other branches alone.
- Do not use `sudo`, change system settings, or stop processes you didn't start. Install packages in a virtual environment only.
- Do not create accounts, accept licenses, or look for credentials beyond those already configured for this user.
- Do not print or store access tokens in logs, configs or reports.
- Do not redesign the study. Record each small implementation choice in `results/phase1/DECISIONS.md`. If a design requirement can't be met, treat it as a blocker.

## Autonomous operation

### Main loop

`results/phase1/STATE.md` is your source of truth. It records the current step, each model's status, the last check result and the next action. Read it at the start and after any restart, then resume from it.

```text
repeat until every model has a final status:
    read STATE.md
    pick the next unfinished step
    do it, then run that step's check
    if it passes: update STATE.md and continue
    if it fails: use the decision table below, then update STATE.md
```

The goal is to finish the planned experiments, not to raise a score. A weak, null or surprising result is still a valid result.

Run long jobs detached from your session, so they survive if you stop. While a job runs, check it every 15 minutes rather than ending your turn.

### Make these decisions yourself

| Situation | What to do |
|---|---|
| Bug or failed check | Find the root cause, fix it, add a regression test and rerun the check. Try up to 5 distinct fixes. |
| Job crashes | Resume from the traces. After 3 failed restarts of one shard, treat it as a bug. |
| Job is hung (no new rows for 30 minutes) | Stop your own process and resume it. |
| Out of GPU memory | Halve the batch size and rerun the batching check. |
| Network or download failure | Retry with backoff for up to 1 hour. |
| Requested GPUs are busy | Check every 10 minutes for up to 4 hours. If only one is free, run the models one after the other. |
| Low disk space | Delete only caches and partial files you created. |
| Projected compute over 8 hours | Reduce source count evenly, down to 50 per cell. If that's still too long, skip Dream. |
| Dream needs access you don't have, or isn't ready after 5 fixes or 4 hours of work | Mark Dream `skipped` and continue with LLaDA. |
| G2 fails | Record it and continue to Exp 3. It's a finding, not a reason to stop or retune. |

Log every decision in `DECISIONS.md`, with what happened, what you chose and why.

### Freeze before results

Before starting Exp 1, write `results/phase1/PREREG.md` and commit it. Include the config, seeds, prompt template, thresholds and planned analyses.

- **Before Exp 2 starts:** you may fix the prompt template or decoder, using only G0 and Exp 1 data.
- **After Exp 2 starts:** the code and config are frozen, except for bug fixes.
- **Bug fix after the freeze:** the bug must be shown by a test, trace or code inspection, not by accuracy looking wrong. If you investigate a surprising result and find no bug, the result stands.
- **After any such fix:** log an amendment in `PREREG.md`, move the affected traces to `results/phase1/invalid/`, and rerun everything the bug touched. Never delete traces, and never choose between valid runs by their results.

### Final status for each model

- **`complete`:** Exp 1–3 finished and the Definition of Done is met.
- **`skipped`:** Dream only, as allowed above.
- **`blocked`:** a blocker from "When to stop" remains after you tried the steps above.

## Step 1: Inspect the environment

Before writing code, check and record:

- GPU model, count, VRAM and current usage (`nvidia-smi`)
- Disk space, RAM, Python, PyTorch and CUDA versions
- Whether a job scheduler is in use
- Whether the models are already downloaded or need Hugging Face access

Budget about 30 GB of disk for weights and under 1 GB for traces.

Expected model repos, which you must verify before use:

- LLaDA: `ML-GSAI/LLaDA-8B-Instruct`
- Dream: `Dream-org/Dream-v0-Instruct-7B`

Both rely on custom remote code. Read that code before running it, pin exact model revisions, and read each model's mask token, attention-mask requirements and forward interface from its own code and config. Don't assume they match.

## Step 2: Build the code

Suggested layout:

```text
phase1/
  config.yaml        # seeds, thresholds, table sizes, model revisions
  words.py           # single-token value pools per tokenizer
  tasks.py           # instance generation
  decoder.py         # one-token decoding and branch logic
  run.py             # shard runner, with resume support
  analyze.py         # gates, tables and report
  tests/             # G0 checks
results/phase1/      # traces, logs, report
```

### Decoder

Use `bf16` (or the models' recommended precision), `eval()`, `torch.no_grad()` and no KV caching.

```text
x = prompt tokens + output template, with masks in the slots
while slots remain:
    run a full forward pass on x
    compute the softmax over the full vocabulary at each masked slot
    set the mask token's probability to zero
    choose a slot according to the order
    write that slot's argmax token into x
```

- **Orders:** `A-first`, `B-first` and `CF`.
- **CF rule:** choose the slot with the highest top-1 probability.
- **Ties:** break exact ties with a seeded random choice, never by position.
- **Prediction:** always greedy.
- **Committed tokens:** never change once written.

### Task definitions

Every value (`A`, `H`, `B`) must encode to exactly one token **in its template context**. For example, a value may merge with an adjacent quote. Test this with the real prompt and template, per tokenizer. Build a pool of at least 200 such values per model, and use each value at most once within a source. Randomize roles and pairings across sources. Avoid obviously related word pairs.

Keep prompts identical across orders, using each model's chat template. Ask for the answer only, with no reasoning text. Store the exact template in `config.yaml`. Keep field A left of field B throughout Phase 1.

**Exp 1: Copy two values**

```text
Input: a=red; b=oak
Output: {"a":"<MASK>","b":"<MASK>"}
```

Use 20 instances, with orders A-first, B-first and CF.

**Exp 2: Single-token lookup**

Each source has `n` latent rows `(q_i, A_i, H_i, B_i)` and one target row. Use short unique keys for `q_i`. `H` is an auxiliary value that never appears in the output. The same latent rows generate all three conditions, so targets are identical:

| Condition | Anchor table | Mapping table | Path to B |
|---|---|---|---|
| **Direct** | `q → A, H, B` | Inert table of the same size, with keys that match nothing in the anchor | Read directly |
| **Shared-path** | `q → A, H` | `A → B` | Through A |
| **Separate-path** | `q → A, H` | `H → B` | Through H, not A |

Never include both mapping tables. Shuffle each table's row order independently, using a seed. Match table sizes and token lengths across conditions.

Run 200 sources at table sizes 4, 8 and 16, under all 3 conditions and all 3 orders.

**Exp 3: Prefilled-field intervention**

Reuse the Exp 2 sources for Shared-path and Separate-path, at all three table sizes. Each branch decodes B only, with A held in the stated state:

| Branch | State of A |
|---|---|
| **Masked** | Left masked |
| **Gold** | Correct A prefilled |
| **Predicted** | Prefilled with the model's own A prediction from the initial state, right or wrong |
| **Wrong** | Prefilled with `A_j`, a seeded random non-target row |

For Wrong, record `B_j` as the alternative answer. For Shared-path it is the link of the wrong A. For Separate-path, `A_j` has no link, so use the same `B_j` as a baseline. Every branch uses the same B decoding rule and number of B forward passes.

### Trace schema

Write one JSONL row per run, with one file per shard. Each row includes:

```text
run_id, model, model_revision, code_commit, seed, experiment, source_id, table_size,
condition, order_or_branch, target_A, target_B, predicted_A, predicted_B, alternative_B,
A_correct, B_correct, both_correct, B_matches_alternative, first_field,
steps: [{slot, token, prob}], step0: {field: {top5_tokens, top5_probs}}, tie_broken
```

Save top-5 values only, not full logits. Runs must resume safely after interruption, without duplicates.

## Step 3: Pass G0 before launch

Do a smoke test on a small sample. Launch only if all of these pass:

| Check | Pass condition |
|---|---|
| Slot alignment | Masking one token of a known-correct filled template recovers it |
| Determinism | Repeated runs produce identical traces |
| Immutability | Committed tokens never change |
| Batching | Batched and single-run results match |
| Tokenization | Every value is exactly one token in context, with at least 200 usable values per model |
| Task integrity | Tests confirm one correct answer per instance and no leakage between mapping tables |
| Speed | Measured throughput fits the night |
| Memory | Peak VRAM leaves a safe margin at the chosen batch size |

If a check fails, follow the decision table. If only Dream can't be made ready, continue with LLaDA and note that in the report.

## Step 4: Launch

Run in `tmux` or a job scheduler, under a small supervisor script that restarts failed shards and resumes from the traces. Use one model per GPU. Expected size:

| Experiment | Passes per model |
|---|---|
| Exp 1 | 120 |
| Exp 2 | 10,800 |
| Exp 3 | 6,000 |
| **Total** | **16,920** |

The planning estimate is about 0.1 s per pass, or about 1 GPU-hour for both models. It's unverified, so use your smoke-test measurement. If the projected time is over 8 hours, follow the decision table.

Each model runs Exp 1, G1, Exp 2 and Exp 3 in that order, with no human review between them.

**G1 runs automatically after Exp 1.** It passes if field accuracy is at least 95% under every order. If it fails, stop that model's run, follow the decision table, then rerun G0 and Exp 1 before continuing.

## Step 5: Analyze and report

Write `results/phase1/report.md`, with results per model and table size:

1. **Run summary:** environment, model revisions, actual GPU time, peak VRAM, any failures and any deviations
2. **G2 result:** passes if Direct is at least 90%, B accuracy on a path condition is clearly above chance (1 / table size) and below about 90%, and each condition has at least 20 discordant pairs
3. **Exp 2:** A, B and full-answer accuracy by condition and order
4. **Exp 2 pairs:** both right, both wrong, only A-first right and only B-first right, with an exact McNemar test on discordant pairs. Include how often CF picked the successful order among discordant instances.
5. **Exp 2 interaction:** A-first minus B-first gap on Shared-path vs. Separate-path
6. **Exp 3:** B accuracy for Gold vs. Masked, Predicted vs. Masked and Wrong vs. Masked, plus the Shared-path vs. Separate-path difference in each gap
7. **Exp 3 propagation:** the rate at which B equals the alternative answer in the Wrong branch, Shared-path vs. Separate-path
8. **Step-0 confidence:** by field and condition, and how well it predicts CF's first field
9. **Recommendation:** which configuration, if any, to lock for Exp 4

Use paired bootstrap 95% intervals clustered by source (10,000 resamples).

### Interpretation limits

State these in the report:

- All Phase 1 fields keep A on the left, so CF's preference can't yet be separated from position. Exp 4 tests that.
- Gold beating Wrong does not show that the correct value helps. Compare against Masked.
- Exp 3 measures conditional response in a fixed context. It is not an equal-compute method comparison.
- Results are pilot evidence. Keep these sources out of any final test set.

## Definition of Done

Don't call the work finished until all of these are true:

- Row counts match the expected totals, or the reduced totals in `DECISIONS.md`, with no duplicate runs
- G0, G1 and G2 results are recorded for each model that ran
- Rerunning `analyze.py` from the traces reproduces `report.md`
- 20 randomly chosen trace rows per experiment rescore correctly with independent code
- The report includes the interpretation limits and every deviation
- `PREREG.md`, `DECISIONS.md` and `STATE.md` are complete
- Your jobs have stopped and their GPUs are free

## When to stop

These are the only reasons to stop early, and only after the decision table has been exhausted:

- LLaDA can't be accessed without a license or token you don't have
- No free GPU appears within 4 hours
- G0 or G1 still fails on LLaDA after 5 distinct fixes
- The custom model code conflicts with the one-token decoder
- A design requirement can't be met, such as fewer than 200 single-token values

If a blocker affects only one model, finish the other. Then write `results/phase1/BLOCKED.md` with what you tried, exactly what you need, and the command that resumes the work.

## Final message

Send this only when every model has a final status. End with:

- Each model's final status, plus the blocker and path to `BLOCKED.md` if there is one
- What ran, what didn't and any deviations
- G0, G1 and G2 status for each model
- The 3–5 most important findings, with counts and intervals
- Paths to `report.md`, `DECISIONS.md` and the traces
- Your Exp 4 recommendation, marked as awaiting human review
