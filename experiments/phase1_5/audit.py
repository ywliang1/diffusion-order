"""Task audit for a Phase 1.5 config (CPU only, no model outputs).

For every source, condition and variant: every table value is exactly one token in the
rendered prompt (the token covers the value, optionally with one leading space); the
prompt has the same token length under all three conditions; the target pair aligns in
the output slots; no source matches a Phase 1 source.

    python -m experiments.phase1_5.audit --config experiments/phase1_5/config_dev.yaml
"""
import argparse
import json
import re

from dlm.canvas import align, build
from dlm.models import ROOT, load_tokenizer, mask_id_of
from dlm.runner import load_cfg
from experiments.phase1_5.exp import cells, pool
from tasks import lookup
from tasks.exclusion import is_phase1


def offsets(tok, ids):
    out, pos = [], 0
    for t in ids:
        piece = tok.decode([t], skip_special_tokens=False)
        out.append((pos, pos + len(piece)))
        pos += len(piece)
    return out, pos


def audit_model(name, cfg):
    tok, mask = load_tokenizer(name), mask_id_of(name)
    words = pool(tok, mask, name)
    res = dict(pool=len(words), checked_values=0, not_single_token=0, length_mismatch=0, misaligned=0,
               phase1_matches=0, resampled_sources=0, examples=[])
    cols = lookup.COLS8 if cfg.get('cols8') else lookup.COLS
    for v, n in cells(cfg, name):
        _, chat = lookup.parse_variant(v)
        for sid in range(cfg['sources']):
            s = lookup.make_source(n, sid, words, cfg['seed'], cols=cols)
            t = s['rows'][s['target']]
            res['phase1_matches'] += is_phase1(t['A'], t['B'], [x for r in s['rows'] for k, x in r.items() if k != 'q'])
            res['resampled_sources'] += s['resamples'] > 0
            lengths = []
            for cond in lookup.CONDITIONS:
                lookup.integrity(s, cond)
                inst = lookup.instruction(s, cond, v)
                c = build(tok, mask, inst, lookup.OUTPUT, chat=chat)
                lengths.append(len(c.ids))
                if align(tok, mask, inst, lookup.OUTPUT, {'A': t['A'], 'B': t['B']}, chat=chat, canvas=c) is None:
                    res['misaligned'] += 1
                ids = c.ids[:c.prompt_len]
                offs, total = offsets(tok, ids)
                text = tok.decode(ids, skip_special_tokens=False)
                assert total == len(text)
                vals = lookup.table_values(s, cond, v)
                start = text.index('Anchor')
                for m in re.finditer(r'(?<![A-Za-z0-9_|<])[a-z]+(?![A-Za-z0-9_|>])', text[start:]):
                    if m.group() not in vals:
                        continue
                    st, en = m.start() + start, m.end() + start
                    res['checked_values'] += 1
                    cover = [(a, b) for a, b in offs if b > st and a < en]
                    if not (len(cover) == 1 and cover[0][1] == en and text[cover[0][0]:st] in ('', ' ')):
                        res['not_single_token'] += 1
                        if len(res['examples']) < 5:
                            res['examples'].append((v, n, sid, cond, m.group(), [text[a:b] for a, b in cover]))
            if len(set(lengths)) != 1:
                res['length_mismatch'] += 1
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--config', required=True)
    ap.add_argument('--models', default='llada,dream')
    a = ap.parse_args()
    cfg = load_cfg(a.config)
    out = {m: audit_model(m, cfg) for m in a.models.split(',')}
    path = ROOT / 'results' / cfg.get('stage', 'phase1_5') / f"task_audit-{cfg['split']}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(out, indent=2) + '\n')
    print(json.dumps(out, indent=2))


if __name__ == '__main__':
    main()
