# Exp 4 decisions and deviations

- 2026-11-17: Exp 4 calibrates its own table size (`PREREG.md`), because LLaDA did not meet the Phase 1.5b gate at any size up to 128.
- 2026-11-17: Dev calibration (1,600 CF rows per model). LLaDA: size 128 (two-hop dependent 73.0%, one-hop 96.5%; in band). Dream: no size reached 90% one-hop (81.5% at 16, 57.5% at 32, 68.0% at 64, 42.5% at 128), so the fallback branch picks 16, where two-hop dependent accuracy is 96.0%, outside the 40–80% band. H2 for Dream is therefore tested near ceiling and is expected to be weak. Main run: LLaDA 100 sources at 128, Dream 200 sources at 16 (seed 40001; task audits clean).
