"""Lookup tasks for Phase 1.5 onward: sources, table formats and prompts.

A source has n rows with columns q (key), A, H, B, C, D, E; every value is a distinct
single-token word. One target row is queried. Conditions decide where b is found:

    Direct         anchor row's 4th column is B; the mapping table is inert filler (D -> E)
    Shared-path    anchor 4th column is filler C; mapping A -> B
    Separate-path  anchor 4th column is filler C; mapping H -> B

The anchor and mapping row orders are drawn once per source and shared by all
conditions and variants, so those comparisons are paired.

Formats (variants):
    V1  space-separated rows, column labels match the answer keys: "Anchor (key a h b):"
    V2  explicit rows: "key=k02 | a=frequency | h=detect | b=notes"
    V3  V2 with columns ordered key, h, a, b (H no longer next to b)
    V4  V1 plus one instruction line naming which column fills which field
A '-nochat' suffix (e.g. 'V1-nochat') renders the same prompt without the chat template.
"""
import random
import re

from dlm.canvas import Field, align
from tasks.exclusion import is_phase1, stopwords

COLS = ('A', 'H', 'B', 'C', 'D', 'E')
CONDITIONS = ('Direct', 'Shared-path', 'Separate-path')
VARIANTS = ('V1', 'V2', 'V3', 'V4')

HEAD = 'Read the tables and return only the JSON object. No explanation.\n'
V4_LINE = 'Fill field a from a column labeled a and field b from a column labeled b.\n'
TAIL = 'Target key: {q}\nReturn only the JSON object with fields a and b; no explanation.\n'
OUTPUT = ['{"a":"', Field('A'), '","b":"', Field('B'), '"}']

# (anchor 4th column, mapping left, mapping right) as (source column, label)
LAYOUT = {
    'Direct': (('B', 'b'), ('D', 'd'), ('E', 'e')),
    'Shared-path': (('C', 'c'), ('A', 'a'), ('B', 'b')),
    'Separate-path': (('C', 'c'), ('H', 'h'), ('B', 'b')),
}


def parse_variant(v):
    base, _, suffix = v.partition('-')
    if base not in VARIANTS or suffix not in ('', 'nochat'):
        raise ValueError(f'unknown variant {v!r}')
    return base, suffix != 'nochat'


def all_prompt_text():
    probe = HEAD + V4_LINE + TAIL + 'Anchor Mapping key '
    return probe


def single_token_word(tok, word):
    """word is one token bare, with a leading space, and right after '=' (as in 'a=word')."""
    enc = lambda s: tok.encode(s, add_special_tokens=False)
    bare = enc(word)
    if len(bare) != 1 or len(enc(' ' + word)) != 1:
        return False
    eq = enc('a=' + word)
    return eq[-1:] == bare and len(eq) == len(enc('a=')) + 1


def build_pool(tok, mask_id, minimum=1000):
    """Plain lowercase single-token words usable in every context of every variant, minus
    prompt words and the model's chat-template words. Output-slot alignment is checked with and without the chat template."""
    template = tok.apply_chat_template([{'role': 'user', 'content': 'x'}], tokenize=False, add_generation_prompt=True)
    stop = stopwords(all_prompt_text(), template)
    seen, cands = set(), []
    for tid in range(len(tok)):
        if tid == mask_id:
            continue
        w = tok.decode([tid], skip_special_tokens=False)
        if w in seen or not re.fullmatch(r'[a-z]{3,9}', w) or w in stop:
            continue
        seen.add(w)
        if single_token_word(tok, w):
            cands.append(w)
    probe = 'Target key: k00\n'
    anchor = next(w for w in cands if all(align(tok, mask_id, probe, OUTPUT, {'A': w, 'B': w}, chat=c) for c in (True, False)))
    pool = [w for w in cands
            if all(align(tok, mask_id, probe, OUTPUT, g, chat=c)
                   for c in (True, False) for g in ({'A': w, 'B': anchor}, {'A': anchor, 'B': w}))]
    if len(pool) < minimum:
        raise ValueError(f'only {len(pool)} usable values')
    return sorted(pool)


def make_source(size, sid, words, seed):
    """Deterministic source. Draws are repeated (same RNG stream) until the source matches no
    Phase 1 source; `resamples` records how many draws were rejected."""
    rng = random.Random(f'lookup-{seed}-{size}-{sid}')
    resamples = 0
    while True:
        vals = rng.sample(words, len(COLS) * size)
        rows = [dict(q=f'k{i:02d}', **{c: vals[len(COLS) * i + j] for j, c in enumerate(COLS)}) for i in range(size)]
        target = rng.randrange(size)
        t = rows[target]
        if not is_phase1(t['A'], t['B'], [v for r in rows for k, v in r.items() if k != 'q']):
            break
        resamples += 1
    wrong = rng.choice([i for i in range(size) if i != target])
    anchor_order = list(range(size))
    map_order = list(range(size))
    rng.shuffle(anchor_order)
    rng.shuffle(map_order)
    return dict(size=size, source_id=sid, seed=seed, rows=rows, target=target, wrong=wrong,
                anchor_order=anchor_order, map_order=map_order, resamples=resamples)


def integrity(source, condition):
    rows, t = source['rows'], source['rows'][source['target']]
    assert len({r['q'] for r in rows}) == len(rows)
    assert len({r[c] for r in rows for c in COLS}) == len(COLS) * len(rows)
    key = {'Shared-path': 'A', 'Separate-path': 'H'}.get(condition)
    if key:
        assert [r['B'] for r in rows if r[key] == t[key]] == [t['B']]
    return True


def tables(source, condition, variant):
    base, _ = parse_variant(variant)
    (c4, l4), (ml, mll), (mr, mrl) = LAYOUT[condition]
    rows = source['rows']
    anchor = [rows[i] for i in source['anchor_order']]
    mapping = [rows[i] for i in source['map_order']]
    if base in ('V1', 'V4'):
        a = [f"{r['q']} {r['A']} {r['H']} {r[c4]}" for r in anchor]
        m = [f'{r[ml]} {r[mr]}' for r in mapping]
        return (f'Anchor (key a h {l4}):\n' + '\n'.join(a) + f'\nMapping ({mll} {mrl}):\n' + '\n'.join(m))
    cols = [('a', 'A'), ('h', 'H')] if base == 'V2' else [('h', 'H'), ('a', 'A')]
    a = [' | '.join([f"key={r['q']}"] + [f'{lab}={r[c]}' for lab, c in cols] + [f'{l4}={r[c4]}']) for r in anchor]
    m = [f'{mll}={r[ml]} | {mrl}={r[mr]}' for r in mapping]
    return 'Anchor:\n' + '\n'.join(a) + '\nMapping:\n' + '\n'.join(m)


def instruction(source, condition, variant):
    base, _ = parse_variant(variant)
    q = source['rows'][source['target']]['q']
    return HEAD + (V4_LINE if base == 'V4' else '') + tables(source, condition, variant) + '\n' + TAIL.format(q=q)


def table_values(source, condition):
    """Every value string shown in the tables under this condition (for the error taxonomy)."""
    (c4, _), (ml, _), (mr, _) = LAYOUT[condition]
    vals = set()
    for r in source['rows']:
        vals |= {r['A'], r['H'], r[c4], r[ml], r[mr]}
    return vals
