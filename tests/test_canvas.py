"""Canvas building against the frozen Phase 1 renderer, with the real tokenizers (CPU only)."""
import json

import pytest

from dlm.canvas import Field, align, build
from dlm.models import load_tokenizer, mask_id_of, ROOT

PARTS = ['{"a":"', Field('A'), '","b":"', Field('B'), '"}']


@pytest.fixture(scope='module', params=['llada', 'dream'])
def tm(request):
    return request.param, load_tokenizer(request.param), mask_id_of(request.param)


def test_matches_phase1_render(tm):
    from phase1.decoder import render
    name, tok, mask = tm
    inst = 'Read the tables.\nTarget key: k03\n'
    ids, slots = render(tok, mask, inst)
    c = build(tok, mask, inst, PARTS)
    assert c.ids == ids and c.fields == {'A': [slots['A']], 'B': [slots['B']]}


def test_multi_token_fields_and_tail(tm):
    name, tok, mask = tm
    c = build(tok, mask, 'x', ['{"a":"', Field('A', 3), '","b":"', Field('B', 2), '"}'], tail=4)
    assert len(c.fields['A']) == 3 and len(c.fields['B']) == 2
    assert c.tail == list(range(len(c.ids) - 4, len(c.ids)))
    assert all(c.ids[p] == mask for p in c.masked_positions())


def test_align_accepts_single_token_values(tm):
    name, tok, mask = tm
    words = json.loads((ROOT / f'results/phase1/words-{name}.json').read_text())
    g = align(tok, mask, 'x', PARTS, {'A': words[0], 'B': words[1]})
    assert g is not None and len(g['A']) == 1


def test_align_rejects_wrong_length(tm):
    name, tok, mask = tm
    assert align(tok, mask, 'x', PARTS, {'A': 'antidisestablishmentarianism', 'B': 'cat'}) is None


def test_no_template_variant_has_no_chat_markup(tm):
    name, tok, mask = tm
    c = build(tok, mask, 'hello', PARTS, chat=False)
    text = tok.decode(c.ids[:c.prompt_len])
    assert 'assistant' not in text and 'hello' in text


def test_build_chat_masks_whole_response(tm):
    from dlm.canvas import build_chat
    name, tok, mask = tm
    c = build_chat(tok, mask, [{'role': 'system', 'content': 'S'}, {'role': 'user', 'content': 'U'}], 16)
    assert c.tail == list(range(c.prompt_len, c.prompt_len + 16)) and len(c.ids) == c.prompt_len + 16
    assert all(c.ids[p] == mask for p in c.tail) and mask not in c.ids[:c.prompt_len]
    final = list(c.ids)
    final[c.tail[0]], final[c.tail[1]], final[c.tail[2]] = 5, 6, 7
    assert c.content_positions(final, end_ids=(7,)) == c.tail[:2]
