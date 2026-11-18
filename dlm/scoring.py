"""Field scoring and the lookup error taxonomy.

Predictions are compared after stripping leading/trailing whitespace; the raw
string is kept, and `changed_by_norm` marks answers whose correctness the
normalization changed.
"""


def norm(s):
    return s.strip() if s is not None else None


def score_field(raw, gold):
    return dict(pred_raw=raw, pred=norm(raw), gold=gold, correct=norm(raw) == gold,
                correct_raw=raw == gold, changed_by_norm=(norm(raw) == gold) != (raw == gold))


CATEGORIES = ('correct', 'target_row_H', 'target_row_other', 'distractor_row_same_field',
              'other_table_value', 'non_table')


def taxonomy(pred, rows, target, gold_col, h_col='H', extra_values=()):
    """Classify a lookup prediction.

    rows: list of dicts (column -> value) for the source; target: target row index;
    gold_col: column holding the right answer; extra_values: other strings shown in the
    tables (e.g. inert mapping values), counted as table values.
    """
    p = norm(pred)
    t = rows[target]
    if p == t[gold_col]:
        return 'correct'
    if h_col in t and p == t[h_col]:
        return 'target_row_H'
    if p in {v for k, v in t.items() if k != 'q'}:
        return 'target_row_other'
    if any(p == r[gold_col] for i, r in enumerate(rows) if i != target):
        return 'distractor_row_same_field'
    if p in {v for r in rows for k, v in r.items()} or p in set(extra_values):
        return 'other_table_value'
    return 'non_table'
