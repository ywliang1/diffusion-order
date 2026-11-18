"""Three-field RQ1 study: role (prerequisite, dependent, independent h) x slot (6 layouts) x hop, CF only.

Config keys: stage, split, seed, size, sources, orders.
run_id: <model>-<split>-n<size>-s<sid>-d<direction>-<layout>-h<hop>-<order>
"""
from dlm import ranks, schedules
from dlm.canvas import build
from dlm.decoder import Job, decode
from dlm.scoring import score_field, taxonomy
from experiments.phase1_5.exp import pool as base_pool
from experiments.rq1.exp import shown_rows
from tasks import lookup


def pool(tok, mask_id, name):
    """The Phase 1.5 pool minus every word of the three-field prompt text (only the closing line is new)."""
    stop = lookup.rl3_prompt_words()
    return [w for w in base_pool(tok, mask_id, name) if w.lower() not in stop]


def prepare(tok, mask_id, name, cfg):
    return dict(tok=tok, mask_id=mask_id, name=name, cfg=cfg, words=pool(tok, mask_id, name))


def jobs(ctx):
    c, name = ctx['cfg'], ctx['name']
    out = []
    for sid in range(c['sources']):
        for d in lookup.DIRECTIONS:
            for hop in lookup.HOPS:
                for lay in lookup.LAYOUTS3:
                    for o in c['orders']:
                        schedules.parse(o)
                        out.append(dict(run_id=f"{name}-{c['split']}-n{c['size']}-s{sid}-d{d}-{lay}-h{hop}-{o}",
                                        sid=sid, direction=d, hop=hop, layout=lay, order=o,
                                        group=f"s{sid}-d{d}-h{hop}-{lay}"))
    return out


def execute(bundle, ctx, group, batch=False):
    tok, mask_id, c = bundle.tok, bundle.mask_id, ctx['cfg']
    j0 = group[0]
    source = lookup.make_source(c['size'], j0['sid'], ctx['words'], c['seed'])
    lookup.rl_integrity(source, j0['direction'], j0['hop'])
    canvas = build(tok, mask_id, lookup.rl3_instruction(source, j0['direction'], j0['hop']),
                   lookup.rl3_output(j0['layout'], j0['direction']))
    fo = canvas.field_of()
    positions = canvas.masked_positions()
    t = source['rows'][source['target']]
    shown = shown_rows(source, j0['hop'])
    tie_seed = c['seed'] + j0['sid'] + c['size'] * 1000
    slots = lookup.rl3_slots(j0['layout'])
    rows = []
    for j in group:
        sched = schedules.make(j['order'], roles=canvas.roles, tie_seed=tie_seed, order_seed_base=c['seed'] + j['sid'])
        r = decode(bundle, [Job(canvas.ids, positions, sched, fo, canvas.roles)])[0]
        pred = {f: tok.decode([r['ids'][p] for p in ps]) for f, ps in canvas.fields.items()}
        fields = {f: score_field(pred[f], t[f]) for f in pred}
        first = {f: ranks.first_commit(r['steps'], ps) for f, ps in canvas.fields.items()}
        margins = [s['cf_margin'] for s in r['steps'] if s['cf_margin'] is not None]
        rows.append(dict(
            run_id=j['run_id'], split=c['split'], table_size=c['size'], source_id=j['sid'], direction=j['direction'],
            hop=j['hop'], layout=j['layout'], order=j['order'], target=dict(t), roles=canvas.roles, slot=slots,
            ranks=ranks.field_ranks(r['steps'], canvas.fields, positions), first_commit=first,
            field_order=sorted(first, key=first.get), fields=fields,
            taxonomy={f: taxonomy(pred[f], shown, source['target'], f) for f in pred},
            all_correct=all(v['correct'] for v in fields.values()),
            min_cf_margin=min(margins) if margins else None,
            tie_broken=any(s['tie'] for s in r['steps']), prompt_tokens=canvas.prompt_len,
            steps=r['steps'], step0=r['step0']))
    return rows
