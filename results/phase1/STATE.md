# Phase 1 state

Current step: Exp 2 and Exp 3 on both models. Code and config are frozen except documented bug fixes.

| Model | Status | Last check | Next action |
|---|---|---|---|
| LLaDA-8B-Instruct | Exp 1 complete | G0 pass; G1 pass (20/20 A and B under every order) | Supervisor runs Exp 2 and Exp 3 |
| Dream-v0-Instruct-7B | Exp 1 complete | G0 pass; G1 pass (at least 19/20 per field/order) | Supervisor runs Exp 2 and Exp 3 |

Detached supervisors: `phase1-supervisor-llada` on GPU 0, `phase1-supervisor-dream` on GPU 1. Logs and trace counts are in `results/phase1/`. After both finish, run analysis, independent rescoring, reproducibility check, and verify GPUs free.
