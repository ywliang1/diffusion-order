from experiments.bfcl.lenient import lenient


def test_trailing_period_dropped():
    assert lenient('[diabetes_prediction(weight=150, height=70)].') == ('[diabetes_prediction(weight=150, height=70)]', ['L1'])


def test_json_style_list_rewritten():
    out, rules = lenient('[\n    "biology.get_cell_info",\n    {"cell_type": "human", "detailed": true}\n]')
    assert out == "[biology.get_cell_info(cell_type='human', detailed=True)]" and rules == ['L2']


def test_dict_calls_rewritten():
    out, _ = lenient('Here: [{"name": "f", "arguments": {"x": 1}}, {"function": "g", "parameters": {"y": "z"}}] done')
    assert out == "[f(x=1), g(y='z')]"


def test_bare_call_wrapped_and_prose_dropped():
    assert lenient('Sure! calc(a=1, b=(2, 3)) is the call.')[0] == '[calc(a=1, b=(2, 3))]'


def test_valid_output_unchanged_and_no_value_repair():
    assert lenient('[f(x=1)]') == ('[f(x=1)]', [])
    assert lenient('[f(x="1)]')[0] == '[f(x="1)]'          # unbalanced quote: not repaired
    assert lenient('["name_only"]')[0] == '["name_only"]'  # not call-like: left for the checker to reject


def test_json_format_untouched():
    assert lenient('[{"function": "f"}].', 'json') == ('[{"function": "f"}].', [])
