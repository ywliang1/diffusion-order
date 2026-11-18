"""BFCL generation: chat-templated BFCL prompt + a fully masked canvas of fixed length, decoded with
one commit per pass under L2R, R2L, random-s0..2 or CF. Shared EOS cropping: content is every canvas
token before the first end token; nothing is repaired. Scoring runs separately in the BFCL venv
(experiments/bfcl/score.py).

Config keys: stage, split ('test', 'dev' or 'sanity'), seed, length, orders, schemas, limit (optional).
run_id: <model>-<split>-<item id>-<schema>-<order>
"""
import json
import re
import zlib

from dlm import ranks, schedules
from dlm.canvas import build_chat
from dlm.decoder import Job, decode
from dlm.models import ROOT

FILES = {'test': 'items.jsonl', 'dev': 'dev.jsonl', 'sanity': 'sanity.jsonl'}
NAME = re.compile(r'^\s*`*\s*(?:json)?\s*\[?\s*(?:\{\s*"function"\s*:\s*")?([A-Za-z_][\w.]*)')


def prepare(tok, mask_id, name, cfg):
    items = [json.loads(x) for x in open(ROOT / 'results/bfcl' / FILES[cfg['split']])]
    items = [it for it in items if it['schema'] in cfg['schemas']]
    if cfg.get('limit'):
        keep = sorted({it['id'] for it in items})[:cfg['limit']]
        items = [it for it in items if it['id'] in set(keep)]
    return dict(tok=tok, mask_id=mask_id, name=name, cfg=cfg, items={(it['id'], it['schema']): it for it in items})


def jobs(ctx):
    c, name = ctx['cfg'], ctx['name']
    out = []
    for (iid, schema) in ctx['items']:
        for o in c['orders']:
            schedules.parse(o)
            out.append(dict(run_id=f"{name}-{c['split']}-{iid}-{schema}-{o}", item=iid, schema=schema, order=o,
                            group=f'{iid}-{schema}'))
    return out


def name_positions(content, content_tokens, text):
    """Canvas positions of the first called function's name, via character offsets of the content tokens."""
    m = NAME.search(text)
    if not m:
        return []
    st, en = m.span(1)
    out, pos = [], 0
    for p, piece in zip(content, content_tokens):
        if pos < en and pos + len(piece) > st:
            out.append(p)
        pos += len(piece)
    return out


def execute(bundle, ctx, group, batch=False):
    tok, mask_id, c = bundle.tok, bundle.mask_id, ctx['cfg']
    j0 = group[0]
    it = ctx['items'][(j0['item'], j0['schema'])]
    canvas = build_chat(tok, mask_id, it['messages'], c['length'])
    L = c['length']
    h = zlib.crc32(it['id'].encode()) % 100003
    rows = []
    for j in group:
        sched = schedules.make(j['order'], tie_seed=c['seed'] + h, order_seed_base=c['seed'] + h)
        r = decode(bundle, [Job(canvas.ids, canvas.tail, sched)])[0]
        final = r['ids']
        content = canvas.content_positions(final, end_ids=bundle.end_ids)
        content_ids = [final[p] for p in content]
        content_tokens = [tok.decode([t]) for t in content_ids]
        text = tok.decode(content_ids)
        step_of = {s['pos']: s['step'] for s in r['steps']}
        noncontent = [p for p in canvas.tail if p not in set(content)]
        first_end = canvas.tail[len(content)] if len(content) < L else None
        rk = ranks.normalized(r['steps'], content)
        fn = name_positions(content, content_tokens, text)
        margins = [s['cf_margin'] for s in r['steps'] if s['cf_margin'] is not None]
        rows.append(dict(
            run_id=j['run_id'], split=c['split'], item=it['id'], category=it['category'], schema=j['schema'], order=j['order'],
            return_format=it['return_format'], length=L, prompt_tokens=canvas.prompt_len, text=text,
            content_len=len(content), hit_length_limit=len(content) == L,
            first_end_rank=(step_of[first_end] / (L - 1)) if first_end is not None else None,
            noncontent_mean_rank=(sum(step_of[p] for p in noncontent) / len(noncontent) / (L - 1)) if noncontent else None,
            fn_positions=fn, fn_rank=(sum(rk[p] for p in fn) / len(fn)) if fn else None,
            content_ranks=[rk[p] for p in content], content_tokens=content_tokens,
            min_cf_margin=min(margins) if margins else None, steps=r['steps']))
    return rows
