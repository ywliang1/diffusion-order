"""Stage 3 task audit (CPU only): every table value is exactly k tokens in the rendered prompt (the
tokens tile the value, the first optionally with one leading space); equal prompt length across the
four inputs of a source; both layouts align with k-token output slots; no Phase 1 match.

    python -m experiments.stage3.audit --config experiments/stage3/config_k3.yaml
"""
import argparse
import json
import re

from dlm.canvas import align, build
from dlm.models import ROOT, load_tokenizer, mask_id_of
from dlm.runner import load_cfg
from experiments.exp4.exp import multi_pool, size_of
from experiments.phase1_5.audit import offsets
from tasks import lookup
from tasks.exclusion import is_phase1


def audit_model(name, cfg):
    tok, mask, k = load_tokenizer(name), mask_id_of(name), cfg['tokens']
    words = multi_pool(tok, mask, name, k)
    n = size_of(cfg, name)
    res = dict(pool=len(words), size=n, tokens=k, checked_values=0, wrong_token_count=0, length_mismatch=0,
               misaligned=0, phase1_matches=0, max_canvas=0)
    for sid in range(cfg['sources']):
        s = lookup.make_source(n, sid, words, cfg['seed'])
        t = s['rows'][s['target']]
        res['phase1_matches'] += is_phase1(t['A'], t['B'])
        lengths = set()
        for d in lookup.DIRECTIONS:
            for hop in lookup.HOPS:
                lookup.rl_integrity(s, d, hop)
                inst = lookup.rl_instruction(s, d, hop)
                for lay in lookup.LAYOUTS:
                    parts = lookup.rl_output(lay, d, k)
                    c = build(tok, mask, inst, parts)
                    lengths.add(len(c.ids))
                    res['max_canvas'] = max(res['max_canvas'], len(c.ids))
                    res['misaligned'] += align(tok, mask, inst, parts, {'A': t['A'], 'B': t['B']}, canvas=c) is None
                ids = c.ids[:c.prompt_len]
                offs, _ = offsets(tok, ids)
                text = tok.decode(ids, skip_special_tokens=False)
                vals = lookup.rl_table_values(s, d, hop)
                start = text.index('Anchor')
                for m in re.finditer(r'(?<![A-Za-z0-9_|<])[a-z]+(?![A-Za-z0-9_|>])', text[start:]):
                    if m.group() not in vals:
                        continue
                    st, en = m.start() + start, m.end() + start
                    res['checked_values'] += 1
                    cover = [(a, b) for a, b in offs if b > st and a < en]
                    ok = len(cover) == k and cover[-1][1] == en and text[cover[0][0]:st] in ('', ' ')
                    res['wrong_token_count'] += not ok
        res['length_mismatch'] += len(lengths) != 1
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--config', required=True)
    a = ap.parse_args()
    cfg = load_cfg(a.config)
    out = {m: audit_model(m, cfg) for m in ('llada', 'dream')}
    path = ROOT / 'results' / cfg['stage'] / f"task_audit-{cfg['split']}-k{cfg['tokens']}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(out, indent=2) + '\n')
    print(json.dumps(out, indent=2))


if __name__ == '__main__':
    main()
