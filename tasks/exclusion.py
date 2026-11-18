"""Phase 1 source fingerprints, and the template-word filter for value pools.

A new source is excluded if (a) its unordered target answer pair {A, B} equals the
target pair of any Phase 1 source or copy instance (either model's pool), or
(b) its full set of table values equals that of a Phase 1 source. Phase 1 sources
are regenerated read-only from `phase1.tasks.make_source` with the exported pools.
"""
import hashlib
import json
import random
import re
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PHASE1 = ROOT / 'results/phase1'
CACHE = Path(__file__).resolve().parent / 'phase1_fingerprints.json'
PHASE1_SEED = 1729
PHASE1_SIZES = (4, 8, 16)
PHASE1_SOURCES = 200
PHASE1_COPY = 20


def value_set_hash(values):
    return hashlib.sha1('\x1f'.join(sorted(values)).encode()).hexdigest()


def pair_key(a, b):
    return '\x1f'.join(sorted((a, b)))


def build_fingerprints():
    from phase1.tasks import make_source  # read-only use of the frozen generator
    pairs, sets = set(), set()
    for model in ('llada', 'dream'):
        words = json.loads((PHASE1 / f'words-{model}.json').read_text())
        for n in PHASE1_SIZES:
            for sid in range(PHASE1_SOURCES):
                s = make_source(n, sid, words, PHASE1_SEED)
                t = s['rows'][s['target']]
                pairs.add(pair_key(t['A'], t['B']))
                sets.add(value_set_hash([v for r in s['rows'] for k, v in r.items() if k != 'q']))
        vals = random.Random(PHASE1_SEED).sample(words, 2 * PHASE1_COPY)
        for sid in range(PHASE1_COPY):
            pairs.add(pair_key(vals[2 * sid], vals[2 * sid + 1]))
    return dict(target_pairs=sorted(pairs), value_sets=sorted(sets))


@lru_cache(maxsize=1)
def fingerprints():
    if not CACHE.exists():
        CACHE.write_text(json.dumps(build_fingerprints()) + '\n')
    d = json.loads(CACHE.read_text())
    return frozenset(d['target_pairs']), frozenset(d['value_sets'])


def is_phase1(target_a, target_b, table_values=None):
    pairs, sets = fingerprints()
    if pair_key(target_a, target_b) in pairs:
        return True
    return table_values is not None and value_set_hash(table_values) in sets


# Words that occur in prompts, headers, labels or instructions of any stage, plus generic
# function words. None of these may be used as a table value.
BASE_STOPWORDS = {
    'value', 'values', 'key', 'keys', 'left', 'right', 'target', 'the', 'and', 'with', 'only', 'return',
    'read', 'tables', 'table', 'anchor', 'mapping', 'json', 'object', 'fields', 'field', 'explanation',
    'copy', 'input', 'output', 'row', 'rows', 'same', 'both', 'from', 'come', 'comes', 'answer', 'query',
    'true', 'false', 'null', 'none', 'yes', 'not', 'for', 'are', 'its', 'this', 'that', 'each', 'one', 'two',
}


def template_words(*texts):
    return {w.lower() for t in texts for w in re.findall(r'[A-Za-z]+', t)}


def stopwords(*texts):
    return BASE_STOPWORDS | template_words(*texts)
