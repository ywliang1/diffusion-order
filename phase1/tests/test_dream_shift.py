import torch
from phase1.decoder import slot_logits


class Fake:
    class Config:
        model_type = 'Dream'

    config = Config()

    def __call__(self, input_ids, use_cache):
        assert use_cache is False

        class Result:
            pass

        result = Result()
        result.logits = torch.arange(12).reshape(1, 3, 4).float()
        return result


def test_dream_position_shift_from_generation_code():
    out = slot_logits(Fake(), torch.zeros(1, 3, dtype=torch.long))
    assert out[0, 1].tolist() == [0, 1, 2, 3]
    assert out[0, 2].tolist() == [4, 5, 6, 7]
