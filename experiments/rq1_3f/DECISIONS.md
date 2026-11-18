# Three-field RQ1 study: decisions and deviations

- 2026-11-18: Design approved by the team, with LLaDA at 128 rows added, the independent field `h` kept, and the ±0.10 margin kept. PREREG frozen before any model output.
- 2026-11-18: Hardware: rosetta15 A100-PCIE-40GB for the whole stage, chosen before any output. rosetta21 was down (ssh timeout during the handshake since about 08:45 EST). All eight rosetta7 A6000s were in use by other users (97–100% utilization, 33–48 GB of 49 GB used). The team's instruction was: rosetta7 A6000s if free, otherwise the whole stage on rosetta15, logged here.
