"""Commitment schedules. Each picks one masked position per forward pass.

Names: L2R, R2L, random-s<k>, CF, A-first, B-first, PF, DF. Anything else raises.
Field-first schedules (A-first, B-first, PF, DF) use the CF rule inside the
current field, then fall through to CF over whatever remains (e.g. an EOS tail).
CF ties are broken by `tie_rng.choice` over the tied positions in position order,
called at every CF step (this matches Phase 1's RNG consumption exactly).
"""
import random
import re

FIXED = ('L2R', 'R2L', 'CF', 'A-first', 'B-first', 'PF', 'DF')


def parse(name):
    if name in FIXED:
        return name, None
    m = re.fullmatch(r'random-s(\d+)', name or '')
    if m:
        return 'random', int(m.group(1))
    raise ValueError(f'unknown order {name!r}')


def cf_pick(candidates, conf, tie_rng):
    """-> (position, tie_broken, margin to the best other candidate or None)."""
    best = max(conf[p] for p in candidates)
    winners = [p for p in sorted(candidates) if conf[p] == best]
    pos = tie_rng.choice(winners)
    others = [conf[p] for p in candidates if p != pos]
    return pos, len(winners) > 1, (best - max(others)) if others else None


class Schedule:
    """`choose(remaining, conf, field_of)` -> (position, tie_broken, choice margin or None).

    The choice margin is the chosen slot's confidence minus the best other slot this
    schedule could have picked (None for L2R/R2L/random or a single candidate)."""

    def __init__(self, name, roles=None, tie_seed=0, order_seed_base=0):
        self.name = name
        self.kind, k = parse(name)
        self.tie_rng = random.Random(tie_seed)
        self.order_rng = random.Random(order_seed_base * 1000003 + k) if self.kind == 'random' else None
        self.priority = None
        if self.kind == 'A-first':
            self.priority = ['A', 'B']
        elif self.kind == 'B-first':
            self.priority = ['B', 'A']
        elif self.kind in ('PF', 'DF'):
            roles = roles or {}
            pre = [f for f, r in roles.items() if r == 'prerequisite']
            dep = [f for f, r in roles.items() if r == 'dependent']
            if len(pre) != 1 or len(dep) != 1:
                raise ValueError(f'{self.kind} needs exactly one prerequisite and one dependent field, got {roles}')
            self.priority = pre + dep if self.kind == 'PF' else dep + pre

    @property
    def needs_conf(self):
        return self.kind not in ('L2R', 'R2L', 'random')

    def choose(self, remaining, conf, field_of):
        remaining = sorted(remaining)
        if self.kind == 'L2R':
            return remaining[0], False, None
        if self.kind == 'R2L':
            return remaining[-1], False, None
        if self.kind == 'random':
            return self.order_rng.choice(remaining), False, None
        cands = remaining
        if self.priority:
            for f in self.priority:
                inside = [p for p in remaining if field_of.get(p) == f]
                if inside:
                    cands = inside
                    break
        return cf_pick(cands, conf, self.tie_rng)


def make(name, roles=None, tie_seed=0, order_seed_base=0):
    return Schedule(name, roles=roles, tie_seed=tie_seed, order_seed_base=order_seed_base)
