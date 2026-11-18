# Code audit before Phase 1.5

Audited at commit `03a4017` (branch `phase1-pilot`) on 2026-11-17. No existing file was edited. The audit added only this file and `audit/`, which holds the scripts and raw outputs behind each claim.

## Top findings

1. **Direct B fails on column choice, not row retrieval.** When Direct B is wrong, the answer is almost always the **target row's H**. That is the value immediately left of B in the anchor row, and the B column is labeled `value`, not `b`. Under A-first, this accounts for 426 of 449 LLaDA errors and 267 of 382 Dream errors. Distractor-row B values account for essentially none (`audit/results/direct_b_errors.txt`). A-first makes it worse: after `"a":"<A>"` is committed, the model continues the row to H. This points Phase 1.5 at hypotheses (a), the column label, and (b), the explicit row format.
2. **Results are not reproducible across GPU types.** Phase 1 ran on A6000s, and rosetta15 has A100s. When I replayed 10 Phase 1 rows with unchanged code, 2 committed different tokens. Both were near-ties: in one, CF confidences of 0.599 and 0.609 swapped which field went first. Step-0 probabilities drifted by as much as 0.054. Reruns on the same host were identical.
3. **The decoder covers only the Phase 1 toy task.** It masks two value slots inside a prefilled JSON scaffold. There is no full canvas, no EOS or padding, no L2R, R2L or random orders, and no PF or DF. **Order names it does not recognize silently become B-first.**
4. **Running the Phase 1 code again would mix data with Phase 1.** `run.py` appends to `results/phase1/traces/` and skips rows by `run_id`, and `g0.py` overwrites `results/phase1/G0-*.json`. Neither has any way to exclude Phase 1 sources.
5. **The pipeline has no RQ1 analysis yet.** There is no rank normalization and no mixed-effects model, and `statsmodels` is not installed.

## 1. Repo map

| Path | What it does |
|---|---|
| `phase1/config.yaml` | Seeds (task and tie seed 1729, bootstrap seed 7331), pinned revisions, sizes, gate thresholds, and exact prompt and output templates |
| `phase1/decoder.py` | `render` builds chat template + prompt + `{"a":"<MASK>","b":"<MASK>"}` and finds the slots. `aligned` checks that the filled and masked versions tokenize identically. `slot_logits` applies Dream's shift. `decode` runs the one-commit-per-pass loop |
| `phase1/tasks.py` | `pool` and `usable_pool` build the single-token word pool. `make_source` builds rows with keys q, A, H, B, C, D and E. `tables` renders Direct, Shared-path and Separate-path tables. `integrity` checks that the answer is unique |
| `phase1/run.py` | Entry point for Exp 1, 2 and 3. Loads the model (bf16, pinned weights), generates runs, and appends resumable JSONL traces |
| `phase1/supervise.py` | One process per model: runs Exp 1, then G1, then Exp 2 and 3, restarting on hangs or crashes |
| `phase1/g0.py` | G0 gate: copy recovery, determinism, immutability, batched vs. single decisions, and timing |
| `phase1/analyze.py` | Builds `report.md`: accuracies, source-clustered bootstrap, paired gaps, interactions, McNemar, G2, and the Exp 4 recommendation |
| `phase1/rescore.py` | Separate scorer that rebuilds 20 targets per experiment from seeds and checks them against the traces |
| `phase1/audit_tasks.py`, `export_words.py`, `download.py` | Prompt-length audit across conditions, word-pool export, and weight download |
| `phase1/tests/` | 3 tests: the Dream shift, that logit drift doesn't change decisions, and that report sections are present |
| `results/phase1/` | PREREG, DECISIONS, STATE, report, gate JSONs, and traces and logs (gitignored, present on disk) |
| `weights/` | Local snapshots. Dream's `generation_utils.py` and `modeling_dream.py` were the reference for the shift and attention checks |
| `handoff_phase1.md` / `.txt`, `phase1_scope.md`, `docs/` | Planning docs. The `.md` and `.txt` handoffs are byte-identical |

**How to run** (from the repo root, on a GPU host such as rosetta15):
- G0: `python -m phase1.g0 --model llada --gpu 0`
- Everything in Phase 1: `python -m phase1.supervise --model llada --gpu 0 --sources 200`
- One experiment: `python -m phase1.run --model llada --gpu 0 --exp 2`
- Report: `python -m phase1.analyze`
- Tests: `.venv/bin/python -m pytest phase1/tests`

Do not rerun any of these as-is (see risk H1).

## 2. Decoder vs. spec

| Item | Status | Evidence |
|---|---|---|
| One commit per forward pass; committed tokens never rewritten | **Pass** | `decoder.py:41-58`: one forward pass per loop iteration (`:42`) and one write (`:56`). Committed slots are removed from `remaining` (`:58`), and only `remaining` positions are ever written |
| Full-vocabulary greedy, excluding only the mask token | **Pass** | `decoder.py:45-48`. Softmax runs in fp32 over the full vocabulary with `z[mask_id]=-inf` |
| CF confidence only over masked value slots | **Pass** | `decoder.py:44,50-51`. Only value slots are ever masked |
| Seeded tie-breaking | **Pass** (with a caveat) | `decoder.py:38,51-53`. Seed is `seed+sid+size*1000` (`run.py:40`). Ties require exact float equality, and near-ties are not flagged (see finding 2) |
| No KV cache; bf16 | **Pass** | `decoder.py:28` (`use_cache=False`), `run.py:18` (`torch_dtype=bfloat16`) |
| Each model's own mask token and chat template | **Pass** | `run.py:19` (`config.mask_token_id`: LLaDA 126336, Dream 151666), `decoder.py:7` (`apply_chat_template`, generation prompt) |
| Dream one-position logit shift; none for LLaDA | **Pass** | `decoder.py:29-31` matches `weights/Dream-v0-Instruct-7B/generation_utils.py:412`, and `tests/test_dream_shift.py` covers it. Dream's attention is bidirectional with no mask (`modeling_dream.py:430`, `is_causal=False`). Dream is forced onto math SDPA (`run.py:12-15`) |
| Whole canvas as one block | **Partial** | There are no semi-AR blocks, but there is no generation canvas either. The JSON scaffold is prefilled and only 2 slots are masked (`decoder.py:8`) |
| EOS and padding handling | **Fail (missing)** | No EOS or pad positions after the output, and nothing crops on EOS. The canvas ends at `}` with no end-of-turn token |
| Commit ranks logged for every token | **Partial** | `steps` (`decoder.py:57`) records the order, token and probability for each committed slot. It has no explicit position or rank field. Top-5 is logged at step 0 only (`:49`), and there is no CF margin |
| Order names validated | **Fail** | `decoder.py:54`: any order other than `CF` or `A-first` becomes B-first, so `L2R` would silently run as B-first |

## 3. Task generator

| Item | Status | Evidence |
|---|---|---|
| Single token in output context | **Pass** | `tasks.py:52-58` with `decoder.aligned` |
| Single token in table context | **Pass** | Checked on the real tokenized prompts for all 600 sources × 3 conditions: 0 failures out of about 84.5k value occurrences per model (`audit/results/table_context_tokens.txt`). Before this audit, this was assumed from encoding `' '+word` in isolation (`tasks.py:10`) |
| Token lengths matched across conditions | **Pass** | The same number of words by construction (`tasks.py:32-40`), and `task_audit.json` found 0 mismatches |
| Tables shuffled independently | **Pass** | `tasks.py:31`: anchor and mapping get separate permutations, and the seed differs per condition (`:30`). So the target row's position also differs across conditions for the same source |
| Seeds reproducible | **Pass** | The regenerated pool equals the Phase 1 export on rosetta15 for both models, and same-host reruns are identical |
| Phase 1 sources can be excluded | **Fail** | A source is identified only by (seed, size, source_id), so the same config regenerates the Phase 1 sources exactly |
| Prompt words reused as values | **Risk** | 17 words from the prompt (`value`, `key`, `left`, `right`, `target`, `the`, …) are in the pool. 118 of 600 LLaDA sources and 97 of 600 Dream sources contain one. Any difference in accuracy is confounded with table size, so this is a risk to remove, not a measured effect |
| Role swap (query direction) | **Missing** | A is always the prerequisite (`tasks.py:36-37,48`) |
| Layout swap (B left of A) | **Missing** | The output order is hard-coded (`decoder.py:8`, `config.yaml:23`) |
| One-hop controls matched to two-hop | **Missing** | Direct is a one-hop lookup, but it is not matched to the dependent field for RQ2 |
| Multi-token values with equal slot lengths | **Missing** | Values are single tokens throughout: the pool (`tasks.py:10`), `aligned` (`decoder.py:24`), `run.py:58`, and one position per field in `decode` |

## 4. Analysis

| Item | Status | Evidence |
|---|---|---|
| Paired bootstrap | **Pass** | `analyze.py:16-31`: per-source differences, 10k resamples clustered on (size, source), percentile intervals |
| Interaction contrasts | **Pass** | `analyze.py:33-42` |
| McNemar | **Pass** | `analyze.py:82`: exact two-sided binomial test on discordant **full-answer** pairs. There is no B-only McNemar and none for Exp 3 |
| G2 matches the prereg | **Pass** | `analyze.py:116-126` |
| Rank normalization over content tokens | **Missing** | With two fields, the only rank is `first_field` |
| Mixed-effects regression | **Missing** | `statsmodels` is not installed in `.venv` |
| Scoring strictness | **Risk** | Scoring compares decoded strings exactly (`run.py:63`). About 0.9% of Dream predictions (50 of 5,400 in Exp 2) are the gold word with a leading space and are counted wrong. LLaDA has 0 |

## 5. Tests and smoke run

- **Unit tests:** 3 out of 3 pass (`pytest phase1/tests`).
- **Smoke run:** I replayed 5 Phase 1 Exp 2 rows per model through the unmodified `make_row`, covering sizes 4, 8 and 16, all three conditions, and all three orders. Each model ran on its own GPU on rosetta15 (8× A100-PCIE-40GB), and outputs went only to `audit/results/`.

| | LLaDA | Dream |
|---|---|---|
| Model load (network FS, both loading at once) | 286 s | 280 s |
| First instance (warm-up) | 4.1 s | 3.6 s |
| Steady state, per 2-pass instance | 0.06–0.20 s | 0.10–0.12 s |
| Peak VRAM allocated / reserved | 16.2 / 16.3 GB | 15.5 / 15.9 GB |
| Same-host rerun identical | yes | yes |
| Commits match Phase 1 (A6000) traces | 4/5 | 4/5 |

The mismatches:
- `llada-e2-n16-s4-Shared-path-CF`: on the A6000, step-0 confidences were A 0.599 and B 0.609, so CF went B-first and committed A as `cot` (wrong). On the A100, CF went A-first and got A right.
- `dream-e2-n8-s1-Shared-path-A-first`: the second-step argmax flipped from `array` (0.395) to `fest`.

Loading dominates the cost. Weights fill less than half of a 40 GB card, so one resident model per GPU with data-parallel sharding is the natural layout.

## 6. Risks, by severity

**High**
- **H1.** Rerunning the Phase 1 code writes into Phase 1 records. Traces append to `results/phase1/traces/{model}-exp{n}.jsonl` and skip rows by `run_id` (`run.py:87-97`). `g0.py:67` overwrites the Phase 1 gate files. The config path is hard-coded (`run.py:9`). All new work needs its own modules and output directory.
- **H2.** Results depend on the GPU type, and CF is sensitive to near-ties. Trace rows don't record the host or GPU. Each experiment should be pinned to one GPU type, with the host and GPU written to every row and the CF margin logged. Phase 1 (A6000) numbers should not be compared head-to-head with new A100 runs. One option: replay all of Phase 1 Exp 2 on an A100 (about 10 minutes per model) to measure the flip rate.
- **H3.** Unknown order names silently become B-first (`decoder.py:54`).
- **H4.** There is no way to exclude Phase 1 sources, so they could leak into a final test set.

**Medium**
- **M1.** There is no full canvas, EOS or padding, so content-only ranks and BFCL can't be done.
- **M2.** Prompt words appear as table values in about 16–20% of sources.
- **M3.** Top-5 tokens are logged only at step 0. The Phase 1.5 diagnostic needs the top-5 at each commit.
- **M4.** Scoring counts leading-space variants as wrong (about 0.9% of Dream predictions).
- **M5.** No data parallelism: `supervise.py` uses one GPU per model. Batched vs. unbatched agreement was checked on a single prompt in G0, and only for decisions.

**Low**
- **L1.** `rescore.py` hard-codes seed 1729 and relative paths. That is fine for Phase 1, but it can't be reused.
- **L2.** The handoff `.md` and `.txt` files are duplicates.
- **L3.** The two-field run loop hides general multi-field bugs, such as `next(iter(remaining))` at `decoder.py:54`.

## 7. Missing pieces

- **RQ1:**
  - A multi-field task generator with a 2×2 role × layout design.
  - L2R, R2L and random (3 seeds) schedules.
  - A per-token log recording the position, field, role, whether it is content, and its rank.
  - Normalized rank over content tokens only.
  - A mixed-effects model of rank on role × position, with field-identity fixed effects and a random intercept per source. This needs `statsmodels`.
  - Bootstrap intervals clustered by source for every reported effect.
- **RQ2:**
  - PF and DF schedules (CF within each field).
  - Matched one-hop and two-hop tasks.
  - Multi-token values with equal slot lengths.
  - Dependent-field accuracy with paired PF−DF gaps, and the hop × order interaction.
- **BFCL:**
  - A loader for 400 balanced simple and multiple examples.
  - Reversing the schema parameter order.
  - A full canvas with a length budget and shared EOS cropping.
  - The official AST checker (pinned `bfcl-eval`).
  - Measures for parse validity, wrong-function errors and argument errors.
  - Function-name commit rank vs. wrong-function errors.

## 8. Proposed structure for the next phase

```
phase1/                      # frozen; no edits
dlm/                         # new shared library
  models.py                  # pinned load, bf16, own mask id, Dream shift + math SDPA
  canvas.py                  # chat template + prompt + masked spans (+EOS/pad tail); field→positions; content flags
  schedules.py               # L2R, R2L, random(seed), CF, PF, DF; unknown names raise
  decoder.py                 # 1 commit/pass; per-step log: pos, field, token, prob, top-5, CF margin
  scoring.py                 # field and full-answer accuracy; error taxonomy (target H, distractor B, non-table…)
  ranks.py                   # normalized content-token commit rank
  stats.py                   # cluster bootstrap, McNemar, mixed effects
  runner.py                  # data-parallel sharding over GPUs; resume by run_id; host/GPU in every row
tasks/
  lookup.py                  # row formats, column labels, role/layout swap, 1-hop/2-hop, multi-token values
  exclusion.py               # fingerprints of Phase 1 sources; new seeds; template-word filter
experiments/
  phase1_5/  config.yaml  PREREG_phase1_5.md  DECISIONS.md  run.py  analyze.py
  exp4/
  bfcl/
results/phase1_5/ ...        # separate from results/phase1
tests/                       # ports of the 3 Phase 1 tests + schedules, canvas, ranks, exclusion
```

Each new module would be tested before use against the frozen `phase1/` code. With the Phase 1 config and an A6000, it should reproduce the Phase 1 traces exactly.
