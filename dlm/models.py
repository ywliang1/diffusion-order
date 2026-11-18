"""Model loading for frozen masked diffusion LMs.

Loads pinned local snapshots in bf16 with no KV cache, exposes each model's own
mask token, and returns slot-aligned logits (Dream predicts position i from
position i-1, so its logits are shifted right by one; LLaDA is not shifted).
"""
import os
import socket
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

import torch
import transformers
from transformers import AutoModel, AutoTokenizer

ROOT = Path(__file__).resolve().parent.parent

# Pinned revisions. These must match the snapshot metadata under weights/.
REVISIONS = {
    'llada': dict(repo='GSAI-ML/LLaDA-8B-Instruct', revision='08b83a6feb34df1a6011b80c3c00c7563e963b07'),
    'dream': dict(repo='Dream-org/Dream-v0-Instruct-7B', revision='05334cb9faaf763692dcf9d8737c642be2b2a6ae'),
}
# Tokens that end the assistant turn; the first one in a decoded canvas starts the shared EOS crop.
END_TOKENS = {
    'llada': ('<|eot_id|>', '<|endoftext|>'),
    'dream': ('<|im_end|>', '<|endoftext|>'),
}


def weights_path(name):
    return ROOT / 'weights' / REVISIONS[name]['repo'].split('/')[1]


def snapshot_revision(name):
    """Commit hash recorded by huggingface_hub when the snapshot was downloaded."""
    meta = weights_path(name) / '.cache/huggingface/download/config.json.metadata'
    return meta.read_text().splitlines()[0].strip() if meta.exists() else None


@dataclass
class Bundle:
    name: str
    model: object
    tok: object
    mask_id: int
    end_ids: tuple
    device: str
    meta: dict = field(default_factory=dict)

    @property
    def shifted(self):
        return self.name == 'dream'


def load_tokenizer(name):
    tok = AutoTokenizer.from_pretrained(weights_path(name), trust_remote_code=True, use_fast=True)
    return tok


def mask_id_of(name):
    import json
    return json.loads((weights_path(name) / 'config.json').read_text())['mask_token_id']


def load(name, gpu):
    if name not in REVISIONS:
        raise ValueError(f'unknown model {name!r}')
    got = snapshot_revision(name)
    if got != REVISIONS[name]['revision']:
        raise RuntimeError(f'{name} snapshot revision {got} != pinned {REVISIONS[name]["revision"]}')
    if name == 'dream':
        # Dream runs with PyTorch's math attention kernel (Phase 1 G0 decision).
        torch.backends.cuda.enable_flash_sdp(False)
        torch.backends.cuda.enable_mem_efficient_sdp(False)
        torch.backends.cuda.enable_math_sdp(True)
    torch.cuda.set_device(gpu)
    tok = load_tokenizer(name)
    model = AutoModel.from_pretrained(weights_path(name), trust_remote_code=True, torch_dtype=torch.bfloat16,
                                      device_map=f'cuda:{gpu}', low_cpu_mem_usage=True).eval()
    mask_id = model.config.mask_token_id
    end_ids = tuple(tok.convert_tokens_to_ids(t) for t in END_TOKENS[name])
    return Bundle(name=name, model=model, tok=tok, mask_id=mask_id, end_ids=end_ids, device=f'cuda:{gpu}',
                  meta=environment(name, gpu))


def slot_logits(model, x, shifted):
    logits = model(input_ids=x, use_cache=False).logits
    if shifted:
        logits = torch.cat([logits[:, :1], logits[:, :-1]], dim=1)
    return logits


def git_commit():
    try:
        sha = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
        dirty = bool(subprocess.check_output(['git', 'status', '--porcelain', '--untracked-files=no'], cwd=ROOT, text=True).strip())
        return sha, dirty
    except Exception:
        return None, None


def environment(name=None, gpu=None):
    sha, dirty = git_commit()
    env = dict(hostname=socket.gethostname(), torch=torch.__version__, transformers=transformers.__version__,
               cuda_runtime=torch.version.cuda, git_commit=sha, git_dirty=dirty)
    if gpu is not None and torch.cuda.is_available():
        env['gpu_name'] = torch.cuda.get_device_name(gpu)
    if name is not None:
        env['model'] = name
        env['model_revision'] = REVISIONS[name]['revision']
    env['pid'] = os.getpid()
    return env
