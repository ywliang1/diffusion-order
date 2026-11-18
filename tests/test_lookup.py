import json

import pytest

from dlm.models import ROOT
from tasks import lookup
from tasks.exclusion import is_phase1


@pytest.fixture(scope='module')
def words():
    return json.loads((ROOT / 'results/phase1_5/pool-llada.json').read_text())


def test_source_is_deterministic_and_excludes_phase1(words):
    a, b = lookup.make_source(8, 3, words, 15001), lookup.make_source(8, 3, words, 15001)
    assert a == b
    t = a['rows'][a['target']]
    assert not is_phase1(t['A'], t['B'])
    assert lookup.make_source(8, 3, words, 15002) != a


def test_conditions_share_row_orders_and_lengths(words):
    s = lookup.make_source(4, 0, words, 15001, cols=lookup.COLS8)
    for v in lookup.VARIANTS:
        texts = [lookup.tables(s, c, v) for c in lookup.CONDITIONS]
        assert len({t.count('\n') for t in texts}) == 1
        # same anchor key order in every condition
        keys = [[ln.split()[0].replace('key=', '') for ln in t.split('\n') if ln.startswith(('k', 'key='))] for t in texts]
        assert keys[0] == keys[1] == keys[2]


def test_formats(words):
    s = lookup.make_source(4, 0, words, 15001)
    r = s['rows'][s['target']]
    assert f"{r['q']} {r['A']} {r['H']} {r['B']}" in lookup.tables(s, 'Direct', 'V1')
    assert 'Anchor (key a h b):' in lookup.tables(s, 'Direct', 'V1')
    assert 'Anchor (key a h c):' in lookup.tables(s, 'Shared-path', 'V1')
    assert 'Mapping (h b):' in lookup.tables(s, 'Separate-path', 'V1')
    assert f"key={r['q']} | a={r['A']} | h={r['H']} | b={r['B']}" in lookup.tables(s, 'Direct', 'V2')
    assert f"key={r['q']} | h={r['H']} | a={r['A']} | b={r['B']}" in lookup.tables(s, 'Direct', 'V3')
    assert f"a={r['A']} | b={r['B']}" in lookup.tables(s, 'Shared-path', 'V2')
    assert lookup.V4_LINE in lookup.instruction(s, 'Direct', 'V4')
    assert lookup.V4_LINE not in lookup.instruction(s, 'Direct', 'V1')
    assert lookup.instruction(s, 'Direct', 'V1') == lookup.instruction(s, 'Direct', 'V1-nochat')


def test_unknown_variant_raises():
    for bad in ['V5', 'v1', 'V1-chat', '']:
        with pytest.raises(ValueError):
            lookup.parse_variant(bad)
    assert lookup.parse_variant('V3-nochat') == ('V3', False)


def test_pool_has_no_template_words(words):
    from tasks.exclusion import stopwords
    assert not set(words) & stopwords(lookup.all_prompt_text())
    assert not set(words) & {'user', 'header', 'start', 'end'}  # LLaDA's own chat-template words


def test_v2d_adds_labeled_decoy_rows(words):
    s = lookup.make_source(8, 0, words, 15011, cols=lookup.COLS8)
    r = s['rows'][s['target']]
    sh = lookup.tables(s, 'Shared-path', 'V2d')
    assert f"a={r['A']} | b={r['B']}" in sh and f"h={r['H']} | b={r['F']}" in sh
    se = lookup.tables(s, 'Separate-path', 'V2d')
    assert f"h={r['H']} | b={r['B']}" in se and f"a={r['A']} | b={r['F']}" in se
    for c in lookup.CONDITIONS:
        assert lookup.tables(s, c, 'V2d').count('\n') == 1 + 8 + 1 + 16 - 1
    # V2 on the same 8-column source is unchanged in shape
    assert lookup.tables(s, 'Shared-path', 'V2').count('\n') == 1 + 8 + 1 + 8 - 1
    with pytest.raises(ValueError):
        lookup.tables(lookup.make_source(8, 0, words, 15011), 'Direct', 'V2d')
