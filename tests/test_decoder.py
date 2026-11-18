from dlm import schedules
from dlm.decoder import Job, decode
from tests.fakes import EOS, MASK, bundle

IDS = [1, 2, MASK, MASK, 3, MASK, MASK]
POS = [2, 3, 5, 6]
CONF = {2: 2.0, 3: 6.0, 5: 1.0, 6: 8.0}


def run(name='CF', b=None):
    b = b or bundle(CONF)
    return b, decode(b, [Job(IDS, POS, schedules.make(name, tie_seed=0), {2: 'A', 3: 'A', 5: 'B', 6: 'B'})])[0]


def test_one_commit_per_forward_pass():
    b, r = run()
    assert len(b.model.calls) == len(POS) == len(r['steps'])
    # each forward pass sees exactly one fewer mask than the previous one
    masks = [int((x == MASK).sum()) for x in b.model.calls]
    assert masks == [4, 3, 2, 1]


def test_committed_tokens_never_rewritten():
    b, r = run()
    calls = b.model.calls
    committed = {}
    for k, s in enumerate(r['steps']):
        committed[s['pos']] = s['token_id']
        for later in calls[k + 1:]:
            for p, t in committed.items():
                assert int(later[0, p]) == t
    for p, t in committed.items():
        assert r['ids'][p] == t
    # unmasked prompt tokens are untouched
    assert r['ids'][:2] == [1, 2] and r['ids'][4] == 3


def test_mask_token_is_never_predicted():
    _, r = run()
    assert all(s['token_id'] != MASK for s in r['steps'])
    assert all(MASK not in s['top5_ids'] for s in r['steps'])


def test_margins_logged():
    _, r = run()
    s0 = r['steps'][0]
    assert s0['pos'] == 6 and s0['cf_margin'] > 0 and s0['choice_margin'] == s0['cf_margin']
    assert r['steps'][-1]['cf_margin'] is None
    assert set(s0) >= {'step', 'pos', 'field', 'role', 'token_id', 'token', 'prob', 'top5_ids', 'top5_probs', 'tok_margin'}


def test_batched_lockstep_matches_single():
    b = bundle(CONF)
    js = [Job(IDS, POS, schedules.make(n, tie_seed=0), {2: 'A', 3: 'A', 5: 'B', 6: 'B'}) for n in ('CF', 'L2R', 'R2L')]
    batched = decode(b, js)
    single = [decode(bundle(CONF), [Job(IDS, POS, schedules.make(n, tie_seed=0), {2: 'A', 3: 'A', 5: 'B', 6: 'B'})])[0]
              for n in ('CF', 'L2R', 'R2L')]
    assert [x['ids'] for x in batched] == [x['ids'] for x in single]


def test_eos_tail_positions_decoded_like_any_other():
    ids = [1, MASK, MASK, MASK]
    b = bundle({1: 3.0, 2: 9.0, 3: 9.5}, tokens={1: 4, 2: EOS, 3: EOS})
    r = decode(b, [Job(ids, [1, 2, 3], schedules.make('CF', tie_seed=0), {1: 'A'})])[0]
    assert [s['pos'] for s in r['steps']] == [3, 2, 1]
    assert r['ids'][2:] == [EOS, EOS]
