# Phase 1 state

Current step: G0 checks on pinned local model downloads.

| Model | Status | Last check | Next action |
|---|---|---|---|
| LLaDA-8B-Instruct | running G0 | Pinned weights downloaded; GPU 0 was idle | Complete G0, benchmark, Exp 1 |
| Dream-v0-Instruct-7B | running G0 | Pinned weights downloaded; GPU 1 was idle | Complete G0, benchmark, Exp 1 |

The detached G0 sessions are `phase1-g0-llada` and `phase1-g0-dream`. Logs are in `results/phase1/logs/`. Final statuses require Exp 1–3, gates, analysis, independent rescoring, and stopped jobs.
