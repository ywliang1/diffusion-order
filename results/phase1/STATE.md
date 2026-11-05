# Phase 1 state

Current step: LLaDA G1 passed after Exp 1; Dream final G0 recovery check running. Next: commit the pre-Exp-2 code and launch detached supervisors.

| Model | Status | Last check | Next action |
|---|---|---|---|
| LLaDA-8B-Instruct | Exp 1 complete | G0 pass; G1 pass (20/20 A and B under every order) | Exp 2 then Exp 3 |
| Dream-v0-Instruct-7B | running G0 | G0 passed after Dream-specific logit shift; final one-mask recovery check running | If G0 passes, Exp 1 and G1 |

Logs: `results/phase1/logs/`; traces: `results/phase1/traces/`. Final statuses require Exp 1–3, gates, analysis, independent rescoring, and stopped jobs.
