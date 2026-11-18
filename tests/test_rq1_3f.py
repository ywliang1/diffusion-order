import pytest

from tasks import lookup


def test_three_field_layouts_cover_all_orders():
    assert sorted(lookup.LAYOUTS3) == sorted({''.join(p) for p in __import__('itertools').permutations('abh')})


def test_three_field_output_and_roles():
    parts = lookup.rl3_output('hba', 'a')
    fields = [p for p in parts if not isinstance(p, str)]
    assert [f.name for f in fields] == ['H', 'B', 'A']
    assert {f.name: f.role for f in fields} == {'A': 'prerequisite', 'B': 'dependent', 'H': 'independent'}
    assert parts[0] == '{"h":"' and parts[-1] == '"}'
    assert lookup.rl3_slots('hba') == {'H': 'first', 'B': 'middle', 'A': 'last'}


def test_unknown_three_field_layout_raises():
    with pytest.raises(ValueError):
        lookup.rl3_output('ab', 'a')


def test_three_field_prompt_words_excluded():
    assert {'and', 'h', 'fields'} <= lookup.rl3_prompt_words()
