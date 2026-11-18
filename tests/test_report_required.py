import pytest

from dlm.report import read_required


def test_missing_trace_is_an_error(tmp_path):
    with pytest.raises(FileNotFoundError):
        read_required(tmp_path / 'main-llada.jsonl')


def test_empty_trace_is_an_error(tmp_path):
    p = tmp_path / 'main-llada.jsonl'
    p.write_text('\n')
    with pytest.raises(ValueError):
        read_required(p)


def test_rows_are_read(tmp_path):
    p = tmp_path / 'main-llada.jsonl'
    p.write_text('{"a": 1}\n{"a": 2}\n')
    assert [r['a'] for r in read_required(p)] == [1, 2]
