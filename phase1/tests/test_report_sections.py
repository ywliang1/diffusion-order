from phase1 import analyze


def test_report_keeps_recommendation_on_empty_traces(monkeypatch):
    monkeypatch.setattr(analyze, 'read', lambda name, exp: [])
    text = analyze.analyze('llada')
    assert '## Exp 4 recommendation' in text
    assert 'Awaiting human review' in text
    assert '## Interpretation limits' in text
