# Phase 1 state

Current step: Exp 3 on both models. Exp 2 completed with 5,400 unique rows per model; supervisors are running Exp 3 regardless of G2, as preregistered.

| Model | Status | Last check | Next action |
|---|---|---|---|
| LLaDA-8B-Instruct | Exp 3 running | G0 pass; G1 pass; Exp 2 5,400/5,400, no duplicate IDs | Finish Exp 3; analyze G2 and all outcomes |
| Dream-v0-Instruct-7B | Exp 3 running | G0 pass; G1 pass; Exp 2 5,400/5,400, no duplicate IDs | Finish Exp 3; analyze G2 and all outcomes |

Detached supervisors: `phase1-supervisor-llada` on GPU 0, `phase1-supervisor-dream` on GPU 1. After both finish, run analysis, independent rescoring, report reproducibility check, and verify GPUs free.
