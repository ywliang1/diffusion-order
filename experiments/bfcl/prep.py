"""Build BFCL items with the official bfcl-eval code. Runs in the isolated BFCL venv:

    PYTHONNOUSERSITE=1 /data/rbg/users/linrui/venvs/bfcl-eval-2026.3.23/bin/python experiments/bfcl/prep.py

Writes results/bfcl/items.jsonl (test: 200 seeded simple_python + all 200 multiple, each with the
original and the reversed parameter order), results/bfcl/dev.jsonl (50 items not in test, for the
canvas length) and results/bfcl/sanity.jsonl (100 seeded live_simple items, JSON output format).
"""
import copy
import json
import random
import sys
from pathlib import Path

import bfcl_eval
from bfcl_eval.model_handler.utils import formulate_system_prompt, system_prompt_pre_processing_chat_model
from bfcl_eval.utils import load_dataset_entry

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'results/bfcl'
DATA = Path(bfcl_eval.__file__).parent / 'data'
SEED = 4610
JSON_FORMAT = 'ret_fmt=json&tool_call_tag=False&func_doc_fmt=json&prompt_fmt=plaintext&style=classic'


def answers(category):
    return {json.loads(x)['id']: json.loads(x)['ground_truth'] for x in open(DATA / 'possible_answer' / f'BFCL_v4_{category}.json')}


def reverse_params(functions):
    """Reverse each function's parameter order (properties and the required list); names, types,
    descriptions and requiredness are unchanged."""
    out = copy.deepcopy(functions)
    for f in out:
        p = f['parameters']
        p['properties'] = dict(reversed(list(p['properties'].items())))
        if 'required' in p:
            p['required'] = list(reversed(p['required']))
    return out


def gold_call(ground_truth):
    """Python-format rendering of the first acceptable answer (optional params whose first option is '' are omitted)."""
    calls = []
    for call in ground_truth:
        (name, params), = call.items()
        args = [f'{k}={v[0]!r}' for k, v in params.items() if v and v[0] != '']
        calls.append(f"{name}({', '.join(args)})")
    return '[' + ', '.join(calls) + ']'


def item(entry, raw_functions, gt, category, schema, fmt=None):
    funcs = reverse_params(entry['function']) if schema == 'reversed' else entry['function']
    eval_funcs = reverse_params(raw_functions) if schema == 'reversed' else raw_functions
    question = copy.deepcopy(entry['question'][0])
    if fmt is None:
        messages = system_prompt_pre_processing_chat_model(question, funcs, entry['id'])
    else:
        messages = [{'role': 'system', 'content': formulate_system_prompt(fmt, funcs)}] + question
    return dict(id=entry['id'], category=category, schema=schema, messages=messages, eval_functions=eval_funcs,
                ground_truth=gt, gold_call=gold_call(gt), return_format='json' if fmt else 'python')


def load(category):
    hinted = {e['id']: e for e in load_dataset_entry(category)}
    raw = {e['id']: e['function'] for e in load_dataset_entry(category, include_language_specific_hint=False)}
    return hinted, raw, answers(category)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    rng = random.Random(SEED)
    simple, simple_raw, simple_gt = load('simple_python')
    multiple, multiple_raw, multiple_gt = load('multiple')
    sids = sorted(simple, key=lambda s: int(s.split('_')[-1]))
    test_simple = sorted(rng.sample(sids, 200), key=lambda s: int(s.split('_')[-1]))
    rest = [s for s in sids if s not in set(test_simple)]
    mids = sorted(multiple, key=lambda s: int(s.split('_')[-1]))
    with open(OUT / 'items.jsonl', 'w') as f:
        for cat, ids, ent, raw, gt in (('simple_python', test_simple, simple, simple_raw, simple_gt),
                                       ('multiple', mids, multiple, multiple_raw, multiple_gt)):
            for i in ids:
                for schema in ('original', 'reversed'):
                    f.write(json.dumps(item(ent[i], raw[i], gt[i], cat, schema)) + '\n')
    live, live_raw, live_gt = load('live_multiple')
    lm = sorted(live, key=lambda s: int(s.split('_')[-1].split('-')[0]) if s.split('_')[-1].split('-')[0].isdigit() else 0)
    dev = [('simple_python', i, simple, simple_raw, simple_gt) for i in rng.sample(rest, 25)] + \
          [('live_multiple', i, live, live_raw, live_gt) for i in rng.sample(sorted(live), 25)]
    with open(OUT / 'dev.jsonl', 'w') as f:
        for cat, i, ent, raw, gt in dev:
            f.write(json.dumps(item(ent[i], raw[i], gt[i], cat, 'original')) + '\n')
    ls, ls_raw, ls_gt = load('live_simple')
    with open(OUT / 'sanity.jsonl', 'w') as f:
        for i in sorted(rng.sample(sorted(ls), 100)):
            f.write(json.dumps(item(ls[i], ls_raw[i], ls_gt[i], 'live_simple', 'original', fmt=JSON_FORMAT)) + '\n')
    meta = dict(bfcl_eval=bfcl_eval.__version__ if hasattr(bfcl_eval, '__version__') else '2026.3.23', seed=SEED,
                test_simple_ids=test_simple, test_multiple_ids=mids, python=sys.version)
    (OUT / 'items_meta.json').write_text(json.dumps(meta, indent=1) + '\n')
    print('test items', 2 * (len(test_simple) + len(mids)), 'dev', len(dev), 'sanity 100')


if __name__ == '__main__':
    main()
