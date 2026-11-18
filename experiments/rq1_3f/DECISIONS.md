# Three-field RQ1 study: decisions and deviations

- 2026-11-18: Design approved by the team, with LLaDA at 128 rows added, the independent field `h` kept, and the ±0.10 margin kept. PREREG frozen before any model output.
- 2026-11-18: Hardware: rosetta15 A100-PCIE-40GB for the whole stage, chosen before any output. rosetta21 was down (ssh timeout during the handshake since about 08:45 EST). All eight rosetta7 A6000s were in use by other users (97–100% utilization, 33–48 GB of 49 GB used). The team's instruction was: rosetta7 A6000s if free, otherwise the whole stage on rosetta15, logged here.
- 2026-11-18: Dev validity check passed for every arm (`results/rq1_3f/dev_check.json`, rosetta15 A100). One-hop all-three-correct and two-hop `h` correct: LLaDA at 8 rows, 100% and 100%; Dream at 8 rows, 99.6% and 99.6%; LLaDA at 128 rows, 100% and 98.3%. All three main arms run as preregistered.
- 2026-11-18 (after the main run): Main runs complete on rosetta15 A100 (`main-n8`: 4,800 CF traces per model; `main-n128`: 2,400 for LLaDA; commit `bfcc85e`). Analysis: `results/rq1_3f/report.md`. Preregistered verdicts:

  | Arm | H1b (role × slot) | H1 (slot) |
  |---|---|---|
  | LLaDA, 8 rows | inconclusive | contradicted |
  | Dream, 8 rows | supported | contradicted |
  | LLaDA, 128 rows | inconclusive | supported |

- 2026-11-18 (after the main run): **Error in the PREREG's H1 measure.** The PREREG says `h`'s position "cancels in the contrasts below". That is true for the DiD but not for POS.
  - **Why:** when a role field moves from the first slot to the last, `h` shifts from {middle, last} to {first, middle}. Under a pairwise (PL) model, POS = [θ_R(last) − θ_R(first)] + ½ [θ_h(last) − θ_h(first)], so it mixes in the reference field's own slot effect.
  - **Evidence:** for LLaDA at 8 rows, POS is +0.064 [+0.046, +0.082] while the PL slot effect is −0.130 [−0.196, −0.067]: opposite signs.
  - **Impact:** the H1 verdicts follow the preregistered rule, but the PL slot effect is the interpretable slot measure. By that measure:
    - LLaDA at 8 rows: −0.13 log-worth, a small left-to-right tendency (later slots committed later);
    - Dream at 8 rows: −0.03 [−0.09, +0.03], none;
    - LLaDA at 128 rows: −1.01 [−1.28, −0.79], a strong left-to-right tendency.
  - The DiD (H1b) is not affected.
- 2026-11-18 (after the main run): **The one-hop control is not null.** The PREREG expected the one-hop role × slot interaction to be near 0, because the roles there are nominal. It is not:
  - LLaDA: DiD +0.189 [+0.148, +0.231] at 8 rows and +0.195 [+0.145, +0.250] at 128 rows; PL +0.71 and +1.09.
  - Dream: PL +0.380 [+0.223, +0.553]; DiD +0.021 [−0.025, +0.068].
  - **Likely reason:** the "prerequisite" field always sits in the anchor row's second column, before `h`, and the "dependent" field (one-hop) after `h`. So the role labels also encode where the value sits in the input.
  - **Impact:** a two-hop role × slot interaction cannot be attributed to the dependency itself. For LLaDA, the two-hop DiD (+0.063 at 8 rows, +0.175 at 128 rows) is no larger than the one-hop control. Dream's two-hop interaction (−0.045, PL −0.17) has the opposite sign to its one-hop PL interaction.
  - **Interpretation:** there is no evidence that dependency role changes how output position affects commit order, beyond what input layout alone produces.
- 2026-11-18: All LLaDA two-hop traces at 8 rows (100%) have a CF margin below 0.02, so the "excluding flip-sensitive traces" sensitivity check has no data for that arm. The rate is 61% for Dream at 8 rows and 66% for LLaDA at 128 rows.
