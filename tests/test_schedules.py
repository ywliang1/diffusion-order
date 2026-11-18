import pytest

from dlm import schedules
from dlm.decoder import Job, decode
from tests.fakes import MASK, bundle

# Toy canvas: positions 0-1 prompt, 2-3 field A, 4 literal, 5-6 field B, 7 tail.
IDS = [1, 2, MASK, MASK, 3, MASK, MASK, MASK]
FIELD_OF = {2: 'A', 3: 'A', 5: 'B', 6: 'B'}
ROLES = {'A': 'dependent', 'B': 'prerequisite'}
POS = [2, 3, 5, 6, 7]
# Confidence: 6 > 3 > 7 > 2 > 5
CONF = {2: 2.0, 3: 6.0, 5: 1.0, 6: 8.0, 7: 4.0}


def order(name, conf=CONF):
    b = bundle(conf)
    r = decode(b, [Job(IDS, POS, schedules.make(name, roles=ROLES, tie_seed=1), FIELD_OF, ROLES)])[0]
    return [s['pos'] for s in r['steps']]


def test_l2r_and_r2l():
    assert order('L2R') == [2, 3, 5, 6, 7]
    assert order('R2L') == [7, 6, 5, 3, 2]


def test_cf_follows_confidence():
    assert order('CF') == [6, 3, 7, 2, 5]


def test_field_first_orders_use_cf_inside_fields():
    assert order('A-first') == [3, 2, 6, 5, 7]
    assert order('B-first') == [6, 5, 3, 2, 7]
    assert order('PF') == [6, 5, 3, 2, 7]   # B is the prerequisite
    assert order('DF') == [3, 2, 6, 5, 7]


def test_random_is_seeded_permutation():
    a, b, c = order('random-s0'), order('random-s0'), order('random-s1')
    assert a == b and sorted(a) == POS and sorted(c) == POS
    assert a != c


def test_unknown_order_raises():
    for bad in ['L2R ', 'l2r', 'random', 'random-0', 'prereq-first', '', None]:
        with pytest.raises(ValueError):
            schedules.make(bad)


def test_pf_requires_roles():
    with pytest.raises(ValueError):
        schedules.make('PF', roles={'A': 'dependent'})


def test_cf_ties_use_seeded_rng_and_flag():
    tie = {2: 5.0, 3: 5.0, 5: 5.0, 6: 5.0, 7: 5.0}
    b = bundle(tie)
    r1 = decode(b, [Job(IDS, POS, schedules.make('CF', tie_seed=3), FIELD_OF)])[0]
    r2 = decode(b, [Job(IDS, POS, schedules.make('CF', tie_seed=3), FIELD_OF)])[0]
    assert [s['pos'] for s in r1['steps']] == [s['pos'] for s in r2['steps']]
    assert r1['steps'][0]['tie'] is True
