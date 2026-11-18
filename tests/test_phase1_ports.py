"""Ports of the three Phase 1 tests to the dlm stack."""
import torch

from dlm import report
from dlm.decoder import slot_probs
from dlm.models import slot_logits
from dlm.schedules import cf_pick
import random


class FakeDream:
    def __call__(self, input_ids, use_cache):
        assert use_cache is False
        return type('R', (), {'logits': torch.arange(12).reshape(1, 3, 4).float()})()


def test_dream_position_shift_from_generation_code():
    out = slot_logits(FakeDream(), torch.zeros(1, 3, dtype=torch.long), shifted=True)
    assert out[0, 1].tolist() == [0, 1, 2, 3]
    assert out[0, 2].tolist() == [4, 5, 6, 7]


def test_llada_is_not_shifted():
    out = slot_logits(FakeDream(), torch.zeros(1, 3, dtype=torch.long), shifted=False)
    assert out[0, 1].tolist() == [4, 5, 6, 7]


def decision(logits, positions, mask):
    probs = slot_probs(logits[positions], mask)
    conf = {p: float(probs[i].max()) for i, p in enumerate(positions)}
    pos, _ = cf_pick(positions, conf, random.Random(0))
    return pos, int(probs[positions.index(pos)].argmax())


def test_nonwinning_logit_variation_does_not_change_decision():
    one = torch.tensor([[2., 1., 0.], [0., 2., 1.]])
    batched = torch.tensor([[2., 1.03, 0.], [0.02, 2., 1.]])
    assert not torch.equal(one, batched)
    assert decision(one, [0, 1], 2) == decision(batched, [0, 1], 2)


def test_report_keeps_required_sections_on_empty_input():
    text = report.build('Phase 1.5 report', {}, required=['Recommendation', 'Interpretation limits', 'Deviations'])
    assert '## Recommendation' in text
    assert '## Interpretation limits' in text
    assert '## Deviations' in text
