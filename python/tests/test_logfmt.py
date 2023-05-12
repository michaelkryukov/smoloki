from smoloki import logfmt_load, logfmt_dump, _logfmt_unescape

CASES = [
    [{"key": "value"}, "key=value"],
    [{"key": '"value"'}, 'key="\\"value\\""'],
    [{"key": "v=alue"}, 'key="v=alue"'],
    [{"key": "va l ue"}, 'key="va l ue"'],
    [{"key": "va\\l\\ue"}, "key=va\\\\l\\\\ue"],
    [{"key": "va\nl\nue"}, "key=va\\nl\\nue"],
    [{"key": "'"}, "key='"],
    [{"key": '"'}, 'key="\\""'],
]


def test_dump():
    for original_value, dumped_value in CASES:
        assert logfmt_dump(original_value) == dumped_value


def test_dump_int_and_float():
    assert logfmt_dump({"key": 1}) == "key=1"
    assert logfmt_dump({"key": 1.5}) == "key=1.5"


def test_load():
    for original_value, dumped_value in CASES:
        assert logfmt_load(dumped_value) == original_value


def test_unescape():
    assert _logfmt_unescape('"hey"') == "hey"
    assert _logfmt_unescape('"\\"hey\\""') == '"hey"'
