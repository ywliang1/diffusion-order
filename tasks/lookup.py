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
    V2d V2 plus n decoy mapping rows keyed by the other key column (Phase 1.5b fallback):
        Shared-path adds "h=<H> | b=<F>", Separate-path adds "a=<A> | b=<F>", Direct adds
        filler "d=<G> | e=<F>". Needs sources drawn with COLS8.
A '-nochat' suffix (e.g. 'V1-nochat') renders the same prompt without the chat template.
"""
import random
import re

from dlm.canvas import Field, align
from tasks.exclusion import is_phase1, stopwords

COLS = ('A', 'H', 'B', 'C', 'D', 'E')
COLS8 = COLS + ('F', 'G')
CONDITIONS = ('Direct', 'Shared-path', 'Separate-path')
VARIANTS = ('V1', 'V2', 'V3', 'V4', 'V2d')

HEAD = 'Read the tables and return only the JSON object. No explanation.\n'
V4_LINE = 'Fill field a from a column labeled a and field b from a column labeled b.\n'
TAIL = 'Target key: {q}\nReturn only the JSON object with fields a and b; no explanation.\n'
OUTPUT = ['{"a":"', Field('A'), '","b":"', Field('B'), '"}']

# Decoy mapping rows for V2d: (left column, left label, right column, right label)
DECOY = {
    'Direct': ('G', 'd', 'F', 'e'),
    'Shared-path': ('H', 'h', 'F', 'b'),
    'Separate-path': ('A', 'a', 'F', 'b'),
}

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


def make_source(size, sid, words, seed, cols=COLS):
    """Deterministic source. Draws are repeated (same RNG stream) until the source matches no
    Phase 1 source; `resamples` records how many draws were rejected."""
    rng = random.Random(f'lookup-{seed}-{size}-{sid}')
    resamples = 0
    while True:
        vals = rng.sample(words, len(cols) * size)
        rows = [dict(q=f'k{i:02d}', **{c: vals[len(cols) * i + j] for j, c in enumerate(cols)}) for i in range(size)]
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
    decoy_order = None
    if 'F' in cols:  # interleaving of true and decoy mapping rows for V2d: (row, is_decoy)
        decoy_order = [(i, False) for i in range(size)] + [(i, True) for i in range(size)]
        rng.shuffle(decoy_order)
    return dict(size=size, source_id=sid, seed=seed, rows=rows, target=target, wrong=wrong,
                anchor_order=anchor_order, map_order=map_order, decoy_order=decoy_order, resamples=resamples)


def integrity(source, condition):
    rows, t = source['rows'], source['rows'][source['target']]
    assert len({r['q'] for r in rows}) == len(rows)
    cols = [c for c in rows[0] if c != 'q']
    assert len({r[c] for r in rows for c in cols}) == len(cols) * len(rows)
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
    cols = [('h', 'H'), ('a', 'A')] if base == 'V3' else [('a', 'A'), ('h', 'H')]
    a = [' | '.join([f"key={r['q']}"] + [f'{lab}={r[c]}' for lab, c in cols] + [f'{l4}={r[c4]}']) for r in anchor]
    if base == 'V2d':
        if source.get('decoy_order') is None:
            raise ValueError('V2d needs a source drawn with COLS8')
        dl, dll, dr, drl = DECOY[condition]
        m = [f'{dll}={rows[i][dl]} | {drl}={rows[i][dr]}' if decoy else f'{mll}={rows[i][ml]} | {mrl}={rows[i][mr]}'
             for i, decoy in source['decoy_order']]
    else:
        m = [f'{mll}={r[ml]} | {mrl}={r[mr]}' for r in mapping]
    return 'Anchor:\n' + '\n'.join(a) + '\nMapping:\n' + '\n'.join(m)


def instruction(source, condition, variant):
    base, _ = parse_variant(variant)
    q = source['rows'][source['target']]['q']
    return HEAD + (V4_LINE if base == 'V4' else '') + tables(source, condition, variant) + '\n' + TAIL.format(q=q)


def table_values(source, condition, variant=None):
    """Every value string shown in the tables under this condition (for the error taxonomy)."""
    (c4, _), (ml, _), (mr, _) = LAYOUT[condition]
    vals = set()
    for r in source['rows']:
        vals |= {r['A'], r['H'], r[c4], r[ml], r[mr]}
    if variant is not None and parse_variant(variant)[0] == 'V2d':
        dl, _, dr, _ = DECOY[condition]
        vals |= {r[dl] for r in source['rows']} | {r[dr] for r in source['rows']}
    return vals


# ---------------------------------------------------------------------------------------
# Role x layout x hop design (RQ1 study, Exp 4), V2 row format.
#
# direction 'a': the anchor gives a (a is the prerequisite); direction 'b': the anchor gives b.
#   two-hop: anchor "key=k | <p>=<P> | h=<H> | c=<C>", mapping "a=<A> | b=<B>" (identical text in
#            both directions; read left-to-right or right-to-left)
#   one-hop: anchor "key=k | <p>=<P> | h=<H> | <d>=<D>" (both answers in the row; <p>/<d> = the
#            prerequisite/dependent field of the matched two-hop item), mapping filler "d=<D> | e=<E>"
# layout 'ab' renders {"a":..,"b":..}; layout 'ba' renders {"b":..,"a":..}. Input text never depends
# on layout. Roles name the reference computation of the two-hop item; one-hop items carry the same
# labels for matching (the "direction role") but have no second lookup.
# ---------------------------------------------------------------------------------------
DIRECTIONS = ('a', 'b')
LAYOUTS = ('ab', 'ba')
HOPS = (2, 1)


def rl_roles(direction):
    pre = 'A' if direction == 'a' else 'B'
    return {pre: 'prerequisite', ('B' if pre == 'A' else 'A'): 'dependent'}


def rl_tables(source, direction, hop):
    rows = source['rows']
    anchor = [rows[i] for i in source['anchor_order']]
    mapping = [rows[i] for i in source['map_order']]
    p, pl = ('A', 'a') if direction == 'a' else ('B', 'b')
    d, dl = ('B', 'b') if direction == 'a' else ('A', 'a')
    last = (d, dl) if hop == 1 else ('C', 'c')
    a = [f"key={r['q']} | {pl}={r[p]} | h={r['H']} | {last[1]}={r[last[0]]}" for r in anchor]
    m = [f"a={r['A']} | b={r['B']}" if hop == 2 else f"d={r['D']} | e={r['E']}" for r in mapping]
    return 'Anchor:\n' + '\n'.join(a) + '\nMapping:\n' + '\n'.join(m)


def rl_instruction(source, direction, hop):
    q = source['rows'][source['target']]['q']
    return HEAD + rl_tables(source, direction, hop) + '\n' + TAIL.format(q=q)


def rl_output(layout, direction, k=1):
    roles = rl_roles(direction)
    fa, fb = Field('A', k, role=roles['A']), Field('B', k, role=roles['B'])
    if layout == 'ab':
        return ['{"a":"', fa, '","b":"', fb, '"}']
    if layout == 'ba':
        return ['{"b":"', fb, '","a":"', fa, '"}']
    raise ValueError(f'unknown layout {layout!r}')


def rl_integrity(source, direction, hop):
    rows, t = source['rows'], source['rows'][source['target']]
    assert len({r[c] for r in rows for c in COLS}) == len(COLS) * len(rows)
    if hop == 2:
        key, other = ('A', 'B') if direction == 'a' else ('B', 'A')
        assert [r[other] for r in rows if r[key] == t[key]] == [t[other]]
    return True


def rl_table_values(source, direction, hop):
    vals = set()
    for r in source['rows']:
        vals |= {r['A'], r['B'], r['H']} | ({r['C']} if hop == 2 else {r['D'], r['E']})
    return vals


def multi_token_ok(tok, value, k):
    """value is exactly k tokens bare, after a space, after '=' and inside quotes, with the same ids."""
    enc = lambda x: tok.encode(x, add_special_tokens=False)
    bare = enc(value)
    if len(bare) != k or len(enc(' ' + value)) != k:
        return False
    eq = enc('a=' + value)
    return eq[-k:] == bare and len(eq) == len(enc('a=')) + k and enc('"' + value + '"')[1:-1] == bare


def build_multi_pool(tok, mask_id, base, k, n=3000, seed=0):
    """Stage 3 values: concatenations of k distinct base-pool words that tokenize to exactly k tokens
    in every context and align in both output slots and both layouts. Deterministic for a seed."""
    rng = random.Random(f'multi-{k}-{seed}')
    probe = 'Target key: k00\n'
    out, seen, tries = [], set(), 0
    while len(out) < n:
        tries += 1
        if tries > 50 * n:
            raise ValueError(f'only {len(out)} {k}-token values after {tries} draws')
        v = ''.join(rng.sample(base, k))
        if v in seen or not multi_token_ok(tok, v, k):
            continue
        seen.add(v)
        if all(align(tok, mask_id, probe, rl_output(lay, 'a', k), {'A': v, 'B': v}) for lay in LAYOUTS):
            out.append(v)
    return sorted(out)


# --- Three-field RQ1 design (experiments/rq1_3f): a, b and an independent reference field h -------------
# Input text is the rl_* V2 text except the closing line; the output has three single-token slots in all
# six orders. h is the target row's H, read straight from the anchor row; nothing depends on it.
TAIL3 = 'Target key: {q}\nReturn only the JSON object with fields a, b and h; no explanation.\n'
LAYOUTS3 = ('abh', 'ahb', 'bah', 'bha', 'hab', 'hba')
SLOTS3 = ('first', 'middle', 'last')


def rl3_prompt_words():
    return set(re.findall(r'[a-z]+', (TAIL3 + HEAD).lower()))


def rl3_roles(direction):
    roles = rl_roles(direction)
    roles['H'] = 'independent'
    return roles


def rl3_instruction(source, direction, hop):
    q = source['rows'][source['target']]['q']
    return HEAD + rl_tables(source, direction, hop) + '\n' + TAIL3.format(q=q)


def rl3_output(layout, direction, k=1):
    if layout not in LAYOUTS3:
        raise ValueError(f'unknown layout {layout!r}')
    roles = rl3_roles(direction)
    parts = []
    for i, c in enumerate(layout):
        parts += [('{"' if i == 0 else '","') + c + '":"', Field(c.upper(), k, role=roles[c.upper()])]
    return parts + ['"}']


def rl3_slots(layout):
    return {c.upper(): SLOTS3[i] for i, c in enumerate(layout)}
