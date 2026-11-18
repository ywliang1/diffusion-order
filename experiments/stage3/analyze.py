"""Stage 3 analysis: multi-token values. H1 (now with an identifiable role x position interaction),
H2 (PF vs DF), and within-field commit order under CF.

    python -m experiments.stage3.analyze
"""
import json

import numpy as np

from dlm import report, stats
from dlm.models import ROOT
from experiments.exp4 import analyze as e4
from experiments.rq1 import analyze as rq1

BASE = ROOT / 'results/stage3'


def load(k, m):
    p = BASE / 'traces' / f'main-k{k}-{m}.jsonl'
    return [json.loads(x) for x in open(p) if x.strip()] if p.exists() else []


def contiguous(steps, fields):
    """True if each field's tokens were committed as one uninterrupted block."""
    seq = [s['field'] for s in steps if s['field'] is not None]
    return all(sum(1 for i, f in enumerate(seq) if f == g and (i == 0 or seq[i - 1] != g)) == 1 for g in fields)


def within_table(cf):
    lines = ['| Hop | Field role | Fields committed left to right inside the field | Traces with each field committed as one block |',
             '|---:|---|---:|---:|']
    for hop in (2, 1):
        rows = [r for r in cf if r['hop'] == hop]
        if not rows:
            continue
        blocks = stats.cluster_bootstrap([float(contiguous(r['steps'], ('A', 'B'))) for r in rows], [r['source_id'] for r in rows])
        for role in ('prerequisite', 'dependent'):
            vals = [(float(r['within_field_l2r'][f]), r['source_id']) for r in rows for f in ('A', 'B') if r['roles'][f] == role]
            c = stats.cluster_bootstrap([v for v, _ in vals], [s for _, s in vals])
            lines.append(f'| {hop} | {role} | {stats.fmt(c)} | {stats.fmt(blocks)} |')
    return '\n'.join(lines)


def run():
    sections, summary = {}, {}
    for m in ('llada', 'dream'):
        for k in (2, 3):
            rows = load(k, m)
            if not rows:
                continue
            key = f'{m} k={k}'
            meta = {(r['meta']['hostname'], r['meta']['gpu_name'], r['meta']['git_commit']) for r in rows}
            cf = [r for r in rows if r['order'] == 'CF']
            df = rq1.field_frame(cf)
            fit, boot = rq1.effects(df[df.hop == 2])
            v1 = rq1.verdict(fit, boot)
            res = e4.h2(rows)
            flip = np.mean([r['min_cf_margin'] is not None and r['min_cf_margin'] < rq1.FLIP for r in cf])
            summary[key] = dict(h1=v1, h2=res['verdict'], position=boot['position'], role=boot['role'],
                                interaction=boot['interaction'], pf_df_two=res[2]['gap'], pf_df_one=res[1]['gap'],
                                hop_x_order=res['interaction'], flip_fraction=float(flip), size=rows[0]['table_size'])
            sections[f'{key}: summary'] = (f'Table size {rows[0]["table_size"]}; rows {len(rows)}; hosts/GPUs/commits {sorted(meta)}.\n\n'
                                          f'- **H1: {v1}.**\n- **H2: {res["verdict"]}.**\n'
                                          f'- CF traces with a margin below {rq1.FLIP}: {100 * flip:.1f}%.')
            sections[f'{key}: H1 (CF commit rank, two-hop, with role × position)'] = rq1.effect_table(fit, boot)
            sections[f'{key}: within-field commit order under CF'] = within_table(cf)
            sections[f'{key}: H2 (PF vs DF)'] = e4.h2_table(res)
            sections[f'{key}: accuracy by order'] = e4.accuracy_table(rows)
            sections[f'{key}: alignment'] = rq1.alignment(cf)
    sections['Interpretation limits'] = '\n'.join([
        '- Run on rosetta15 A100s (whole stage); compare with A6000 stages at the level of effects, not rows.',
        '- Orders limited to CF, PF and DF (compute); L2R, R2L and random were not run in this stage.',
        '- Table sizes: LLaDA 64 (128 exceeds its context with 3-token values), Dream 16 (its Exp 4 size).'])
    dec = ROOT / 'experiments/stage3/DECISIONS.md'
    sections['Deviations'] = dec.read_text() if dec.exists() else ''
    (BASE / 'report.md').write_text(report.build('Stage 3: multi-token values', sections, required=['Interpretation limits', 'Deviations']))
    (BASE / 'summary.json').write_text(json.dumps(summary, indent=2, default=float) + '\n')
    print('wrote', BASE / 'report.md', {k: (v['h1'], v['h2']) for k, v in summary.items()})


if __name__ == '__main__':
    run()
