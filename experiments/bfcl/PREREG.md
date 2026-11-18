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
