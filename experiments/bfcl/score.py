"""Score BFCL traces with the official bfcl-eval decoder and AST checker. Runs in the BFCL venv:

    PYTHONNOUSERSITE=1 /data/rbg/users/linrui/venvs/bfcl-eval-2026.3.23/bin/python experiments/bfcl/score.py --stage bfcl --trace test

The output text is passed unchanged to `default_decode_ast_prompting` (BFCL's own light
normalization: strip backticks/whitespace, add missing outer brackets); no further repair.
"""
import argparse
import json
from pathlib import Path

from bfcl_eval.constants.enums import Language, ReturnFormat
from bfcl_eval.eval_checker.ast_eval.ast_checker import ast_checker
from bfcl_eval.model_handler.utils import default_decode_ast_prompting

ROOT = Path(__file__).resolve().parents[2]
CHECK_MODEL = 'qwen3-8b'   # a BFCL prompting config with underscore_to_dot=False; affects only name conversion
FILES = {'test': 'items.jsonl', 'dev': 'dev.jsonl', 'sanity': 'sanity.jsonl'}


def error_class(parse_ok, res):
    if not parse_ok:
        return 'parse_error'
    if res['valid']:
        return 'correct'
    t = res.get('error_type', '')
    if 'wrong_func_name' in t:
        return 'wrong_function'
    if 'wrong_count' in t:
        return 'wrong_count'
    return 'argument_error'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--stage', default='bfcl')
    ap.add_argument('--trace', required=True)
    ap.add_argument('--models', default='llada,dream')
    a = ap.parse_args()
    from bfcl_eval.constants.model_config import MODEL_CONFIG_MAPPING
    assert not MODEL_CONFIG_MAPPING[CHECK_MODEL].underscore_to_dot
    base = ROOT / 'results' / a.stage
    for m in a.models.split(','):
        src = base / 'traces' / f'{a.trace}-{m}.jsonl'
        if not src.exists():
            continue
        out = base / 'scores' / f'{a.trace}-{m}.jsonl'
        out.parent.mkdir(parents=True, exist_ok=True)
        items, n, good = {}, 0, 0
        with open(out, 'w') as f:
            for line in open(src):
                r = json.loads(line)
                if r['split'] not in items:
                    items[r['split']] = {(x['id'], x['schema']): x for x in map(json.loads, open(ROOT / 'results/bfcl' / FILES[r['split']]))}
                it = items[r['split']][(r['item'], r['schema'])]
                fmt = ReturnFormat.JSON if r['return_format'] == 'json' else ReturnFormat.PYTHON
                try:
                    decoded = default_decode_ast_prompting(r['text'], fmt)
                    parse_ok = isinstance(decoded, list) and all(isinstance(x, dict) for x in decoded)
                except Exception as e:  # unparseable output is a result, not a crash
                    decoded, parse_ok, perr = None, False, repr(e)[:200]
                else:
                    perr = None
                res = {'valid': False, 'error_type': 'parse_error'}
                if parse_ok:
                    try:
                        res = ast_checker(it['eval_functions'], decoded, it['ground_truth'], Language.PYTHON,
                                          it['category'], CHECK_MODEL)
                    except Exception as e:
                        res = {'valid': False, 'error_type': f'checker_exception:{type(e).__name__}', 'error': [repr(e)[:200]]}
                cls = error_class(parse_ok, res)
                f.write(json.dumps(dict(run_id=r['run_id'], item=r['item'], category=r['category'], schema=r['schema'],
                                        order=r['order'], parse_valid=parse_ok, parse_error=perr, ast_valid=bool(res['valid']),
                                        error_type=res.get('error_type'), error_class=cls)) + '\n')
                n += 1
                good += bool(res['valid'])
        print(m, a.trace, 'rows', n, 'AST valid', good)


if __name__ == '__main__':
    main()
