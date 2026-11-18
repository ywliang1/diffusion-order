"""The pre-registered gate and selection rule, on synthetic trace rows."""
from experiments.phase1_5 import analyze as an


def rows_for(variant, direct, shared, separate, sizes=(4, 8), n=100, models=an.MODELS):
    """direct/shared/separate: fraction of sources with B correct (same for every order)."""
    out = []
    for m in models:
        for size in sizes:
            for cond, frac in (('Direct', direct), ('Shared-path', shared), ('Separate-path', separate)):
                for o in an.ORDERS:
                    for sid in range(n):
                        out.append(dict(model=m, variant=variant, experiment=2, table_size=size, condition=cond, order=o,
                                        source_id=sid, B_correct=sid < frac * n))
    return out


def pick(*groups):
    rows = [r for g in groups for r in g]
    return an.select(an.index(rows), sorted({r['variant'] for r in rows}))


def test_first_passing_in_preference_order():
    s = pick(rows_for('V1', .80, .60, .40), rows_for('V4', .95, .60, .40), rows_for('V2', .99, .60, .40))
    assert s['choice'] == 'V4' and s['passing'] == ['V4', 'V2']


def test_direct_threshold_is_inclusive_and_per_order():
    assert pick(rows_for('V1', .90, .60, .40))['choice'] == 'V1'
    assert pick(rows_for('V1', .89, .60, .40))['choice'] is None


def test_shared_band_and_separate_chance():
    assert pick(rows_for('V1', .95, .85, .40))['choice'] is None      # Shared above 80%
    assert pick(rows_for('V1', .95, .35, .40))['choice'] is None      # Shared below 40%
    assert pick(rows_for('V1', .95, .60, .38))['choice'] == 'V1'      # Separate below 40% but above chance (25%, 12.5%)
    assert pick(rows_for('V1', .95, .60, .20))['choice'] is None      # Separate at chance for size 4


def test_nochat_fallback_only_when_no_template_variant_passes():
    s = pick(rows_for('V1', .85, .60, .40), rows_for('V2', .80, .60, .40), rows_for('V1-nochat', .95, .60, .40))
    assert s['closest'] == 'V1' and s['choice'] == 'V1-nochat'
    s = pick(rows_for('V1', .95, .60, .40), rows_for('V1-nochat', .99, .60, .40))
    assert s['choice'] == 'V1'
