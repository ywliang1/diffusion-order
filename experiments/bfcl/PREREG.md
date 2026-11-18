# BFCL preregistration: commitment order on single-turn Python tool calls

Written and committed before any full BFCL run. The only model outputs seen before this file are 12 smoke decodes per model (2 items), used to check the pipeline; they are excluded from analysis.

## Questions (realism check from the proposal)

On realistic single-turn calls, how do commitment orders affect parse validity, wrong-function errors and argument errors? Is the function name's commit rank associated with wrong-function errors? Does reversing the schema's parameter order change any of this?

## Data

- **bfcl-eval 2026.3.23**, BFCL v4 data shipped in the package. It runs in an isolated venv (`/data/rbg/users/linrui/venvs/bfcl-eval-2026.3.23`) because it pins numpy 1.26.
- **Test:** 200 `simple_python` items sampled with seed 4610, plus all 200 `multiple` items. IDs are in `results/bfcl/items_meta.json`.
- **Schema conditions:** original, and reversed. Reversed flips the order of each function's `properties` and its `required` list; names, types, descriptions and requiredness are unchanged.
- **Prompts** come from BFCL's own code: `load_dataset_entry` (with the Python 3 language hint) and `system_prompt_pre_processing_chat_model` with the default format (Python call syntax, JSON function docs, plaintext, classic style), wrapped in each model's chat template.
- **Dev (canvas length only):** 25 unused `simple_python` items plus 25 `live_multiple` items.

## Decoding

- **Canvas:** the chat-templated prompt followed by **64** masked tokens, with no scaffold. 64 is the smallest multiple of 8 that holds the dev 99th-percentile gold call plus an end token (LLaDA: 55.6 tokens; Dream: 53.6). On the test items, 99% of gold calls are at most 60 tokens.
- **Orders:** L2R, R2L, random-s0, random-s1, random-s2, CF. One commit per pass, greedy over the full vocabulary except the mask token, bf16, no KV cache, batch size 1, the whole canvas as one block.
- **Shared EOS cropping:** content is every canvas token before the first end token (LLaDA `<|eot_id|>`/`<|endoftext|>`, Dream `<|im_end|>`/`<|endoftext|>`).
- **No repair:** the content text goes unchanged into BFCL's `default_decode_ast_prompting`, which strips backticks and whitespace and adds missing outer brackets; that is BFCL's own behavior and nothing is added. Scoring uses `ast_checker` with the `qwen3-8b` config, whose only effect is to keep dotted function names unconverted.
- **Hardware:** rosetta21 RTX A6000; rosetta7 A6000 may be added. No A100s in this stage.

## Run priority (proposal cut order: schema reversal first, then Dream on BFCL)

1. LLaDA, original schema
2. Dream, original schema
3. LLaDA, reversed schema
4. Dream, reversed schema

Each block is 2,400 decodes, about 7 A6000 GPU-hours. A block not finished by the end of the session is reported as not run, never as partial results.

## Metrics, per model × schema × order

The three random seeds are averaged within an item before any comparison. All intervals are 95% bootstraps clustered by item (10,000 resamples, seed 7331).

- **Parse validity:** BFCL's decoder returns a list of calls.
- **AST accuracy**, overall and among parseable outputs.
- **Error classes:** parse error · wrong function (`wrong_func_name`) · wrong call count (`wrong_count`) · argument error (missing or unexpected parameter, type or value errors). Wrong-function and argument-error rates are reported over all items.
- **Contrasts:**
  - each order minus L2R on AST accuracy (paired by item);
  - reversed minus original schema, per order (paired by item);
  - simple vs multiple, descriptive.
- **EOS commit rank by order:** the normalized step (0–1 over all 64 steps) at which the first end token is committed, and the mean step of all non-content positions.
- **Function-name commit rank vs wrong-function errors (association only):** among parseable outputs with an identified called name, a logistic regression of wrong-function on the name's normalized content rank, with order as a fixed effect and a random intercept per item (statsmodels `BinomialBayesMixedGLM`, variational Bayes). A GEE logistic model with exchangeable within-item correlation is reported beside it. L2R and R2L fix the rank by construction, so the primary fit uses CF and random orders only.

## Harness sanity check

Dream, CF order, on 100 seeded `live_simple` items with BFCL's JSON output format (`ret_fmt=json`), same canvas. The team's reference figure is about 64% for Dream greedy on BFCL-Live JSON. If our accuracy is below 50%, the harness is inspected for bugs before the main analysis (prompt, template, cropping, decoding). Any fix is logged, and affected runs are rerun in full, never selectively.

## Addendum (2026-11-18): lenient-parse score and autoregressive reference

Written and committed before any lenient score was computed and before any Qwen output existed. The team requested both on 2026-11-18.

### Secondary lenient-parse score

The strict score above remains the primary result. The lenient score is a secondary result that separates format failures from wrong calls.

- **Rules:** fixed in `experiments/bfcl/lenient.py`, with tests in `tests/test_bfcl_lenient.py`. They apply to Python-format items only.
  - **L1:** keep the first balanced `[...]` segment, or else the first balanced `name(...)` call, and drop any prose or trailing characters around it.
  - **L2:** rewrite JSON-style call structures as Python calls: `["f", {args}]`, `{"name": "f", "arguments": {…}}`, and lists of either.
  - Nothing else is repaired: no quote, bracket, argument-name or value fixes.
- **Basis:** the rules were chosen from failure types already seen in LLaDA's strict-scored outputs (trailing periods; JSON-style `["name", {args}]` lists). No lenient score had been computed when they were written.
- **Scoring:** the rewritten text goes through the same `default_decode_ast_prompting` and `ast_checker` as the strict score. Outputs go to `results/bfcl/scores/<trace>-<model>-lenient.jsonl`.
- **Reported per model × schema × order:**
  - lenient AST accuracy;
  - the lenient − strict difference, paired by item, with CIs clustered by item;
  - the share of outputs the rules changed;
  - lenient error classes.
- **Interpretation:** the strict − lenient gap measures format failure. Order contrasts under the lenient score show whether the order effects survive once format failures are removed.

### Autoregressive reference: Qwen2.5-7B-Instruct

- **Model:** `Qwen/Qwen2.5-7B-Instruct` at revision `a09a35458c702b33eeacc393d103063234e8bc28` (`weights/Qwen2.5-7B-Instruct`; `experiments/bfcl/ar.py`).
- **Decoding:** greedy, bf16, batch size 1, at most 64 new tokens (the diffusion canvas length).
- **EOS crop:** content is everything before the first `<|im_end|>` or `<|endoftext|>`, as in the shared crop. No repair.
- **Inputs:** the same chat messages as the diffusion runs, on the same 400 test items × 2 schemas (800 generations). Also the 100-item `live_simple` JSON sanity set.
- **Scoring:** strict and lenient, as above.
- **Hardware:** rosetta15 A100-PCIE-40GB. The diffusion BFCL runs were on rosetta21 A6000s, which are now unavailable. The team asked for the reference to run on the same GPU type as the other new runs (the three-field stage, on A100s).
- **Reported:** AST accuracy and error classes per schema, and the reversed − original difference.
- **Interpretation:** Qwen is a different model with a different tokenizer, so this is a descriptive reference point for the diffusion models, not a paired order contrast. No hypothesis test is attached.
