"""Exp 4: role x layout x hop with CF, PF, DF, L2R, R2L and random orders (RQ1 + RQ2), V2 format.

Same items as the RQ1 study (tasks.lookup rl_*), at a table size per model.
Config keys: stage, split, seed, size (int, or {model: int}), sources, orders, tokens (values per field, default 1).
run_id: <model>-<split>-n<size>-s<sid>-d<direction>-<layout>-h<hop>-<order>
"""
import json

from dlm import ranks, schedules
from dlm.canvas import build
from dlm.decoder import Job, decode
from dlm.models import ROOT
from dlm.scoring import score_field, taxonomy
from experiments.phase1_5.exp import pool
from experiments.rq1.exp import shown_rows
from tasks import lookup


def size_of(cfg, name):
    s = cfg['size']
    return s[name] if isinstance(s, dict) else s


def multi_pool(tok, mask_id, name, k):
    path = ROOT / 'results/stage3' / f'pool-k{k}-{name}.json'
    if path.exists():
        return json.loads(path.read_text())
    words = lookup.build_multi_pool(tok, mask_id, pool(tok, mask_id, name), k)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(words) + '\n')
    return words


def prepare(tok, mask_id, name, cfg):
    k = cfg.get('tokens', 1)
    words = pool(tok, mask_id, name) if k == 1 else multi_pool(tok, mask_id, name, k)
    return dict(tok=tok, mask_id=mask_id, name=name, cfg=cfg, size=size_of(cfg, name), words=words, k=k)


def jobs(ctx):
    c, name, n = ctx['cfg'], ctx['name'], ctx['size']
    sizes = c.get('sizes_per_model', {}).get(name, [n])
    n_sources = c.get('sources_per_model', {}).get(name, c['sources'])
    out = []
    for size in sizes:
        for sid in range(n_sources):
            for d in lookup.DIRECTIONS:
                for hop in lookup.HOPS:
                    for lay in lookup.LAYOUTS:
                        for o in c['orders']:
                            schedules.parse(o)
                            out.append(dict(run_id=f"{name}-{c['split']}-n{size}-s{sid}-d{d}-{lay}-h{hop}-{o}",
                                            size=size, sid=sid, direction=d, hop=hop, layout=lay, order=o,
                                            group=f"n{size}-s{sid}-d{d}-h{hop}-{lay}"))
    return out


def execute(bundle, ctx, group, batch=False):
    tok, mask_id, c = bundle.tok, bundle.mask_id, ctx['cfg']
    j0 = group[0]
    size = j0['size']
    source = lookup.make_source(size, j0['sid'], ctx['words'], c['seed'])
    lookup.rl_integrity(source, j0['direction'], j0['hop'])
    canvas = build(tok, mask_id, lookup.rl_instruction(source, j0['direction'], j0['hop']),
                   lookup.rl_output(j0['layout'], j0['direction'], ctx['k']))
    fo = canvas.field_of()
    positions = canvas.masked_positions()
    left = min(canvas.fields, key=lambda f: canvas.fields[f][0])
    t = source['rows'][source['target']]
    shown = shown_rows(source, j0['hop'])
    tie_seed = c['seed'] + j0['sid'] + size * 1000
    pre = next(f for f, role in canvas.roles.items() if role == 'prerequisite')
    dep = next(f for f, role in canvas.roles.items() if role == 'dependent')
    rows = []
    for j in group:
        sched = schedules.make(j['order'], roles=canvas.roles, tie_seed=tie_seed, order_seed_base=c['seed'] + j['sid'])
        r = decode(bundle, [Job(canvas.ids, positions, sched, fo, canvas.roles)])[0]
        pred = {f: tok.decode([r['ids'][p] for p in ps]) for f, ps in canvas.fields.items()}
        fields = {f: score_field(pred[f], t[f]) for f in pred}
        margins = [s['cf_margin'] for s in r['steps'] if s['cf_margin'] is not None]
        rows.append(dict(
            run_id=j['run_id'], split=c['split'], table_size=size, source_id=j['sid'], direction=j['direction'],
            hop=j['hop'], layout=j['layout'], order=j['order'], target=dict(t), roles=canvas.roles,
            position={f: ('left' if f == left else 'right') for f in canvas.fields},
            ranks=ranks.field_ranks(r['steps'], canvas.fields, positions), fields=fields,
            taxonomy={f: taxonomy(pred[f], shown, source['target'], f) for f in pred},
            A_correct=fields['A']['correct'], B_correct=fields['B']['correct'],
            both_correct=fields['A']['correct'] and fields['B']['correct'],
            prerequisite_correct=fields[pre]['correct'], dependent_correct=fields[dep]['correct'],
            first_field=r['steps'][0]['field'], prerequisite_first=ranks.first_commit(r['steps'], canvas.fields[pre]) < ranks.first_commit(r['steps'], canvas.fields[dep]),
            left_first=r['steps'][0]['field'] == left, min_cf_margin=min(margins) if margins else None,
            tokens_per_value=ctx['k'], within_field_l2r={f: ranks.within_field_l2r(r['steps'], ps) for f, ps in canvas.fields.items()},
            first_commit={f: ranks.first_commit(r['steps'], ps) for f, ps in canvas.fields.items()},
            tie_broken=any(s['tie'] for s in r['steps']), prompt_tokens=canvas.prompt_len,
            steps=r['steps'], step0=r['step0']))
    return rows
