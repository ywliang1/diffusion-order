# Phase 1 masked diffusion pilot findings

This pilot asked a narrow question: **does the order in which a masked diffusion language model fills two answer fields change whether it gets them right?** It also tested whether putting a value into the first field changes the second field's answer. Both LLaDA-8B-Instruct and Dream-v0-Instruct-7B showed large effects on the controlled lookup task. The pilot did **not** produce a configuration ready to carry into Exp 4: both models failed the preset quality gate because they often missed field B even when B was directly available in the table.

The results are useful as evidence that a committed or prefilled value can affect another field. They are not yet a clean demonstration that a confidence-based decoder has learned the correct dependency order. This guide explains the task and that distinction from the beginning. The [full report](../results/phase1/report.md) contains every accuracy cell, paired count, and confidence interval.

## How masked diffusion answers this task

A conventional language model writes one token after another, usually from left to right. A masked diffusion language model can instead begin with several hidden positions, represented by mask tokens, and fill them in an order chosen by a decoder. At each step, the decoder runs the model on the whole current sequence and examines its predictions at the still-masked positions. Once it writes a token, that token stays fixed.

Here the answer always had two one-token values in a JSON object:

```json
{"a":"<MASK>","b":"<MASK>"}
```

We call the value in `a` **A** and the value in `b` **B**. A was always to the left of B in the answer. The decoder used one of three orders:

| Order | First commitment | Second commitment |
|---|---|---|
| A-first | Write the model's best token for A | Predict B again with A visible |
| B-first | Write the model's best token for B | Predict A again with B visible |
| Confidence-first (CF) | Write whichever field has the higher top-token probability | Predict the remaining field again |

A-first and B-first therefore use the same initial prompt and the same number of model passes; the difference is which prediction becomes permanent first. CF also uses two passes. Predictions were greedy over the model's **full vocabulary**, excluding only the mask token. The decoder did not restrict answers to words in the tables. Exact confidence ties were broken with a seeded random choice.

A commitment can help when the first value is a useful clue for the second. It can also hurt if the first value is wrong, or if the model changes its prediction after seeing a filled position. The experiment measures those effects; it does not assume that the model follows a particular reasoning process.

## What the models had to look up

Each lookup source contained a table with 4, 8, or 16 keyed rows. A target key identified one row, and the required answer was that row's A and B. Each row also had a hidden auxiliary value, **H**, which never appeared in the output. The same underlying rows and target were used to create three conditions:

| Condition | Where A comes from | How B can be found |
|---|---|---|
| Direct | The target row | Read B in the target row |
| Shared-path | The target row | Find the mapping from that A to B |
| Separate-path | The target row | Find the mapping from that row's H to B |

For example, imagine the target row says `k07 → A=paper, H=river`. In Shared-path, a second table has `paper → metal`; in Separate-path, it has `river → metal`. Both call for `{"a":"paper","b":"metal"}`. The example only illustrates the structure; the actual values and pairings were randomized.

This comparison matters because A is on the path to B only in Shared-path. If filling A first helps B much more there than in Separate-path, that pattern is consistent with a dependency between the fields. Direct serves as a simpler control: B is already in the target row. The tables had the same number of rows and matched token lengths across conditions. An audit of all 600 sources per model found zero token-length mismatches. Every value was one token in its template context, and each source used distinct values.

Each model saw 200 sources at each table size. Every source was run under all three conditions and all three orders, allowing results to be compared **within the same source**. Exp 2 had 5,400 runs per model. Exp 3 reused the Shared-path and Separate-path sources; no instance was removed because a model got it wrong.

## Why the pilot began with a copy test

Before the lookup task, Exp 1 simply asked the models to copy two visible values into A and B. It had 20 instances under each order. This checked that masks, token positions, prompts, and decoding worked on a simple task before interpreting harder results.

LLaDA copied both fields correctly in **20/20 instances under every order**. Dream reached at least **19/20 for each field and order**. Both passed the preset G1 minimum of 95%. Both also passed the earlier G0 checks for one-mask recovery, tokenization, determinism, immutable commitments, batching agreement, memory, speed, and task integrity.

Passing a copy test does not establish that the lookup tables are easy. It does make a basic mask-position or output-format failure a less likely explanation for the later low scores.

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

An exact McNemar test uses those one-order-only counts to ask whether the disagreements are balanced or favor one order. It does not add information from sources where both orders had the same correctness result.

CF usually favored A at the first step, especially on Dream. It often picked the field associated with the successful fixed order among discordant Shared-path sources: **68/97** for LLaDA and **70/74** for Dream at size 8. CF did not consistently match A-first's final B accuracy. Its choice is based on the model's confidence at step zero, and confidence is not a guarantee that the first commitment will be correct or helpful. Since A was always left of B, this pilot cannot tell whether CF favored A because of a learned dependency, its position, or both.

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

## What prefilled A did to B in Exp 3

Exp 3 held A in one of four states while decoding B: still masked; filled with the correct A (**Gold**); filled with the model's initial A prediction (**Predicted**); or filled with A from a non-target row (**Wrong**). The key comparison is each branch against **Masked**. Gold beating Wrong by itself would be ambiguous, because Wrong could actively pull B toward an incorrect mapping.

Gold A improved B accuracy over Masked A substantially in Shared-path. The effect was smaller, near zero, or negative in Separate-path:

| Model | Rows per table | Shared-path Gold minus Masked | Separate-path Gold minus Masked |
|---|---:|---:|---:|
| LLaDA | 4 | +37.0 points [30.0, 44.0] | -1.5 points [-7.0, 4.0] |
| LLaDA | 8 | +46.0 points [39.0, 53.5] | -16.5 points [-22.0, -11.5] |
| LLaDA | 16 | +40.0 points [33.0, 47.0] | -2.5 points [-5.0, -0.5] |
| Dream | 4 | +32.5 points [25.5, 39.5] | +0.5 points [-6.0, 7.0] |
| Dream | 8 | +36.0 points [29.5, 42.5] | +5.0 points [-2.0, 12.0] |
| Dream | 16 | +40.5 points [33.5, 47.5] | -3.0 points [-9.0, 3.0] |

Putting the model's own initial A prediction into the field also improved Shared-path B accuracy: by **27.5 to 43.5 points** for LLaDA and **31.0 to 38.5 points** for Dream, depending on table size. This is the operationally relevant branch because a decoder normally has its own prediction, not an oracle's gold value. It does not make Exp 3 a fair comparison of complete decoding methods: Exp 3 measures B's response in a fixed context, and obtaining Predicted A requires an initial A pass.

The Wrong branch tested where a misleading value sends the model. If the wrong A came from row *j*, that row's B was recorded as the **alternative answer**. Shared-path has a mapping from that wrong A to the alternative B. Separate-path does not, so matching that same alternative is a baseline for comparison. At table size 16:

| Model | Wrong branch B equals alternative in Shared-path | Same match in Separate-path | Difference |
|---|---:|---:|---:|
| LLaDA | 185/200 (92.5%) | 7/200 (3.5%) | 89.0 points [84.5, 93.0] |
| Dream | 178/200 (89.0%) | 56/200 (28.0%) | 61.0 points [54.0, 67.5] |

This is strong evidence that the filled A value can steer B along the available A-to-B mapping. It also shows a risk: committing a wrong A can propagate the wrong linked B. The Separate-path baseline is not always zero, so the difference between conditions matters more than the Shared-path match rate alone.

## What the pilot supports and what remains open

The results support a limited mechanism claim: **for these one-token lookup prompts, the value committed in A changes the model's later B prediction, especially when the table connects A to B.** The paired order effects and the Gold, Predicted, and Wrong interventions point in the same direction for both models.

They do not yet support choosing an Exp 4 configuration. Direct B failed the preset 90% gate at every size, so there is no calibrated easy control. A stayed left of B throughout Phase 1, so order effects are still entangled with field position. The task used synthetic single-token values and only two output fields; it says nothing by itself about real tool calls, longer fields, or general performance on other prompts. The 95% intervals resample these sources 10,000 times; they describe uncertainty across similar sampled sources, not uncertainty across new models or task designs. Phase 1 sources should stay out of any final test set.

The current recommendation is **to lock no configuration for Exp 4 yet, pending human review**. A next study should first make the Direct lookup reliably solvable under a fixed, documented prompt, then test whether the Shared-path effect survives changes in A/B position and role. Changing this pilot's prompt now and selecting the better-looking result would break the frozen comparison; any revised setup should be treated as a new experiment.

## Where to find the underlying work

The [full results report](../results/phase1/report.md) has all cells, paired tests, step-zero confidence summaries, and deviations. The [preregistration](../results/phase1/PREREG.md) records the thresholds and planned analyses; [decisions](../results/phase1/DECISIONS.md) records implementation choices and fixes. The [trace files](../results/phase1/traces/) contain one JSONL row per run. Both models finished with **60 Exp 1, 5,400 Exp 2, and 4,800 Exp 3 rows**; sampled independent rescoring and report reproduction checks passed. Model revisions and seeds are in [config.yaml](../phase1/config.yaml).
