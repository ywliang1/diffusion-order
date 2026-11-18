import json
import random

import pytest

from dlm import ranks, scoring
from dlm.canvas import Canvas
from tasks import exclusion

EOS = 10


def test_rank_normalization_excludes_eos():
    # canvas: field A at 2, field B at 3, tail 4..6 where 5 and 6 became EOS
    c = Canvas(ids=[], fields={'A': [2], 'B': [3]}, roles={}, tail=[4, 5, 6], prompt_len=2)
    final = {2: 7, 3: 8, 4: 9, 5: EOS, 6: EOS}
    content = c.content_positions(final_ids=final, end_ids=(EOS,))
    assert content == [2, 3, 4]
    # commit order: EOS first (as CF often does), then B, tail content, A
    steps = [dict(step=i, pos=p) for i, p in enumerate([6, 5, 3, 4, 2])]
    r = ranks.normalized(steps, content)
    assert r == {3: 0.0, 4: 0.5, 2: 1.0}
    assert ranks.field_ranks(steps, c.fields, content) == {'A': 1.0, 'B': 0.0}
    assert ranks.normalized(steps, content, scale='proposal') == {3: 1 / 3, 4: 2 / 3, 2: 1.0}


def test_multi_token_field_rank_is_mean_and_within_field_order():
    steps = [dict(step=i, pos=p) for i, p in enumerate([5, 2, 3, 4])]
    fr = ranks.field_ranks(steps, {'A': [2, 3], 'B': [4, 5]}, [2, 3, 4, 5])
    assert fr == pytest.approx({'A': (1 / 3 + 2 / 3) / 2, 'B': (0 + 1) / 2})
    assert ranks.within_field_l2r(steps, [2, 3]) and not ranks.within_field_l2r(steps, [4, 5])


def test_unknown_rank_scale_raises():
    with pytest.raises(ValueError):
        ranks.normalized([], [], scale='k/n')


def test_scoring_strips_whitespace_and_records_raw():
    s = scoring.score_field(' metal', 'metal')
    assert s['correct'] and not s['correct_raw'] and s['changed_by_norm'] and s['pred_raw'] == ' metal'
    s = scoring.score_field('metal', 'metal')
    assert s['correct'] and not s['changed_by_norm']
    s = scoring.score_field('iron ', 'metal')
    assert not s['correct'] and not s['changed_by_norm']


def test_error_taxonomy():
    rows = [dict(q='k00', A='a0', H='h0', B='b0'), dict(q='k01', A='a1', H='h1', B='b1')]
    t = lambda p: scoring.taxonomy(p, rows, 0, 'B', extra_values=('e9',))
    assert t('b0') == 'correct'
    assert t(' h0') == 'target_row_H'
    assert t('a0') == 'target_row_other'
    assert t('b1') == 'distractor_row_same_field'
    assert t('h1') == 'other_table_value' and t('e9') == 'other_table_value'
    assert t('zebra') == 'non_table'


def test_phase1_sources_are_excluded():
    from phase1.tasks import make_source
    for model in ('llada', 'dream'):
        words = json.loads((exclusion.PHASE1 / f'words-{model}.json').read_text())
        for n, sid in [(4, 0), (8, 117), (16, 199)]:
            s = make_source(n, sid, words, exclusion.PHASE1_SEED)
            t = s['rows'][s['target']]
            assert exclusion.is_phase1(t['A'], t['B'])
            assert exclusion.is_phase1(t['B'], t['A'])  # unordered
            vals = [v for r in s['rows'] for k, v in r.items() if k != 'q']
            assert exclusion.is_phase1('zz_none', 'zz_none2', vals)
        vals = random.Random(exclusion.PHASE1_SEED).sample(words, 40)
        assert exclusion.is_phase1(vals[0], vals[1])  # copy instance 0


def test_fresh_pairs_mostly_not_excluded():
    words = json.loads((exclusion.PHASE1 / 'words-llada.json').read_text())
    rng = random.Random(20261117)
    hits = sum(exclusion.is_phase1(*rng.sample(words, 2)) for _ in range(2000))
    assert hits <= 2


def test_stopwords_cover_template_words():
    sw = exclusion.stopwords('Read the tables and return only the JSON object.')
    assert {'value', 'key', 'left', 'right', 'target', 'the', 'read', 'tables', 'json'} <= sw
