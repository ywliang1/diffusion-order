# RQ1 study decisions and deviations

- 2026-11-17: Study approved by the team to run in parallel with Phase 1.5b, V2 format, size 8, CF only.
- 2026-11-17: Main run complete on rosetta21 A6000 (1,600 CF traces per model, commit `450a96a`).
- 2026-11-17: Analysis note (not a change to the plan). With two single-token fields, the two ranks in a trace sum to 1, so the pre-registered role × position interaction is identically zero in the data (bootstrap [0, 0]); the mixed model's interval for it reflects only its standard error. The design is balanced, so refitting without the interaction gives identical main effects (LLaDA position +0.013 [−0.028, +0.053], role +0.568; Dream position −0.052 [−0.095, −0.010], role +0.378). The interaction becomes identifiable only with multi-token fields (Stage 3).
- 2026-11-17: Caveat. 91.1% of LLaDA traces (9.8% of Dream's) have a CF margin below 0.02, because both fields are near probability 1 at size 8. The role effect is systematic across 800 two-hop traces, but individual LLaDA commit orders are fragile (Stage 0: about 30% of decisions with margin < 0.01 flip between GPU types).
