"""Markdown report assembly with required sections that are always present."""


def build(title, sections, required=()):
    """sections: ordered dict heading -> markdown body. Required headings missing from
    `sections` (or empty) are still emitted with an explicit 'No data.' body."""
    out = [f'# {title}', '']
    names = list(sections) + [r for r in required if r not in sections]
    for name in names:
        body = sections.get(name) or 'No data.'
        out += [f'## {name}', '', body.rstrip(), '']
    return '\n'.join(out)
