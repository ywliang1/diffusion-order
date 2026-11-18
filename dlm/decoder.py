"""One-commit-per-forward-pass greedy decoder over the whole canvas as one block.

Greedy argmax over the full vocabulary with only the mask token excluded.
Committed tokens are never rewritten. Several jobs with equal canvas length and
equal step count can run in lockstep as one batch (no padding, no attention mask);
each row keeps its own schedule and tie RNG.
"""
import torch

from dlm.models import slot_logits


def slot_probs(logits_rows, mask_id):
    """logits_rows: [k, V] -> fp32 probabilities with the mask token excluded."""
    z = logits_rows.float().clone()
    z[:, mask_id] = -float('inf')
    return torch.softmax(z, dim=-1)


class Job:
    def __init__(self, ids, positions, schedule, field_of=None, roles=None, step0_positions=None):
        self.ids = list(ids)
        self.positions = sorted(positions)
        self.schedule = schedule
        self.field_of = field_of or {}
        self.roles = roles or {}
        self.step0_positions = step0_positions if step0_positions is not None else self.positions


def step0_key(job, p):
    """Field name for single-token fields, 'field#k' for the k-th token of a longer field, else the position."""
    f = job.field_of.get(p)
    if f is None:
        return str(p)
    mine = [q for q in job.step0_positions if job.field_of.get(q) == f]
    return f if len(mine) == 1 else f'{f}#{mine.index(p)}'


@torch.no_grad()
def decode(bundle, jobs, topk=5):
    """Run jobs in lockstep. Returns one dict per job: final ids, per-step log, step-0 top-k."""
    if not jobs:
        return []
    L = len(jobs[0].ids)
    n = len(jobs[0].positions)
    if any(len(j.ids) != L or len(j.positions) != n for j in jobs):
        raise ValueError('batched jobs need equal canvas length and step count')
    tok, mask_id = bundle.tok, bundle.mask_id
    x = torch.tensor([j.ids for j in jobs], device=bundle.device)
    for j in jobs:
        for p in j.positions:
            if j.ids[p] != mask_id:
                raise ValueError(f'decode position {p} is not masked')
    remaining = [list(j.positions) for j in jobs]
    out = [dict(steps=[], step0={}) for _ in jobs]
    committed = [dict() for _ in jobs]
    for step in range(n):
        logits = slot_logits(bundle.model, x, bundle.shifted)
        for b, j in enumerate(jobs):
            rem = remaining[b]
            probs = slot_probs(logits[b, rem], mask_id)
            top = torch.topk(probs, max(topk, 2), dim=-1)
            conf = {p: float(top.values[i, 0]) for i, p in enumerate(rem)}
            if step == 0:
                for i, p in enumerate(rem):
                    if p in j.step0_positions:
                        out[b]['step0'][step0_key(j, p)] = dict(pos=p, top5_ids=top.indices[i, :topk].tolist(),
                                                    top5_tokens=[tok.decode([t]) for t in top.indices[i, :topk].tolist()],
                                                    top5_probs=top.values[i, :topk].tolist())
            pos, tie = j.schedule.choose(rem, conf, j.field_of)
            i = rem.index(pos)
            tid = int(top.indices[i, 0])
            ranked = sorted(conf.values(), reverse=True)
            others = [conf[p] for p in rem if p != pos]
            if int(x[b, pos]) != mask_id:
                raise RuntimeError('attempt to rewrite a committed token')
            x[b, pos] = tid
            committed[b][pos] = tid
            rem.remove(pos)
            out[b]['steps'].append(dict(
                step=step, pos=pos, field=j.field_of.get(pos), role=j.roles.get(j.field_of.get(pos)),
                token_id=tid, token=tok.decode([tid]), prob=conf[pos],
                top5_ids=top.indices[i, :topk].tolist(), top5_probs=top.values[i, :topk].tolist(),
                tok_margin=float(top.values[i, 0] - top.values[i, 1]),
                cf_margin=(ranked[0] - ranked[1]) if len(ranked) > 1 else None,
                choice_margin=(conf[pos] - max(others)) if others else None,
                tie=tie))
    final = x.tolist()
    for b, j in enumerate(jobs):
        for p, t in committed[b].items():
            if final[b][p] != t:
                raise RuntimeError('committed token changed')
        out[b]['ids'] = final[b]
    return out


def decode_one(bundle, job, topk=5):
    return decode(bundle, [job], topk)[0]
