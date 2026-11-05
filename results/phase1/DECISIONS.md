# Decisions and deviations

- 2026-11-05: The handoff's `ML-GSAI/LLaDA-8B-Instruct` returned HTTP 401. The public model is `GSAI-ML/LLaDA-8B-Instruct` at revision `08b83a6feb34df1a6011b80c3c00c7563e963b07`. Use the corrected namespace. Dream is pinned at `05334cb9faaf763692dcf9d8737c642be2b2a6ae`.
- 2026-11-05: Eight idle NVIDIA RTX A6000 GPUs (48 GiB each); use GPUs 0 and 1 only. Disk has 9.3 TiB free, RAM 503 GiB total. No active scheduler allocation is apparent; `tmux` is available. System Python 3.13 lacks PyTorch; use a virtual environment based on the existing qwen3 Python environment with PyTorch 2.5.1 CUDA 12.1 and pin Transformers 4.46.3 to match model configs.
