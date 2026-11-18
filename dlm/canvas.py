"""Canvas construction: prompt, assistant continuation with masked field spans, optional EOS/pad tail.

The output is a list of literal strings and `Field`s. A field is rendered as
`n_tokens` mask tokens (or as a prefilled value). The full text is tokenized
once, mask positions are assigned to fields in order, and the tail is appended
as raw mask ids after the last output token.
"""
from dataclasses import dataclass, field as dfield


@dataclass
class Field:
    name: str
    n_tokens: int = 1
    role: str = None          # 'prerequisite', 'dependent', or None
    prefill: str = None       # if set, the field is rendered filled, not masked


@dataclass
class Canvas:
    ids: list
    fields: dict              # name -> list of canvas positions (masked fields only)
    roles: dict               # name -> role
    tail: list                # positions of the masked EOS/pad tail
    prompt_len: int           # tokens before the assistant continuation
    gold: dict = dfield(default_factory=dict)  # name -> gold token ids (when aligned)

    def field_of(self):
        return {p: f for f, ps in self.fields.items() for p in ps}

    def masked_positions(self):
        return sorted([p for ps in self.fields.values() for p in ps] + list(self.tail))

    def content_positions(self, final_ids=None, end_ids=()):
        """Content = field positions, plus tail positions before the first end token in the final ids."""
        pos = {p for ps in self.fields.values() for p in ps}
        if self.tail and final_ids is not None:
            for p in self.tail:
                if final_ids[p] in end_ids:
                    break
                pos.add(p)
        return sorted(pos)


def mask_string(tok, mask_id):
    return tok.decode([mask_id], skip_special_tokens=False)


def prefix_text(tok, user_text, chat=True):
    if chat:
        return tok.apply_chat_template([{'role': 'user', 'content': user_text}], tokenize=False, add_generation_prompt=True)
    bos = tok.bos_token or ''
    return bos + user_text.rstrip('\n') + '\n'


def render(tok, mask_id, user_text, parts, fill=None, chat=True):
    """Return (ids, prompt_len, field_names) with each Field masked unless filled by `fill` or its prefill."""
    fill = fill or {}
    m = mask_string(tok, mask_id)
    pre = prefix_text(tok, user_text, chat)
    out = []
    for p in parts:
        if isinstance(p, Field):
            if p.name in fill:
                out.append(fill[p.name])
            elif p.prefill is not None:
                out.append(p.prefill)
            else:
                out.append(m * p.n_tokens)
        else:
            out.append(p)
    ids = tok.encode(pre + ''.join(out), add_special_tokens=False)
    prompt_len = len(tok.encode(pre, add_special_tokens=False))
    return ids, prompt_len


def build(tok, mask_id, user_text, parts, tail=0, chat=True):
    ids, prompt_len = render(tok, mask_id, user_text, parts, chat=chat)
    masked = [f for f in parts if isinstance(f, Field) and f.prefill is None]
    positions = [i for i, v in enumerate(ids) if v == mask_id]
    want = sum(f.n_tokens for f in masked)
    if len(positions) != want:
        raise ValueError(f'mask count {len(positions)} != {want}')
    fields = {}
    k = 0
    for f in masked:
        fields[f.name] = positions[k:k + f.n_tokens]
        k += f.n_tokens
    tail_pos = list(range(len(ids), len(ids) + tail))
    ids = ids + [mask_id] * tail
    roles = {f.name: f.role for f in parts if isinstance(f, Field)}
    return Canvas(ids=ids, fields=fields, roles=roles, tail=tail_pos, prompt_len=prompt_len)


def align(tok, mask_id, user_text, parts, gold, chat=True, canvas=None):
    """Check that filling every masked field with its gold string keeps all other tokens fixed and
    gives exactly n_tokens tokens per field. Returns {field: gold ids} or None if misaligned."""
    canvas = canvas or build(tok, mask_id, user_text, parts, chat=chat)
    filled, _ = render(tok, mask_id, user_text, parts, fill=gold, chat=chat)
    body = canvas.ids[:len(canvas.ids) - len(canvas.tail)]
    if len(filled) != len(body):
        return None
    slot = canvas.field_of()
    for i, (a, b) in enumerate(zip(body, filled)):
        if i not in slot and a != b:
            return None
    out = {}
    for name, ps in canvas.fields.items():
        g = tok.encode(gold[name], add_special_tokens=False)
        if len(g) != len(ps) or [filled[p] for p in ps] != g:
            return None
        out[name] = g
    return out
