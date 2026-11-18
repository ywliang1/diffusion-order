"""Task audit for the three-field RQ1 design (CPU only): every table value is one token in context, the four
inputs (direction x hop) of a source have equal token length, all six layouts align, no Phase 1 match, no
prompt word in the pool.

    python -m experiments.rq1_3f.audit --config experiments/rq1_3f/config_main-n8.yaml [--models llada]
"""
import argparse
import json
import re

from dlm.canvas import align, build
from dlm.models import ROOT, load_tokenizer, mask_id_of
from dlm.runner import load_cfg
from experiments.phase1_5.audit import offsets
from experiments.rq1_3f.exp import pool
from tasks import lookup
from tasks.exclusion import is_phase1


def audit_model(name, cfg):
    tok, mask = load_tokenizer(name), mask_id_of(name)
    words = pool(tok, mask, name)
    res = dict(pool=len(words), prompt_words_in_pool=len(lookup.rl3_prompt_words() & set(words)), checked_values=0,
               not_single_token=0, length_mismatch=0, misaligned=0, phase1_matches=0, max_canvas=0)
    for sid in range(cfg['sources']):
        s = lookup.make_source(cfg['size'], sid, words, cfg['seed'])
        t = s['rows'][s['target']]
        res['phase1_matches'] += is_phase1(t['A'], t['B'], [x for r in s['rows'] for k, x in r.items() if k != 'q'])
        lengths = set()
        for d in lookup.DIRECTIONS:
            for hop in lookup.HOPS:
                lookup.rl_integrity(s, d, hop)
                inst = lookup.rl3_instruction(s, d, hop)
                for lay in lookup.LAYOUTS3:
                    parts = lookup.rl3_output(lay, d)
                    c = build(tok, mask, inst, parts)
                    lengths.add(len(c.ids))
                    res['max_canvas'] = max(res['max_canvas'], len(c.ids))
                    res['misaligned'] += align(tok, mask, inst, parts, {f: t[f] for f in ('A', 'B', 'H')}, canvas=c) is None
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
                    if not (len(cover) == 1 and cover[0][1] == en and text[cover[0][0]:st] in ('', ' ')):
                        res['not_single_token'] += 1
        res['length_mismatch'] += len(lengths) != 1
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--config', required=True)
    ap.add_argument('--models', default='llada,dream')
    a = ap.parse_args()
    cfg = load_cfg(a.config)
    out = {m: audit_model(m, cfg) for m in a.models.split(',')}
    path = ROOT / 'results' / cfg['stage'] / f"task_audit-{cfg['split']}-n{cfg['size']}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(out, indent=2) + '\n')
    print(json.dumps(out, indent=2))


if __name__ == '__main__':
    main()
