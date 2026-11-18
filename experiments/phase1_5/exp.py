"""Phase 1.5: lookup prompts with Direct/Shared/Separate conditions (Exp 2 design) and the
prefilled-A intervention (Exp 3 design), under prompt variants V1-V4 (+ '-nochat').

Config keys: split, seed, sizes, sources, variants, exps ([2] or [2, 3]).
run_id: <model>-<split>-<variant>-e<exp>-n<size>-s<sid>-<condition>-<order>
"""
import json

from dlm import schedules
from dlm.canvas import build
from dlm.decoder import Job, decode
from dlm.models import ROOT
from dlm.scoring import score_field, taxonomy
from tasks import lookup

ORDERS = ('A-first', 'B-first', 'CF')
BRANCHES = ('Masked', 'Gold', 'Predicted', 'Wrong')
POOL_DIR = ROOT / 'results/phase1_5'


def pool(tok, mask_id, name):
    path = POOL_DIR / f'pool-{name}.json'
    if path.exists():
        return json.loads(path.read_text())
    words = lookup.build_pool(tok, mask_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(words) + '\n')
    return words


def prepare(tok, mask_id, name, cfg):
    return dict(tok=tok, mask_id=mask_id, name=name, cfg=cfg, words=pool(tok, mask_id, name))


def cells(c, name):
    """(variant, size) cells to run: `per_model` (frozen choice per model) overrides variants x sizes;
    `max_size` caps sizes per variant (e.g. V2d prompts must fit LLaDA's 4,096 tokens)."""
    if 'per_model' in c:
        pm = c['per_model'][name]
        return [(pm['variant'], pm['size'])]
    caps = c.get('max_size', {})
    return [(v, n) for v in c['variants'] for n in c['sizes'] if n <= caps.get(v, n)]


def jobs(ctx):
    c, name = ctx['cfg'], ctx['name']
    out = []
    for v, size in cells(c, name):
        lookup.parse_variant(v)
        for exp in c['exps']:
            conds = lookup.CONDITIONS if exp == 2 else ('Shared-path', 'Separate-path')
            arms = ORDERS if exp == 2 else BRANCHES
            for sid in range(c['sources']):
                for cond in conds:
                    for arm in arms:
                        out.append(dict(run_id=f"{name}-{c['split']}-{v}-e{exp}-n{size}-s{sid}-{cond}-{arm}",
                                        variant=v, exp=exp, size=size, sid=sid, condition=cond, order=arm,
                                        group=f"{v}-e{exp}-n{size}-s{sid}-{cond}"))
    return out


def shown_rows(source, condition, variant):
    (c4, _), (ml, _), (mr, _) = lookup.LAYOUT[condition]
    keep = {'q', 'A', 'H', 'B', c4, ml, mr}
    if lookup.parse_variant(variant)[0] == 'V2d':
        dl, _, dr, _ = lookup.DECOY[condition]
        keep |= {dl, dr}
    return [{k: v for k, v in r.items() if k in keep} for r in source['rows']]


def base_row(j, source, canvas, ctx):
    t = source['rows'][source['target']]
    return dict(run_id=j['run_id'], split=ctx['cfg']['split'], variant=j['variant'], experiment=j['exp'],
                table_size=j['size'], source_id=j['sid'], condition=j['condition'], order=j['order'],
                target=dict(t), target_index=source['target'], resamples=source['resamples'],
                prompt_tokens=canvas.prompt_len, canvas_tokens=len(canvas.ids))


def score(row, pred, source, condition, variant):
    rows = shown_rows(source, condition, variant)
    t = source['rows'][source['target']]
    row['fields'] = {f: score_field(pred[f], t[f]) for f in pred}
    row['taxonomy'] = {f: taxonomy(pred[f], rows, source['target'], f) for f in pred}
    row['A_correct'] = row['fields']['A']['correct'] if 'A' in row['fields'] else None
    row['B_correct'] = row['fields']['B']['correct']
    row['both_correct'] = bool(row['A_correct']) and row['B_correct']


def execute(bundle, ctx, group, batch=False):
    tok, mask_id = bundle.tok, bundle.mask_id
    j0 = group[0]
    base, chat = lookup.parse_variant(j0['variant'])
    seed = ctx['cfg']['seed']
    cols = lookup.COLS8 if ctx['cfg'].get('cols8') else lookup.COLS
    source = lookup.make_source(j0['size'], j0['sid'], ctx['words'], seed, cols=cols)
    lookup.integrity(source, j0['condition'])
    canvas = build(tok, mask_id, lookup.instruction(source, j0['condition'], j0['variant']), lookup.OUTPUT, chat=chat)
    fo = canvas.field_of()
    pA, pB = canvas.fields['A'][0], canvas.fields['B'][0]
    tie_seed = seed + j0['sid'] + j0['size'] * 1000
    rows = []
    if j0['exp'] == 2:
        for j in group:
            r = decode(bundle, [Job(canvas.ids, [pA, pB], schedules.make(j['order'], tie_seed=tie_seed), fo)])[0]
            row = base_row(j, source, canvas, ctx)
            score(row, {'A': tok.decode([r['ids'][pA]]), 'B': tok.decode([r['ids'][pB]])}, source, j['condition'], j['variant'])
            row.update(first_field=r['steps'][0]['field'], tie_broken=any(s['tie'] for s in r['steps']),
                       steps=r['steps'], step0=r['step0'])
            rows.append(row)
        return rows
    # Exp 3: initial A from the fully masked canvas, then B with A held per branch.
    init = decode(bundle, [Job(canvas.ids, [pA], schedules.make('A-first', tie_seed=tie_seed), fo)])[0]
    init_A = tok.decode([init['ids'][pA]])
    t, wrong = source['rows'][source['target']], source['rows'][source['wrong']]
    for j in group:
        held = {'Masked': None, 'Gold': t['A'], 'Predicted': init_A, 'Wrong': wrong['A']}[j['order']]
        ids = list(canvas.ids)
        if held is not None:
            tid = tok.encode(held, add_special_tokens=False)
            if len(tid) != 1:
                raise ValueError(f'held value not single token: {held!r}')
            ids[pA] = tid[0]
        r = decode(bundle, [Job(ids, [pB], schedules.make('B-first', tie_seed=tie_seed), fo)])[0]
        row = base_row(j, source, canvas, ctx)
        pred_B = tok.decode([r['ids'][pB]])
        score(row, {'B': pred_B}, source, j['condition'], j['variant'])
        alt = wrong['B'] if j['order'] == 'Wrong' else None
        row.update(held_A=held, initial_A=score_field(init_A, t['A']), alternative_B=alt,
                   B_matches_alternative=(pred_B.strip() == alt if alt is not None else None),
                   first_field='B', tie_broken=any(s['tie'] for s in r['steps']), steps=r['steps'], step0=r['step0'])
        rows.append(row)
    return rows
