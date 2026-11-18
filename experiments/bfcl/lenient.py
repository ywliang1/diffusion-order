"""Secondary lenient parse for BFCL outputs (pre-specified 2026-11-18, before any lenient score was computed).

Applied to the cropped content text, then the result goes through the same official decoder and AST checker
as the strict score. Python-format items only; JSON-format items (the sanity set) are left unchanged.
Rules, in order:
  L1 extract   keep the first balanced top-level `[...]` if the text has one, else the first balanced
               `name(...)` call (wrapped in [...]); text before it (prose) and after it (".", ";", prose) is dropped.
  L2 json-list a segment that is a JSON or Python literal of call-like structures is rewritten as Python calls:
               ["f", {args}]  ·  [["f", {args}], ...]  ·  {"name"|"function": "f", "arguments"|"parameters"|"args": {args}}
               ·  a list of such dicts. Values are rendered with Python repr.
Nothing else is repaired (no quote, bracket, argument-name or value fixes).
"""
import ast
import json
import re

NAME = re.compile(r'[A-Za-z_][\w.]*\s*\(')
NAME_KEYS = ('name', 'function')
ARG_KEYS = ('arguments', 'parameters', 'args')


def _balanced(text, start, open_ch, close_ch):
    depth, quote, esc = 0, None, False
    for i in range(start, len(text)):
        ch = text[i]
        if quote:
            if esc:
                esc = False
            elif ch == '\\':
                esc = True
            elif ch == quote:
                quote = None
            continue
        if ch in '"\'':
            quote = ch
        elif ch == open_ch:
            depth += 1
        elif ch == close_ch:
            depth -= 1
            if depth == 0:
                return text[start:i + 1]
    return None


def extract(text):
    """L1: the first balanced [...] segment, else the first balanced call wrapped in [...]; None if neither."""
    i = text.find('[')
    if i >= 0:
        seg = _balanced(text, i, '[', ']')
        if seg:
            return seg
    m = NAME.search(text)
    if m:
        j = text.index('(', m.start())
        seg = _balanced(text, j, '(', ')')
        if seg:
            return '[' + text[m.start():j].strip() + seg + ']'
    return None


def _literal(seg):
    for load in (json.loads, ast.literal_eval):
        try:
            return load(seg)
        except Exception:
            continue
    return None


def _call(name, args):
    if not isinstance(name, str) or not isinstance(args, dict) or not re.fullmatch(r'[A-Za-z_][\w.]*', name):
        return None
    return f"{name}({', '.join(f'{k}={v!r}' for k, v in args.items())})"


def _from_dict(d):
    name = next((d[k] for k in NAME_KEYS if k in d), None)
    args = next((d[k] for k in ARG_KEYS if k in d), {})
    return _call(name, args)


def json_list(seg):
    """L2: rewrite a literal of call-like structures as '[f(a=1), g(b=2)]'; None if not call-like."""
    v = _literal(seg)
    if isinstance(v, dict):
        v = [v]
    if not isinstance(v, list) or not v:
        return None
    if len(v) == 2 and isinstance(v[0], str) and isinstance(v[1], dict):
        v = [v]
    calls = []
    for x in v:
        if isinstance(x, dict):
            c = _from_dict(x)
        elif isinstance(x, (list, tuple)) and len(x) == 2:
            c = _call(x[0], x[1])
        else:
            c = None
        if c is None:
            return None
        calls.append(c)
    return '[' + ', '.join(calls) + ']'


def lenient(text, return_format='python'):
    """Returns (new_text, rules_applied)."""
    if return_format != 'python':
        return text, []
    seg = extract(text)
    if seg is None:
        return text, []
    rules = ['L1'] if seg.strip() != text.strip() else []
    conv = json_list(seg)
    if conv is not None:
        return conv, rules + ['L2']
    return seg, rules
