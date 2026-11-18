# Three-field RQ1 study: role × position on CF commit order: preregistration

**Status: frozen 2026-11-18.** The team approved it on 2026-11-18 with these choices:

- add LLaDA at 128 rows;
- keep the independent third field;
- keep the ±0.10 margin.

This file is committed before any model output from this stage, including smoke. Code: `experiments/rq1_3f/{exp,audit,analyze}.py` and `tasks/lookup.py` (`rl3_*`). The analysis was checked on synthetic data only.

## Why a new design

H1 asks whether output position shifts commit order differently for prerequisite and dependent fields (the role × position interaction). The current two-field design cannot estimate that interaction, for any number of tokens per value:

- Each trace has exactly two fields, one per role and one per position. The two field ranks therefore sum to a constant, and the interaction contrast is exactly 0 (RQ1 study, Exp 4, Stage 3; `experiments/stage3/DECISIONS.md`).
- Changing the rank measure does not help. A Plackett–Luce (PL) model of the commit order has Fisher-information rank 2 of 4 cells. Only the two cross-trace differences θ(pre, left) − θ(dep, right) and θ(pre, right) − θ(dep, left) are identified.
- Adding a third field, used as a fixed reference, fixes this. The PL rank becomes 8 of 9, which is full rank once the overall constant is removed. "Committed before the reference field" then becomes a separate yes/no outcome for each role, and those outcomes do not sum to a constant.

**Simulation check** (`python -m experiments.rq1_3f.identifiability`): PL commit orders with a planted interaction, 200 sources, 40 simulations per row.

| Planted PL interaction | PL estimate (sd) | Model-free difference-in-differences (sd) |
|---:|---:|---:|
| 0 | −0.001 (0.158) | −0.001 (0.032) |
| +0.5 | +0.486 (0.160) | +0.083 (0.034) |
| +1.0 | +1.018 (0.147) | +0.204 (0.035) |

## Question and hypotheses

- **H1b (new, primary):** under CF, the effect of output position on commit order differs between the prerequisite and the dependent field.
- **H1 (re-test):** under CF, output position affects commit order after controlling for role and field identity.

## Items

The task is the RQ1 study's V2 two-hop lookup, plus one more output field.

- **The third field `h`** is the target row's `h` value. It is read straight from the anchor row by key, just like the prerequisite, but nothing depends on it. This makes it the **independent reference** role: it matches the prerequisite on lookup type and differs only in dependency role.
- **Input:** unchanged from the RQ1 study, since the anchor rows already contain `h=<H>`. The only text change is the closing line: "Return only the JSON object with fields a, b and h; no explanation."
- **Output:** a JSON scaffold with three masked single-token slots, in all **6 orders** of a, b and h (`{"a":…,"b":…,"h":…}`, `{"a":…,"h":…,"b":…}`, …). The input text never depends on layout.
- **Per-source factors:** query direction (a-prerequisite or b-prerequisite) × 6 layouts × hop (two-hop, or the matched one-hop control) = **24 items per source**, all with the same target triple.
- **One-hop control:** the anchor row carries both a and b, as in the RQ1 study, so all three fields are direct lookups. "Prerequisite" and "dependent" there are nominal labels, set by query direction.
- **Code:** new functions next to the existing `rl_*` functions in `tasks/lookup.py` (`rl3_output`, `rl3_instruction`, `rl3_slots`). The existing functions, used by RQ1, Exp 4 and Stage 3, are not changed.
- **Pool:** the Phase 1.5 pools minus every word of the prompt text. No word was removed: 4,015 words for LLaDA and 4,759 for Dream.
- **Task audit** (`results/rq1_3f/task_audit-*.json`): 0 failures in every config.
  - Main runs: 32,000 value checks per model at 8 rows, and 256,000 for LLaDA at 128 rows. Dev and smoke configs are also clean.
  - Prompt lengths are equal within each source, and all 6 layouts align.
  - No source matches a Phase 1 source.
  - The longest canvas is 3,298 tokens (LLaDA at 128 rows), within the 4,096-token context.

## Setup

- **Models and decoding:** as in the RQ1 study: pinned revisions, bf16, no KV cache, one commit per pass, greedy over the full vocabulary except the mask token, batch size 1. **CF only.** CF ties are broken by `random.Random(seed + source_id + 1000 × size)`.
Two arms, analyzed separately:

| Arm | Models | Rows | Sources | Seed | Traces per model | Of which two-hop | Trace name |
|---|---|---:|---:|---:|---:|---:|---|
| Primary | LLaDA, Dream | 8 | 200 | 60001 | 4,800 | 2,400 | `main-n8` |
| Second size (approved) | LLaDA only | 128 | 100 | 60001 | 2,400 | 1,200 | `main-n128` |

LLaDA at 128 rows is its Exp 4 size, where Exp 4 found the largest position effect.

**Dev validity check** (not a selection step): 20 sources (seed 60011), all 24 items, CF, at each arm's size (`dev-n8`, `dev-n128`).
- **Requirement:** one-hop all-three-correct ≥ 90%, and two-hop `h` accuracy ≥ 90%, per model and arm.
- **If an arm fails:** it is not run. I report it and stop for review, with no size search.

**Hardware:** rosetta15, NVIDIA A100-PCIE-40GB, for the whole stage. This was decided before any output, following the approved fallback. On 2026-11-18, rosetta21 was down (ssh timeout) and all eight rosetta7 A6000s were busy with other users' jobs (97–100% utilization, 33–48 GB used each). Within this stage, rows are comparable; across GPU types, only effects are.

## Measures

For each trace:
- the commit step of each field's single token;
- the full order of the three fields;
- field accuracy;
- the CF margin, with flip-sensitive meaning a minimum margin below 0.02.

## Primary analysis: two-hop traces, per model

**1. Model-free contrast (decides the verdicts).**

For role R ∈ {pre, dep} and slot p ∈ {first, last}, let B(R, p) be the share of traces in which R is committed before `h`, among traces with R in slot p.

Because all 6 layouts are used, `h` occupies the other slots equally often for both roles, so `h`'s position cancels in the contrasts below.

- **Interaction (H1b):** DiD = [B(dep, last) − B(dep, first)] − [B(pre, last) − B(pre, first)].
- **Position main effect (H1):** POS = ½ [B(dep, last) − B(dep, first) + B(pre, last) − B(pre, first)].

CIs are 95% bootstraps clustered by source (10,000 resamples, seed 7331).

**2. Plackett–Luce model (confirms the sign).**

- **Model:** the probability of the observed three-field commit order, with log-worth θ = role (3 levels) + slot (3) + role × slot + field identity (a vs b), and a weak ridge penalty (10⁻³) to guard against separation.
- **Reported:**
  - the interaction contrast [θ(dep, last) − θ(dep, first)] − [θ(pre, last) − θ(pre, first)];
  - the slot main effect, ½ [θ(dep, last) − θ(dep, first) + θ(pre, last) − θ(pre, first)];
  - the joint 4-df role × slot test: a Wald test on the double-centered 3 × 3 cell matrix, using the bootstrap covariance.
- **Also reported:** the number of bootstrap refits that did not converge.
- **CIs:** from the same source bootstrap.

**Verdict rules (per model):**

| Hypothesis | Supported | Contradicted | Inconclusive |
|---|---|---|---|
| **H1b** | DiD CI excludes 0, and the PL interaction CI excludes 0 with the same sign | DiD CI lies within ±0.10 | anything else |
| **H1** | POS CI excludes 0, and the PL slot main effect (last − first) CI excludes 0 with the same sign | POS CI lies within ±0.10 | anything else |

The ±0.10 margin is on the probability scale, the same as the RQ1 margin in rank units.

**Power** (simulation above): with 200 sources, the DiD has an SE of about 0.034; at 100 sources (128-row arm), about 0.048. The 95% CI half-width is therefore about 0.07, and the ±0.10 equivalence region is reachable only if the true |DiD| is below about 0.03.

## Secondary and descriptive

- **The same contrasts on one-hop controls.** These are expected near 0 for the interaction, since the roles there are nominal.
- **Middle-slot contrasts**, and B(R, p) for every cell.
- **Mean normalized rank** by role × slot (MixedLM `rank ~ role * slot + field`, source intercept).
  - **Caveat:** if each field's expected rank depended only on its own role and slot, this interaction would be forced to 0, because ranks within a trace still sum to a constant.
  - So a nonzero value means a field's rank depends on where the other fields sit. The DiD and PL rows are the interpretable ones.
- **Sensitivity:** excluding flip-sensitive traces, and on fully correct traces only.
- **Alignment:** the prerequisite committed before the dependent, two-hop vs one-hop.

## Approved choices (2026-11-18)

1. **Second size:** LLaDA at 128 rows (100 sources). Dream's Exp 4 size was 16, close to 8, so Dream gets no second arm.
2. **Third field:** the independent field `h`.
3. **Equivalence margin:** ±0.10 on the probability scale.

Smoke: 5 sources (120 traces per model) to `results/rq1_3f_smoke/`, excluded from analysis. Deviations go in `experiments/rq1_3f/DECISIONS.md`.
