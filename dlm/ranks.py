"""Commit ranks over content tokens only (EOS and padding excluded).

A content token's normalized rank is (k-1)/(n-1), where k is its 1-based order
among the n committed content tokens: 0 = committed first, 1 = committed last.
`proposal` scaling (k/n) is also available. A field's rank is the mean over its tokens.
"""


def content_order(steps, content_positions):
    content = set(content_positions)
    return [s['pos'] for s in steps if s['pos'] in content]


def normalized(steps, content_positions, scale='unit'):
    order = content_order(steps, content_positions)
    n = len(order)
    if scale == 'unit':
        return {p: (k / (n - 1) if n > 1 else 0.0) for k, p in enumerate(order)}
    if scale == 'proposal':
        return {p: (k + 1) / n for k, p in enumerate(order)}
    raise ValueError(f'unknown rank scale {scale!r}')


def field_ranks(steps, fields, content_positions, scale='unit'):
    r = normalized(steps, content_positions, scale)
    return {f: sum(r[p] for p in ps) / len(ps) for f, ps in fields.items() if ps and all(p in r for p in ps)}


def first_commit(steps, positions):
    ps = set(positions)
    return next((s['step'] for s in steps if s['pos'] in ps), None)


def within_field_l2r(steps, positions):
    """True if the field's tokens were committed strictly left to right."""
    ps = set(positions)
    order = [s['pos'] for s in steps if s['pos'] in ps]
    return order == sorted(order)
