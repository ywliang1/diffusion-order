# BFCL decisions and deviations

- 2026-11-17: bfcl-eval 2026.3.23 runs in an isolated venv (it pins numpy 1.26, which conflicts with the generation venv). A no-deps install failed because the AST checker imports every API model handler at load time, so the venv has the full dependency set plus `soundfile`.
- 2026-11-17: Smoke-run bug fixed before any full run: the function-name locator took the first word of prose outputs as the function name. It now takes the first identifier followed by `(` (or a JSON `"function"` value). Only the 24 smoke rows were affected.
- 2026-11-17: Scoring config `qwen3-8b` (a BFCL prompting config with `underscore_to_dot=False`); the first choice, `Qwen/Qwen2.5-7B-Instruct`, is not in this version's config table.
- 2026-11-17: Scorer validation: 790/800 rendered gold calls pass; the 10 failures come from rendering only the first acceptable value per parameter, not from the checker.
