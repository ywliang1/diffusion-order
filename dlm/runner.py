"""Data-parallel runner: one resident model per GPU, instances sharded across GPUs, resume by run_id.

An experiment module provides:
    prepare(tok, mask_id, model_name, cfg) -> ctx          (CPU only; tokenizer-dependent setup)
    jobs(ctx) -> list of dicts with 'run_id' and 'group'   (deterministic order)
    execute(bundle, ctx, group_jobs, batch) -> list of trace rows

Jobs that share a 'group' run in one execute call (and may share a lockstep batch when
batch=True). Groups are dealt round-robin to shards. Each shard appends to its own file
under results/<stage>/traces/shards/, fsyncing each row; `merge` checks counts, duplicate
run_ids and that every row came from one GPU type, then writes results/<stage>/traces/<trace>-<model>.jsonl.

    python -m dlm.runner launch --exp experiments.equivalence.exp --config experiments/equivalence/config.yaml \
        --stage equivalence --trace phase1 --models llada,dream --gpus 0,1,2,3,4,5,6,7 [--expect-gpu "RTX A6000"]
"""
import argparse
import importlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent


def stage_dir(stage):
    return ROOT / 'results' / stage


def shard_dir(stage):
    return stage_dir(stage) / 'traces' / 'shards'


def shard_files(stage, trace, model):
    return sorted(shard_dir(stage).glob(f'{trace}-{model}.shard*.jsonl'))


def read_jsonl(path):
    with open(path) as f:
        return [json.loads(line) for line in f if line.strip()]


def done_ids(stage, trace, model):
    seen = set()
    for p in shard_files(stage, trace, model):
        for line in open(p):
            if line.strip():
                seen.add(json.loads(line)['run_id'])
    return seen


def load_cfg(path):
    return yaml.safe_load(Path(path).read_text())


def grouped(jobs):
    groups, index = [], {}
    for j in jobs:
        g = j.get('group', j['run_id'])
        if g not in index:
            index[g] = len(groups)
            groups.append([])
        groups[index[g]].append(j)
    return groups


def worker(a):
    from dlm.models import load
    exp = importlib.import_module(a.exp)
    cfg = load_cfg(a.config)
    bundle = load(a.model, a.gpu)
    if a.expect_gpu and a.expect_gpu not in bundle.meta.get('gpu_name', ''):
        raise SystemExit(f'GPU {bundle.meta.get("gpu_name")} does not match expected {a.expect_gpu!r}')
    ctx = exp.prepare(bundle.tok, bundle.mask_id, a.model, cfg)
    groups = grouped(exp.jobs(ctx))
    mine = [g for i, g in enumerate(groups) if i % a.nshards == a.shard]
    seen = done_ids(a.stage, a.trace, a.model)
    out = shard_dir(a.stage) / f'{a.trace}-{a.model}.shard{a.shard}of{a.nshards}.jsonl'
    out.parent.mkdir(parents=True, exist_ok=True)
    meta = dict(bundle.meta, stage=a.stage, trace=a.trace, seed=cfg.get('seed'), config=str(a.config))
    import torch
    torch.cuda.reset_peak_memory_stats()
    start, new = time.time(), 0
    todo = [g for g in mine if any(j['run_id'] not in seen for j in g)]
    print(f'START shard {a.shard}/{a.nshards} groups {len(mine)} todo {len(todo)} gpu {a.gpu} {meta.get("gpu_name")}', flush=True)
    with open(out, 'a', buffering=1) as f:
        for g in todo:
            rows = exp.execute(bundle, ctx, g, batch=a.batch)
            for r in rows:
                if r['run_id'] in seen:
                    continue
                r['meta'] = meta
                f.write(json.dumps(r, ensure_ascii=False) + '\n')
                seen.add(r['run_id'])
                new += 1
            f.flush()
            os.fsync(f.fileno())
            if new and new % 200 < len(rows):
                print(f'PROGRESS {new} rows {time.time() - start:.1f}s', flush=True)
    print(f'DONE shard {a.shard} new {new} seconds {time.time() - start:.1f} '
          f'peak_GB {torch.cuda.max_memory_allocated() / 1e9:.2f}', flush=True)


def expected_ids(a, model):
    from dlm.models import load_tokenizer, mask_id_of
    exp = importlib.import_module(a.exp)
    ctx = exp.prepare(load_tokenizer(model), mask_id_of(model), model, load_cfg(a.config))
    return [j['run_id'] for j in exp.jobs(ctx)]


def merge(a, model, order=None):
    rows = [r for p in shard_files(a.stage, a.trace, model) for r in read_jsonl(p)]
    ids = [r['run_id'] for r in rows]
    if len(ids) != len(set(ids)):
        raise RuntimeError(f'duplicate run_ids in {a.trace}-{model}')
    gpus = {r['meta'].get('gpu_name') for r in rows}
    if len(gpus) > 1:
        raise RuntimeError(f'mixed GPU types in {a.trace}-{model}: {gpus}')
    if order is not None:
        missing = set(order) - set(ids)
        if missing:
            raise RuntimeError(f'{len(missing)} runs missing for {model}, e.g. {sorted(missing)[:3]}')
        pos = {rid: i for i, rid in enumerate(order)}
        rows.sort(key=lambda r: pos[r['run_id']])
    path = stage_dir(a.stage) / 'traces' / f'{a.trace}-{model}.jsonl'
    with open(path, 'w') as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + '\n')
    return path, len(rows), gpus


def launch(a):
    models = a.models.split(',')
    gpus = [int(g) for g in a.gpus.split(',')]
    if len(gpus) < len(models):
        raise SystemExit('need at least one GPU per model')
    per = len(gpus) // len(models)
    logs = stage_dir(a.stage) / 'logs'
    logs.mkdir(parents=True, exist_ok=True)
    order = {m: expected_ids(a, m) for m in models}
    for attempt in range(1, a.retries + 2):
        procs = []
        for mi, m in enumerate(models):
            mine = gpus[mi * per:(mi + 1) * per]
            for si, g in enumerate(mine):
                cmd = [sys.executable, '-u', '-m', 'dlm.runner', 'worker', '--exp', a.exp, '--config', a.config,
                       '--stage', a.stage, '--trace', a.trace, '--model', m, '--gpu', str(g),
                       '--shard', str(si), '--nshards', str(len(mine))]
                if a.batch:
                    cmd.append('--batch')
                if a.expect_gpu:
                    cmd += ['--expect-gpu', a.expect_gpu]
                log = open(logs / f'{a.trace}-{m}-shard{si}of{len(mine)}.log', 'a')
                log.write(f'\nLAUNCH attempt {attempt} {time.ctime()} host {os.uname().nodename}\n')
                log.flush()
                procs.append((m, si, subprocess.Popen(cmd, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT)))
        codes = [(m, si, p.wait()) for m, si, p in procs]
        incomplete = [m for m in models if len(done_ids(a.stage, a.trace, m) & set(order[m])) < len(order[m])]
        print(f'attempt {attempt}: exit codes {codes}; incomplete {incomplete}', flush=True)
        if not incomplete:
            break
    else:
        raise SystemExit(f'incomplete after {a.retries + 1} attempts: {incomplete}')
    for m in models:
        path, n, g = merge(a, m, order[m])
        print(f'MERGED {path} rows {n} gpu {g}', flush=True)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('mode', choices=['launch', 'worker', 'merge'])
    ap.add_argument('--exp', required=True)
    ap.add_argument('--config', required=True)
    ap.add_argument('--stage', required=True)
    ap.add_argument('--trace', required=True)
    ap.add_argument('--model')
    ap.add_argument('--models', default='llada,dream')
    ap.add_argument('--gpu', type=int)
    ap.add_argument('--gpus', default='0,1,2,3,4,5,6,7')
    ap.add_argument('--shard', type=int, default=0)
    ap.add_argument('--nshards', type=int, default=1)
    ap.add_argument('--batch', action='store_true')
    ap.add_argument('--expect-gpu', default=None)
    ap.add_argument('--retries', type=int, default=2)
    a = ap.parse_args(argv)
    if a.mode == 'worker':
        worker(a)
    elif a.mode == 'launch':
        launch(a)
    else:
        for m in a.models.split(','):
            print(merge(a, m, expected_ids(a, m)))


if __name__ == '__main__':
    main()
