# Phase 1 masked diffusion pilot findings

This pilot asked a narrow question: **does the order in which a masked diffusion language model fills two answer fields change whether it gets them right?** It also tested whether putting a value into the first field changes the second field's answer. The larger project concerns structured outputs such as tool calls, where one field may help determine another. A small lookup task lets us test that idea with a known correct answer and a known path between fields before trying realistic tool calls.

Both LLaDA-8B-Instruct and Dream-v0-Instruct-7B showed large effects on the controlled lookup task. The results indicate that a committed or prefilled value can affect another field. The pilot did **not** produce a configuration ready to carry into Exp 4: both models failed the preset quality gate because they often missed field B even when B was directly available in the table. The [full report](../results/phase1/report.md) contains every accuracy cell, paired count, and confidence interval.

The three experiments had separate jobs:

| Experiment | What changed | Question it answered |
|---|---|---|
| Exp 1, copy | The decoding order | Can the models fill the two masks on a simple task? |
| Exp 2, lookup | The path to B and the decoding order | Does choosing A or B first change correctness, especially when A leads to B? |
| Exp 3, prefilled A | The value visible in A before B is predicted | Does correct, predicted, or wrong A change B's answer? |

## How masked diffusion answers this task

A conventional language model writes one token after another, usually from left to right. A masked diffusion language model can instead begin with several hidden positions, represented by mask tokens, and fill them in an order chosen by a decoder. At each step, the decoder runs the model on the whole current sequence and examines its predictions at the still-masked positions. Once it writes a token, that token stays fixed. The pilot changed this decoding procedure; it did not train or change the model weights.

Here the model was given the JSON structure and asked to fill only two one-token values:

```json
{"a":"<MASK>","b":"<MASK>"}
```

`<MASK>` is readable notation here; each run used its model's actual special mask token. The masks stand for the *values* inside the quotes; the model did not have to generate the braces, field names, or punctuation. We call the value in `a` **A** and the value in `b` **B**. A was always to the left of B in the answer. A **commitment** is the moment the decoder replaces one mask with a token and leaves it there. The decoder used one of three orders:

| Order | First commitment | Second commitment |
|---|---|---|
| A-first | Write the model's best token for A | Predict B again with A visible |
| B-first | Write the model's best token for B | Predict A again with B visible |
| Confidence-first (CF) | Write whichever field has the higher top-token probability | Predict the remaining field again |

A-first and B-first therefore use the same initial prompt and the same number of model passes; the difference is which prediction becomes permanent first. CF also uses two passes. Its "confidence" is the probability assigned to each field's most likely token at the initial step, not the probability that the answer is correct. Predictions were greedy over the model's **full vocabulary**, excluding only the mask token. The decoder did not restrict answers to words in the tables. Exact confidence ties were broken with a seeded random choice.

Imagine, schematically, that the first model pass favors A=`paper` and B=`glass`, while the correct B is `metal`. A-first writes `paper` and asks the model again; B can change to `metal`. B-first writes `glass` first, so B remains `glass` even if A is later filled correctly. This example explains why order can change the final answer without changing the prompt or pass count. A commitment can also hurt if the first value is wrong. The experiment measures these effects; it does not assume that the model follows a particular reasoning process.

## What the models had to look up

Each **lookup prompt** contained an **anchor table** and a **mapping table**, each with 4, 8, or 16 rows. A **source** was the underlying set of randomly paired values and one target key from which the three prompt conditions were made. The target key identified the row whose A and B had to be returned. Each row also had an auxiliary value, **H**. H was visible in the anchor table but never requested in the JSON output. The same underlying rows and target were used to create three conditions:

| Condition | Where A comes from | How B can be found |
|---|---|---|
| Direct | The target row | Read B in the target row |
| Shared-path | The target row | Find the mapping from that A to B |
| Separate-path | The target row | Find the mapping from that row's H to B |

Here is one target row shown schematically. Only the relevant row from each table is shown; real prompts also contained distractor rows, and the tables were shuffled independently. The example words are illustrative, not a copied trace.

```text
Target key: k07                     Required answer: {"a":"paper","b":"metal"}

Direct anchor:     k07 paper river metal    B is in the anchor row.
Direct mapping:    stone willow             Its keys match nothing in the anchor.

Shared anchor:     k07 paper river cloud    The last value is filler.
Shared mapping:    paper metal              A leads to B.

Separate anchor:   k07 paper river cloud    The last value is filler.
Separate mapping: river metal              H leads to B; A does not.
```

The actual prompt labeled the anchor columns and mapping columns, supplied a target key, and requested only the JSON answer. The Direct mapping table was inert; its keys were absent from the anchor. Filler values kept the conditions comparable in length. This matters because a shorter or missing second table could make one condition easier for reasons unrelated to the dependency being tested.

This comparison matters because A is on the path to B only in Shared-path. If filling A first helps B much more there than in Separate-path, that pattern is consistent with a dependency between the fields. Direct serves as a simpler control: B is already in the target row. The tables had the same number of rows and matched token lengths across conditions. An audit of all 600 sources per model found zero token-length mismatches. Every value was one token for its model's tokenizer in the output and table contexts, and each source used distinct values. The word pool was chosen separately for the two tokenizers; a "word" can occupy different numbers of tokens in different models.

Each model saw 200 sources at each table size. Within one source and condition, the prompt was identical for A-first, B-first, and CF. Conditions intentionally changed where B appeared, but reused the same target A and B. A **run** was one source under one condition and one order, recorded as one trace row. That gives 200 sources × 3 sizes × 3 conditions × 3 orders = **5,400 Exp 2 runs per model**. Exp 3 reused the Shared-path and Separate-path sources; no instance was removed because a model got it wrong.

## Why the pilot began with a copy test

Before the lookup task, Exp 1 simply asked the models to copy two visible values into A and B. It had 20 instances under each order. This checked that masks, token positions, prompts, and decoding worked on a simple task before interpreting harder results.

LLaDA copied both fields correctly in **20/20 instances under every order**. Dream reached at least **19/20 for each field and order**. Both passed the preset G1 minimum of 95%. Both also passed the earlier G0 checks for one-mask recovery, tokenization, determinism, immutable commitments, batching agreement, memory, speed, and task integrity.

Passing a copy test does not establish that the lookup tables are easy. It does make a basic mask-position or output-format failure a less likely explanation for the later low scores.

## What the three gates meant

A **gate** is a pass condition set before looking at the results it governs. The three gates answered different questions. A model could finish all planned experiments even if the last gate failed.

| Gate | Question answered | Result for both models |
|---|---|---|
| G0, before Exp 1 | Are token positions, decoding, repeatability, task construction, speed, and memory ready for a run? | Pass |
| G1, after Exp 1 | Can each field be copied at least 95% of the time under every order? | Pass |
| G2, after Exp 2 | Is the lookup task calibrated well enough to select a configuration for a later study? | Fail at sizes 4, 8, and 16 |

G2 was set before the lookup results were examined. At each size it required Direct B accuracy of at least 90% under **every** order. Each path condition, averaged over orders, needed a B accuracy below 90% with even the lower end of its 95% interval above chance. Each condition also needed at least 20 sources whose full-answer correctness differed between A-first and B-first. A G2 failure was a finding to record; the plan explicitly continued to Exp 3. Thus **"complete" means the experiments and checks finished**, not that every gate passed.

## How to read the accuracy and paired comparisons

Each Exp 2 table cell contains 200 runs, one per source. **A accuracy** is the share with the right A; **B accuracy** is the share with the right B; **full-answer accuracy** requires both values to be right in the same run. For example, 75.5% B accuracy means 151 of the 200 B values were correct. A model can have high A accuracy and low full-answer accuracy if B is often wrong.

A paired comparison takes the same source under two orders and asks what changed. The reported A-first minus B-first gap is a difference in **percentage points**, not a percent increase over B-first. Bracketed 95% intervals come from 10,000 resamples of whole sources, preserving the A-first, B-first, CF, and condition results belonging to each source. They summarize variation across these constructed sources. The exact McNemar test uses sources where only one of the two fixed orders got the full answer right; it tests whether those disagreements favor one order.

## What changing the order did in Exp 2

The clearest order effect appeared in Shared-path. The table below shows **B accuracy** when A was committed first versus when B was committed first. A percentage-point gap is the simple subtraction of those two accuracies; for example, 75.5% minus 32.0% is 43.5 points. Brackets are 95% intervals from paired resampling of sources.

| Model | Rows per table | Shared-path A-first B | Shared-path B-first B | A-first advantage |
|---|---:|---:|---:|---:|
| LLaDA | 4 | 74.5% | 47.0% | 27.5 points [20.0, 35.0] |
| LLaDA | 8 | 75.5% | 32.0% | 43.5 points [36.0, 51.0] |
| LLaDA | 16 | 49.5% | 11.5% | 38.0 points [31.0, 45.0] |
| Dream | 4 | 73.0% | 42.0% | 31.0 points [24.0, 38.0] |
| Dream | 8 | 78.0% | 43.5% | 34.5 points [27.5, 41.5] |
| Dream | 16 | 71.0% | 32.5% | 38.5 points [31.5, 46.0] |

The advantage was larger in Shared-path than in Separate-path at every size for both models. At size 8, the difference between those two order gaps was **43.0 points** for LLaDA (95% interval **33.5 to 52.5**) and **20.0 points** for Dream (**10.0 to 30.0**). That comparison is more informative than the Shared-path gap alone, because Separate-path gives A a similar output position without making A the route to B.

The paired full-answer counts tell the same story. On LLaDA's size-8 Shared-path sources, **92** answers were right only with A-first, versus **5** right only with B-first. On Dream's size-8 sources, the corresponding counts were **73** versus **1**. These are comparisons of the same 200 sources under the two orders, rather than comparisons of unrelated question sets. The full report gives the exact McNemar tests and all other paired counts.

CF usually favored A at the first step, especially on Dream. Among size-8 Shared-path sources where exactly one fixed order got both fields right, CF chose that order's first field in **68/97** cases for LLaDA and **70/74** for Dream. CF did not consistently match A-first's final B accuracy because it sometimes committed B first. Its choice is based on the model's confidence at step zero, and confidence is not a guarantee that the first commitment will be correct or helpful. The report notes that the step-zero confidence ranking predicted CF's first field in every run; that agreement is automatic because the ranking *defines* CF's choice. Since A was always left of B, this pilot cannot tell whether CF favored A because of a learned dependency, its position, or both.

## Why the easy control failed its gate

The planned G2 gate required Direct B accuracy of at least **90% under every order** at a table size. It also required useful path-task difficulty and at least 20 paired order disagreements per condition. If B were guessed uniformly from *n* rows, chance accuracy would be 1/*n*: **25%** for four rows, **12.5%** for eight, and **6.25%** for sixteen. The path conditions had to be clearly above that chance level while remaining below about 90%. **Neither model passed G2 at any table size.** The decisive problem was Direct B: across models, sizes, and orders, its accuracy ranged from **23.0% to 79.5%**.

| Model | Rows per table | Direct B, A-first | Direct B, B-first | Direct B, CF |
|---|---:|---:|---:|---:|
| LLaDA | 4 | 23.0% | 58.5% | 32.5% |
| LLaDA | 8 | 28.5% | 69.5% | 36.5% |
| LLaDA | 16 | 24.0% | 59.5% | 25.0% |
| Dream | 4 | 33.0% | 59.0% | 37.5% |
| Dream | 8 | 36.5% | 63.0% | 42.0% |
| Dream | 16 | 39.5% | 79.5% | 47.5% |

Direct was meant to show that the model could perform an unambiguous lookup before using its path-task results to choose a future configuration. Instead, even B-first fell short of 90%. This is a real result under the frozen prompt and decoder, not a gate we changed after seeing the data. The pilot does not establish *why* Direct B was poor. The strong order sensitivity in Direct suggests that output context or table presentation may matter, but this study did not isolate either cause. LLaDA's Separate-path condition also had only **3** discordant full-answer pairs at size 8 and **0** at size 16, below the planned minimum of 20.

The problem was especially concentrated in B, not simply a failure to find the target row at all. At size 8 under A-first, LLaDA got Direct A right **91.5%** of the time but B right **28.5%**; Dream got A right **93.5%** but B right **36.5%**. Those figures do not identify the cause, but they explain why a strong Shared-path order effect cannot by itself validate this task as a clean dependency benchmark.

## What prefilled A did to B in Exp 3

Exp 3 reused the same source tables and target as Exp 2, but measured **only B's next prediction**. Before that B prediction, A was in one of four states:

| Branch | A as seen by the model when it predicts B |
|---|---|
| Masked | Still a mask |
| Gold | Filled with the target row's correct A |
| Predicted | Filled with the model's initial A prediction, whether right or wrong |
| Wrong | Filled with A from a seeded, non-target row |

B was decoded with the same rule and the same number of **B forward passes** in every branch. The Predicted branch also needed a preliminary A prediction to obtain the value it would insert. The key accuracy comparison is each branch against **Masked**, which shows what changed when A was supplied. Gold beating Wrong alone would be ambiguous, because Wrong could actively pull B toward an incorrect mapping.

Gold A improved B accuracy over Masked A substantially in Shared-path. The effect was smaller, near zero, or negative in Separate-path:

| Model | Rows per table | Shared-path Gold minus Masked | Separate-path Gold minus Masked |
|---|---:|---:|---:|
| LLaDA | 4 | +37.0 points [30.0, 44.0] | -1.5 points [-7.0, 4.0] |
| LLaDA | 8 | +46.0 points [39.0, 53.5] | -16.5 points [-22.0, -11.5] |
| LLaDA | 16 | +40.0 points [33.0, 47.0] | -2.5 points [-5.0, -0.5] |
| Dream | 4 | +32.5 points [25.5, 39.5] | +0.5 points [-6.0, 7.0] |
| Dream | 8 | +36.0 points [29.5, 42.5] | +5.0 points [-2.0, 12.0] |
| Dream | 16 | +40.5 points [33.5, 47.5] | -3.0 points [-9.0, 3.0] |

For a concrete reading of one row: in LLaDA's size-8 Shared-path condition, B was correct in **32.0%** of Masked runs and **78.0%** of Gold runs. That is the **46.0-point** gap in the table. Predicted reached **75.5%**, while Wrong reached **0%** for target B. Each percentage uses the same 200 sources. In Separate-path at that size, Gold reduced LLaDA's B accuracy from **18.0%** to **1.5%**. The pilot measures that response but does not establish why the unrelated A value had that effect.

Putting the model's own initial A prediction into the field also improved Shared-path B accuracy: by **27.5 to 43.5 points** for LLaDA and **31.0 to 38.5 points** for Dream, depending on table size. This is the operationally relevant branch because a decoder normally has its own prediction, not an oracle's gold value. It does not make Exp 3 a fair comparison of complete decoding methods: Exp 3 measures B's response in a fixed context, and obtaining Predicted A requires an initial A pass.

The Wrong branch tested where a misleading value sends the model. If the wrong A came from row *j*, that row's B was recorded as the **alternative answer**. Shared-path has a mapping from that wrong A to the alternative B. Separate-path does not, so matching that same alternative is a baseline for comparison. At table size 16:

| Model | Wrong branch B equals alternative in Shared-path | Same match in Separate-path | Difference |
|---|---:|---:|---:|
| LLaDA | 185/200 (92.5%) | 7/200 (3.5%) | 89.0 points [84.5, 93.0] |
| Dream | 178/200 (89.0%) | 56/200 (28.0%) | 61.0 points [54.0, 67.5] |

This is strong evidence that the filled A value can steer B along the available A-to-B mapping. It also shows a risk: committing a wrong A can propagate the wrong linked B. The Separate-path baseline is not always zero, so the difference between conditions matters more than the Shared-path match rate alone.

## What the pilot supports and what remains open

The results support three conclusions at different levels of certainty:

1. **Commitment order changed accuracy in this task.** The same sources often had different answers under A-first and B-first, most clearly in Shared-path. Direct also changed substantially with order, so order effects are not unique to a dependency path.
2. **A value placed in A changed B's response in these prompts.** Gold, Predicted, and Wrong A values produced different B responses. The Wrong branch often followed the wrong A's mapping in Shared-path. This supports a conditional-response mechanism, without identifying the model's hidden reasoning steps.
3. **CF's ability to recognize a prerequisite remains unproven.** A was always the left field, and the Direct control failed its accuracy gate. CF's preference for A could mix dependency information with position or other prompt effects.

They do not yet support choosing an Exp 4 configuration. Direct B failed the preset 90% gate at every size, so there is no calibrated easy control. A stayed left of B throughout Phase 1, so order effects are still entangled with field position. The task used synthetic single-token values and only two output fields; it says nothing by itself about real tool calls, longer fields, or general performance on other prompts. The 95% intervals resample these sources 10,000 times; they describe uncertainty across similar sampled sources, not uncertainty across new models or task designs. Phase 1 sources should stay out of any final test set.

Exp 4 was intended to change field position and role, which could help separate a preference for the left field from a preference for a prerequisite field. It was **not run** in this pilot. No real tool-call benchmark, multi-token field study, or training was run either. The results describe these fixed prompts, two model revisions, and one deterministic decoding setup; they do not identify the models' internal reasoning steps.

The current recommendation is **to lock no configuration for Exp 4 yet, pending human review**. A next study should first make the Direct lookup reliably solvable under a fixed, documented prompt, then test whether the Shared-path effect survives changes in A/B position and role. Changing this pilot's prompt now and selecting the better-looking result would break the frozen comparison; any revised setup should be treated as a new experiment.

## How the runs were checked

The models used their own chat templates, mask tokens, and pinned model revisions. The decoder ran full forward passes in bf16 without a key-value cache. Dream's released generation code shifts logits by one position before scoring masks, so the Dream decoder followed that interface; this was resolved during G0, before Dream's Exp 1. The decoder, task configuration, and thresholds were frozen before Exp 2. A later report-only bug fix did not change model traces. No experimental run was discarded or repeated to raise an accuracy score.

Both models produced the planned **60 Exp 1, 5,400 Exp 2, and 4,800 Exp 3 trace rows**, with no duplicate run IDs. A separate scorer reconstructed the correct target from the saved value pool and seed for 20 randomly selected rows in each experiment and model, 120 rows total; all passed. Regenerating the report from the traces reproduced it byte for byte. These checks support the integrity of the recorded comparison, while the failed G2 gate remains part of the scientific result.

## Where to find the underlying work

The [full results report](../results/phase1/report.md) has all cells, paired tests, step-zero confidence summaries, and deviations. The [preregistration](../results/phase1/PREREG.md) records the thresholds and planned analyses; [decisions](../results/phase1/DECISIONS.md) records implementation choices and fixes. The [trace files](../results/phase1/traces/) contain one JSONL row per run. Model revisions and seeds are in [config.yaml](../phase1/config.yaml).
