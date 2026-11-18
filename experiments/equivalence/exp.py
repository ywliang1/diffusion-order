"""Replay Phase 1 Exp 1-3 through the new dlm stack (equivalence check).

Prompts, sources, run_ids and tie seeds follow phase1/run.py exactly. The frozen
phase1 config, task generator and exported word pools are read, never written.
"""
import json

import yaml

from dlm import schedules
from dlm.canvas import Field, build
from dlm.decoder import Job, decode
from dlm.models import ROOT
from dlm.scoring import score_field

P1 = yaml.safe_load((ROOT / 'phase1/config.yaml').read_text())
PARTS = ['{"a":"', Field('A'), '","b":"', Field('B'), '"}']


def prepare(tok, mask_id, name, cfg):
    words = json.loads((ROOT / f'results/phase1/words-{name}.json').read_text())
    return dict(tok=tok, mask_id=mask_id, name=name, cfg=cfg, words=words)


def jobs(ctx):
    from phase1.tasks import make_source
    import random
    name, seed, n = ctx['name'], P1['seed'], ctx['cfg'].get('sources', 200)
    out = []
    for exp in ctx['cfg']['exps']:
        if exp == 1:
            vals = random.Random(seed).sample(ctx['words'], 40)
            for sid in range(20):
                for order in ['A-first', 'B-first', 'CF']:
                    out.append(dict(run_id=f'{name}-e1-n0-s{sid}-Copy-{order}', exp=1, size=0, sid=sid, condition='Copy',
                                    order=order, A=vals[2 * sid], B=vals[2 * sid + 1], group=f'e1-s{sid}'))
            continue
        for size in P1['sizes']:
            for sid in range(n):
                for cond in (['Direct', 'Shared-path', 'Separate-path'] if exp == 2 else ['Shared-path', 'Separate-path']):
                    for order in (['A-first', 'B-first', 'CF'] if exp == 2 else ['Masked', 'Gold', 'Predicted', 'Wrong']):
                        out.append(dict(run_id=f'{name}-e{exp}-n{size}-s{sid}-{cond}-{order}', exp=exp, size=size, sid=sid,
                                        condition=cond, order=order, group=f'e{exp}-n{size}-s{sid}-{cond}'))
    return out


def instruction(job, source):
    if job['exp'] == 1:
        return P1['copy_prompt_template'].format(A=job['A'], B=job['B']).strip()
    from phase1.tasks import tables
    return P1['prompt_template'].format(tables=tables(source, job['condition'], P1['seed']),
                                        target=source['rows'][source['target']]['q'])


def phase1_view(steps):
    return [dict(slot=s['field'], token=s['token'], token_id=s['token_id'], prob=s['prob']) for s in steps]


def execute(bundle, ctx, group, batch=False):
    from phase1.tasks import make_source, integrity
    tok, mask_id = bundle.tok, bundle.mask_id
    j0 = group[0]
    source = None
    if j0['exp'] == 1:
        gold_A, gold_B = j0['A'], j0['B']
    else:
        source = make_source(j0['size'], j0['sid'], ctx['words'], P1['seed'])
        integrity(source, j0['condition'])
        t = source['rows'][source['target']]
        gold_A, gold_B = t['A'], t['B']
    canvas = build(tok, mask_id, instruction(j0, source), PARTS)
    fo = canvas.field_of()
    tie_seed = P1['seed'] + j0['sid'] + j0['size'] * 1000
    pA, pB = canvas.fields['A'][0], canvas.fields['B'][0]
    rows = []
    if j0['exp'] in (1, 2):
        js = [Job(canvas.ids, [pA, pB], schedules.make(j['order'], tie_seed=tie_seed), fo) for j in group]
        res = decode(bundle, js) if batch else [decode(bundle, [x])[0] for x in js]
        for j, r in zip(group, res):
            pred = {f: tok.decode([r['ids'][p]]) for f, p in (('A', pA), ('B', pB))}
            rows.append(dict(run_id=j['run_id'], experiment=j['exp'], table_size=j['size'], source_id=j['sid'],
                             condition=j['condition'], order=j['order'],
                             fields=dict(A=score_field(pred['A'], gold_A), B=score_field(pred['B'], gold_B)),
                             predicted_A=pred['A'], predicted_B=pred['B'], first_field=r['steps'][0]['field'],
                             tie_broken=any(s['tie'] for s in r['steps']), steps=r['steps'], step0=r['step0'],
                             phase1_steps=phase1_view(r['steps'])))
        return rows
    # Exp 3: initial A from the fully masked canvas, then B under each held-A branch.
    init = decode(bundle, [Job(canvas.ids, [pA], schedules.make('A-first', tie_seed=tie_seed), fo)])[0]
    init_A = tok.decode([init['ids'][pA]])
    wrong = source['rows'][source['wrong']]
    js = []
    for j in group:
        held = {'Masked': None, 'Gold': gold_A, 'Predicted': init_A, 'Wrong': wrong['A']}[j['order']]
        ids = list(canvas.ids)
        if held is not None:
            tid = tok.encode(held, add_special_tokens=False)
            if len(tid) != 1:
                raise ValueError(f'held value not single token: {held!r}')
            ids[pA] = tid[0]
        js.append((j, held, Job(ids, [pB], schedules.make('B-first', tie_seed=tie_seed), fo)))
    res = decode(bundle, [x[2] for x in js]) if batch else [decode(bundle, [x[2]])[0] for x in js]
    for (j, held, _), r in zip(js, res):
        pred_B = tok.decode([r['ids'][pB]])
        alt = wrong['B'] if j['order'] == 'Wrong' else None
        rows.append(dict(run_id=j['run_id'], experiment=3, table_size=j['size'], source_id=j['sid'],
                         condition=j['condition'], order=j['order'], held_A=held, alternative_B=alt,
                         fields=dict(A=score_field(init_A, gold_A), B=score_field(pred_B, gold_B)),
                         predicted_A=init_A, predicted_B=pred_B, first_field='B',
                         B_matches_alternative=(pred_B == alt if alt is not None else None),
                         tie_broken=any(s['tie'] for s in r['steps']), steps=r['steps'], step0=r['step0'],
                         phase1_steps=phase1_view(r['steps'])))
    return rows
