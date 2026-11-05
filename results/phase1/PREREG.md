# Phase 1 preregistration

Prepared before Exp 1. Config: `phase1/config.yaml`, seed 1729 for tasks and ties, bootstrap seed 7331 with 10,000 source-cluster resamples. Pinned model revisions are in the config. Prompt template is exact in the config; model chat templates wrap its instruction, and output uses two masked positions in a JSON object with A left of B. Candidate values are tokenized in the full filled template context for each model, and predictions use the full vocabulary excluding only the mask token.

Exp 1: 20 copy instances, three orders. G1 requires each field accuracy at least 95% per order. Exp 2: 200 sources at sizes 4, 8, 16; Direct, Shared-path, Separate-path; A-first, B-first, CF. G2 requires Direct B accuracy at least 90%, a path B accuracy clearly above 1/n and below approximately 90%, and at least 20 discordant A-first/B-first pairs per condition. G2 failure does not stop Exp 3. Exp 3: reuse path sources, decode B with A Masked, Gold, Predicted, or Wrong. Wrong A comes from a seeded non-target row.

Planned outcomes: A/B/both accuracy, paired correctness counts and exact McNemar tests, CF choice on discordant cases, A-first minus B-first interaction, Exp 3 branch gaps and interactions, wrong-branch alternative B matching, and step-0 confidence. Report 95% source-cluster bootstrap intervals. All instances remain in all analyses, regardless of correctness.

Pre-Exp-1 amendment: the assistant continuation contains the two-mask JSON output; the user text requests JSON without embedding a second masked output. The updated exact prompt is in `config.yaml`.

Pre-Exp-1 G2 operationalization: evaluate each table size separately. Direct B accuracy must be at least 90% under every order. Each path condition's B accuracy, pooled across orders by source, must have a source-cluster bootstrap lower 95% bound above 1/n and a point estimate below 90%. Each condition must have at least 20 discordant A-first/B-first full-answer pairs at that size. All three requirements must hold for a size to pass G2.

Post-freeze amendment, report-only bug: code inspection found that `analyze.py` omitted the Exp 4 recommendation and the deviations/failed-check record from its generated report. Restored both sections and added a regression test. The model decoder, tasks, config, and traces are unaffected; there are no affected traces to move to `invalid/` or rerun.
