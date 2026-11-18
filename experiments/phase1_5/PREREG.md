# Phase 1.5 preregistration: making the Direct control solvable

Written and committed before any Phase 1.5 model output exists. This is a new experiment on fresh sources; Phase 1 is not modified or rerun.

## Goal and hypotheses

Phase 1's Direct control failed (Direct B 23–80% against a required 90%). Stage 0 showed that 58–97% of Direct B errors are the target row's H, the value next to B in a column labeled `value`. The model finds the row but takes the wrong column.

- **Primary:** at least one prompt format brings Direct B to at least 90% under A-first, B-first and CF for both models at table sizes 4 and 8, while Shared-path B stays at 40–80% (averaged over orders).
- **Secondary (descriptive):** under any passing format, the share of Direct B errors that are the target row's H drops below its Phase 1 level.

## Fixed setup

- **Models:** LLaDA-8B-Instruct `08b83a6feb34df1a6011b80c3c00c7563e963b07` and Dream-v0-Instruct-7B `05334cb9faaf763692dcf9d8737c642be2b2a6ae`, frozen, bf16, no KV cache.
- **Decoding:** the `dlm` stack, verified equal to Phase 1 on all 10,260 rows per model. One commit per forward pass; greedy over the full vocabulary except the mask token; batch size 1. CF ties are broken by `random.Random(seed + source_id + 1000 × size)`.
- **Hardware:** rosetta21, NVIDIA RTX A6000 only, through `scripts/env.sh`. If rosetta21 has no free GPUs, rosetta7 (also A6000) may be used, but one split never mixes hosts with different GPU types.
- **Output canvas:** `{"a":"<MASK>","b":"<MASK>"}` as the assistant continuation, A left of B, one token per value.

## Task

Each source has n rows with columns key (`k00`…), A, H, B, C, D, E. All 6n values are distinct words. One target row is queried.

| Condition | Anchor row's 4th column | Mapping table | Where b is found |
|---|---|---|---|
| Direct | B | D → E (filler) | target row, 4th column |
| Shared-path | C (filler) | A → B | mapping, keyed by the target's A |
| Separate-path | C (filler) | H → B | mapping, keyed by the target's H |

The anchor and mapping row orders are drawn once per source and shared by all conditions and variants. This differs from Phase 1, where each condition had its own shuffle; the change makes conditions and variants paired.

**Value pools (per tokenizer).** A word is eligible if it:
- matches `[a-z]{3,9}`;
- is one token bare, one token with a leading space, and its own token after `=` (as in `a=word`);
- aligns in both output slots, with and without the chat template;
- is not a prompt or template word, nor one of the model's chat-template words.

The pools hold 4,015 words (LLaDA) and 4,759 (Dream), saved as `results/phase1_5/pool-<model>.json`.

**Exclusion.** A source is redrawn from the same RNG stream if its unordered target pair {A, B} matches any Phase 1 source or copy instance, or its full value set matches a Phase 1 source (`tasks/exclusion.py`).

**Seeds.** Dev 15001, test 15002. Source RNG: `random.Random("lookup-<seed>-<size>-<source_id>")`.

## Prompt variants

Every prompt is:

```text
Read the tables and return only the JSON object. No explanation.
[V4 only] Fill field a from a column labeled a and field b from a column labeled b.
<tables>
Target key: <key>
Return only the JSON object with fields a and b; no explanation.
```

The tables, shown for a Direct target row (key k03, A needs, H ethyl, B ile):

| Variant | Anchor header and row | Mapping header and row |
|---|---|---|
| V1 | `Anchor (key a h b):` / `k03 needs ethyl ile` | `Mapping (d e):` / `<d> <e>` |
| V2 | `Anchor:` / `key=k03 \| a=needs \| h=ethyl \| b=ile` | `Mapping:` / `d=<d> \| e=<e>` |
| V3 | `Anchor:` / `key=k03 \| h=ethyl \| a=needs \| b=ile` | `Mapping:` / `d=<d> \| e=<e>` |
| V4 | as V1, plus the instruction line | as V1 |

On the path conditions the anchor's 4th label is `c`, and the mapping labels are `a b` (Shared-path) or `h b` (Separate-path). V4's instruction is therefore true in every condition. `-nochat` renders the same prompt without the chat template: BOS, the prompt, a newline, then the output.

**Task audit**, before every run and for every variant: every table value is exactly one token in the rendered prompt; prompt token length is equal across the three conditions; the target pair aligns; no source matches Phase 1. Dev audit: 0 failures for both models (`results/phase1_5/task_audit-dev.json`).

## Dev set (variant selection only)

- 100 sources per size, sizes 4, 8 and 16, seed 15001, the same sources for every variant.
- V1–V4 with the chat template; 3 conditions × A-first, B-first, CF. That is 10,800 rows per model.
- **V5 arm** (run after V1–V4 dev): the variant chosen by the rule below, or the closest variant if none passes, rendered `-nochat` on the same dev sources (2,700 rows per model).

### Gate (team decision B, 2026-11-17)

For each model and each size in {4, 8}; size 16 is reported but not gated:

1. **Direct:** B accuracy at least 90% under each of A-first, B-first and CF (point estimate).
2. **Shared-path:** B accuracy averaged over the three orders lies in [40%, 80%] (point estimate), and its source-clustered 95% lower bound exceeds 1/n.
3. **Separate-path:** B accuracy averaged over the three orders has a 95% lower bound above 1/n. Its value is reported, but it has no 40–80% band.

A variant passes if all criteria hold for both models at both gated sizes: 20 criteria in total.

### Selection rule

1. Among V1–V4 (with the chat template) that pass, take the first in the order **V1, V4, V2, V3** (smallest change first).
2. If one passes, it is frozen with the chat template. The V5 arm is reported but cannot change the choice.
3. If none passes, the **closest** variant is the one meeting the most of the 20 criteria. Ties go to the highest minimum Direct B over models, gated sizes and orders. If the closest variant's `-nochat` arm passes, it is frozen.
4. Otherwise no variant is frozen, **no test run happens**, and we report the closest variant and propose new variants.

The rule is implemented in `experiments/phase1_5/analyze.py` (`select`) and tested in `tests/test_phase1_5_select.py`.

## Test set (frozen variant only)

- 200 fresh sources per size, sizes 4, 8 and 16, seed 15002, with a task audit before running.
- **Exp 2 design:** 3 conditions × A-first, B-first, CF.
- **Exp 3 design**, as in Phase 1, on Shared-path and Separate-path: A's slot is predicted from the fully masked canvas (A-first, A only). B is then decoded with A held as Masked, Gold, Predicted (the model's own A) or Wrong (A of a seeded non-target row).
- Total: 10,200 rows per model.
- Test results never change the frozen variant. The gate is re-evaluated on test and reported whether it passes or not.

## Scoring and analysis

- A field is correct if its prediction, with leading and trailing whitespace stripped, equals the gold value. Raw strings are kept, and the number of answers whose correctness changes under this normalization is reported.
- **Error taxonomy for B:** correct · target row's H · target row's other value · another row's B · other table value · not in the tables.
- **Intervals:** 95% percentile bootstrap, 10,000 resamples, clustered by source, seed 7331.
- **Reported per model, variant, size, condition and order:**
  - A, B and both-correct accuracy;
  - paired A-first vs B-first outcomes on B with exact McNemar;
  - the A-first − B-first B gap and its Shared − Separate interaction;
  - mean step-0 top-1 probabilities;
  - how often CF commits A first;
  - the fraction of CF rows with any CF margin below 0.02.
- **Test only:**
  - Exp 3 Gold, Predicted and Wrong minus Masked on B;
  - the rate at which B equals the wrong row's B in the Wrong branch;
  - the Exp 3 taxonomy.
- **Smoke:** before the dev run, 5 V1 sources at size 4 per model (45 rows) run to `results/phase1_5_smoke/`. They are checked only for crashes and trace completeness and are excluded from every analysis.
- Every deviation goes in `experiments/phase1_5/DECISIONS.md`, dated, with its impact. No run is dropped or rerun to change accuracy.
