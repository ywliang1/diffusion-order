"""CPU fakes: a tiny model whose logits depend only on position, and a trivial tokenizer."""
import torch

from dlm.models import Bundle

V = 12
MASK = 11
EOS = 10


class FakeTok:
    def decode(self, ids, skip_special_tokens=False):
        return ''.join(f'<{i}>' for i in ids)


class FakeModel:
    """Position p predicts token tokens[p] with logit conf[p]; the mask token always has the largest logit."""

    def __init__(self, conf, tokens=None):
        self.conf = conf
        self.tokens = tokens or {}
        self.calls = []

    def __call__(self, input_ids, use_cache):
        assert use_cache is False
        self.calls.append(input_ids.clone())
        B, L = input_ids.shape
        logits = torch.zeros(B, L, V)
        for p in range(L):
            logits[:, p, self.tokens.get(p, p % 10)] = self.conf.get(p, 1.0)
        logits[:, :, MASK] = 100.0
        return type('R', (), {'logits': logits})()


def bundle(conf, tokens=None, name='fake'):
    return Bundle(name=name, model=FakeModel(conf, tokens), tok=FakeTok(), mask_id=MASK, end_ids=(EOS,), device='cpu')
