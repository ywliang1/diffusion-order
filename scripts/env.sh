# Environment for remote and nohup runs: nothing under AFS (tokens expire for
# detached processes), no user site-packages, Hugging Face offline.
export HOME=/data/scratch/linrui/llada_home
export PYTHONNOUSERSITE=1
export HF_HOME=/data/rbg/users/linrui/hf_cache
export HF_HUB_OFFLINE=1
export TRANSFORMERS_OFFLINE=1
export XDG_CACHE_HOME=/data/scratch/linrui/xdg_cache
export TORCH_HOME=/data/rbg/users/linrui/torch_cache
export MPLCONFIGDIR=$HOME/.mpl
export TRITON_CACHE_DIR=$HOME/.triton
unset TRANSFORMERS_CACHE
mkdir -p "$HOME" "$MPLCONFIGDIR"
cd /data/rbg/users/linrui/llada
