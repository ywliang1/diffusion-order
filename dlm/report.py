"""Markdown report assembly with required sections that are always present, and a strict trace reader."""
import json


def build(title, sections, required=()):
    """sections: ordered dict heading -> markdown body. Required headings missing from
    `sections` (or empty) are still emitted with an explicit 'No data.' body."""
    out = [f'# {title}', '']
    names = list(sections) + [r for r in required if r not in sections]
    for name in names:
        body = sections.get(name) or 'No data.'
        out += [f'## {name}', '', body.rstrip(), '']
    return '\n'.join(out)


def read_required(path):
    """Rows of an expected JSONL trace. A missing or empty file is an error, never an empty result:
    an analysis must not write a report that silently omits a model (Exp 4, 2026-11-18)."""
    if not path.exists():
        raise FileNotFoundError(f'expected trace is missing: {path}')
    rows = [json.loads(x) for x in open(path) if x.strip()]
    if not rows:
        raise ValueError(f'expected trace is empty: {path}')
    return rows
