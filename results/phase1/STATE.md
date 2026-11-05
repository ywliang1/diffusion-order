# Phase 1 state

Current step: complete. Every model has a final status; no jobs remain.

| Model | Final status | Last check | Next action |
|---|---|---|---|
| LLaDA-8B-Instruct | complete | G0 pass; G1 pass; G2 fail at 4, 8, 16; Exp 1/2/3 rows 60/5,400/4,800; sampled rescoring pass | Human review of report and Exp 4 recommendation |
| Dream-v0-Instruct-7B | complete | G0 pass; G1 pass; G2 fail at 4, 8, 16; Exp 1/2/3 rows 60/5,400/4,800; sampled rescoring pass | Human review of report and Exp 4 recommendation |

Checks completed: exact row counts and no duplicate run IDs; G0/G1/G2 recorded for both models; 20 independently rescored rows per experiment and model passed; `analyze.py` reproduced `report.md` byte for byte (`report.sha256`); three regression tests passed; task-token-length audit found zero mismatches across 600 sources per model; no Phase 1 tmux sessions remain; GPUs 0 and 1 returned to 2 MiB idle usage. G2 failure is a pilot finding and does not change the `complete` status.
