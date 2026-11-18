"""Autoregressive reference for BFCL: Qwen2.5-7B-Instruct, greedy, on the same chat messages as the diffusion runs.

Same budget as the diffusion canvas (`length` new tokens, 64), bf16, batch size 1, no repair. The content is every
generated token before the first end token (<|im_end|> or <|endoftext|>), as in the shared EOS crop. Rows match
the diffusion trace format closely enough for experiments/bfcl/score.py (--models qwen).

    python -m experiments.bfcl.ar --config experiments/bfcl/config_ar.yaml --trace test-ar --gpu 0
"""
import argparse
import json
import socket

import torch
import transformers
from transformers import AutoModelForCausalLM, AutoTokenizer

from dlm.models import ROOT
from dlm.runner import load_cfg

REPO = 'Qwen/Qwen2.5-7B-Instruct'
REVISION = 'a09a35458c702b33eeacc393d103063234e8bc28'
WEIGHTS = ROOT / 'weights/Qwen2.5-7B-Instruct'
END = ('<|im_end|>', '<|endoftext|>')
FILES = {'test': 'items.jsonl', 'dev': 'dev.jsonl', 'sanity': 'sanity.jsonl'}


def snapshot_revision():
    meta = WEIGHTS / '.cache/huggingface/download/config.json.metadata'
    return meta.read_text().splitlines()[0].strip() if meta.exists() else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--config', required=True)
    ap.add_argument('--trace', required=True)
    ap.add_argument('--gpu', type=int, default=0)
    ap.add_argument('--expect-gpu', default=None)
    a = ap.parse_args()
    c = load_cfg(a.config)
    if snapshot_revision() != REVISION:
        raise SystemExit(f'weights revision {snapshot_revision()} != pinned {REVISION}')
    dev = f'cuda:{a.gpu}'
    gpu = torch.cuda.get_device_name(a.gpu)
    if a.expect_gpu and a.expect_gpu not in gpu:
        raise SystemExit(f'expected GPU {a.expect_gpu!r}, got {gpu!r}')
    import subprocess
    sha = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    meta = dict(hostname=socket.getfqdn(), gpu_name=gpu, torch=torch.__version__, transformers=transformers.__version__,
                git_commit=sha, model=REPO, model_revision=REVISION, seed=c['seed'], decoding='greedy', dtype='bfloat16')
    tok = AutoTokenizer.from_pretrained(WEIGHTS)
    model = AutoModelForCausalLM.from_pretrained(WEIGHTS, torch_dtype=torch.bfloat16).to(dev).eval()
    end_ids = [tok.convert_tokens_to_ids(t) for t in END]
    items = [json.loads(x) for x in open(ROOT / 'results/bfcl' / FILES[c['split']])]
    items = [it for it in items if it['schema'] in c['schemas']]
    out = ROOT / 'results' / c['stage'] / 'traces' / f'{a.trace}-qwen.jsonl'
    out.parent.mkdir(parents=True, exist_ok=True)
    done = {json.loads(x)['run_id'] for x in open(out)} if out.exists() else set()
    torch.manual_seed(c['seed'])
    with open(out, 'a') as f:
        for n, it in enumerate(items):
            rid = f"qwen-{c['split']}-{it['id']}-{it['schema']}-AR"
            if rid in done:
                continue
            ids = tok.apply_chat_template(it['messages'], add_generation_prompt=True, return_tensors='pt').to(dev)
            with torch.no_grad():
                gen = model.generate(ids, attention_mask=torch.ones_like(ids), max_new_tokens=c['length'], do_sample=False,
                                     temperature=None, top_p=None, top_k=None, eos_token_id=end_ids, pad_token_id=end_ids[-1])
            new = gen[0, ids.shape[1]:].tolist()
            cut = next((i for i, t in enumerate(new) if t in end_ids), len(new))
            content = new[:cut]
            f.write(json.dumps(dict(
                run_id=rid, split=c['split'], item=it['id'], category=it['category'], schema=it['schema'], order='AR',
                return_format=it['return_format'], length=c['length'], prompt_tokens=int(ids.shape[1]),
                text=tok.decode(content), content_len=len(content), hit_length_limit=cut == len(new) and len(new) == c['length'],
                meta=meta), ensure_ascii=False) + '\n')
            f.flush()
            if n % 50 == 0:
                print('PROGRESS', n, len(items), flush=True)
    print('DONE', out, flush=True)


if __name__ == '__main__':
    main()
