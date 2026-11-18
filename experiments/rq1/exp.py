"""RQ1 study: role x layout (x hop control) commit ranks under CF, V2 format.

Config keys: split, seed, size, sources, orders.
run_id: <model>-<split>-n<size>-s<sid>-d<direction>-<layout>-h<hop>-<order>
"""
from dlm import ranks, schedules
from dlm.canvas import build
from dlm.decoder import Job, decode
from dlm.scoring import score_field, taxonomy
from experiments.phase1_5.exp import pool
from tasks import lookup


def prepare(tok, mask_id, name, cfg):
    return dict(tok=tok, mask_id=mask_id, name=name, cfg=cfg, words=pool(tok, mask_id, name))


def jobs(ctx):
    c, name = ctx['cfg'], ctx['name']
    out = []
    for sid in range(c['sources']):
        for d in lookup.DIRECTIONS:
            for hop in lookup.HOPS:
                for lay in lookup.LAYOUTS:
                    for o in c['orders']:
                        schedules.parse(o)
                        out.append(dict(run_id=f"{name}-{c['split']}-n{c['size']}-s{sid}-d{d}-{lay}-h{hop}-{o}",
                                        sid=sid, direction=d, hop=hop, layout=lay, order=o,
                                        group=f"s{sid}-d{d}-h{hop}-{lay}"))
    return out


def shown_rows(source, hop):
    keep = {'q', 'A', 'B', 'H'} | ({'C'} if hop == 2 else {'D', 'E'})
    return [{k: v for k, v in r.items() if k in keep} for r in source['rows']]


def execute(bundle, ctx, group, batch=False):
    tok, mask_id, c = bundle.tok, bundle.mask_id, ctx['cfg']
    j0 = group[0]
    source = lookup.make_source(c['size'], j0['sid'], ctx['words'], c['seed'])
    lookup.rl_integrity(source, j0['direction'], j0['hop'])
    canvas = build(tok, mask_id, lookup.rl_instruction(source, j0['direction'], j0['hop']),
                   lookup.rl_output(j0['layout'], j0['direction']))
    fo = canvas.field_of()
    positions = canvas.masked_positions()
    left = min(canvas.fields, key=lambda f: canvas.fields[f][0])
    t = source['rows'][source['target']]
    shown = shown_rows(source, j0['hop'])
    tie_seed = c['seed'] + j0['sid'] + c['size'] * 1000
    rows = []
    for j in group:
        sched = schedules.make(j['order'], roles=canvas.roles, tie_seed=tie_seed, order_seed_base=c['seed'] + j['sid'])
        r = decode(bundle, [Job(canvas.ids, positions, sched, fo, canvas.roles)])[0]
        pred = {f: tok.decode([r['ids'][ps[0]]]) for f, ps in canvas.fields.items()}
        fields = {f: score_field(pred[f], t[f]) for f in pred}
        fr = ranks.field_ranks(r['steps'], canvas.fields, positions)
        pre = next(f for f, role in canvas.roles.items() if role == 'prerequisite')
        margins = [s['cf_margin'] for s in r['steps'] if s['cf_margin'] is not None]
        rows.append(dict(
            run_id=j['run_id'], split=c['split'], table_size=c['size'], source_id=j['sid'], direction=j['direction'],
            hop=j['hop'], layout=j['layout'], order=j['order'], target=dict(t), roles=canvas.roles,
            position={f: ('left' if f == left else 'right') for f in canvas.fields}, ranks=fr, fields=fields,
            taxonomy={f: taxonomy(pred[f], shown, source['target'], f) for f in pred},
            A_correct=fields['A']['correct'], B_correct=fields['B']['correct'],
            both_correct=fields['A']['correct'] and fields['B']['correct'],
            first_field=r['steps'][0]['field'], prerequisite_first=r['steps'][0]['field'] == pre,
            left_first=r['steps'][0]['field'] == left, min_cf_margin=min(margins) if margins else None,
            tie_broken=any(s['tie'] for s in r['steps']), prompt_tokens=canvas.prompt_len,
            steps=r['steps'], step0=r['step0']))
    return rows
