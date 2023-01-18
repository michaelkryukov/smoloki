from smoloki import logfmt_load, logfmt_dump

CASES = [
    [{"key": "value"}, "key=value"],
    [{"key": '"value"'}, 'key=\\"value\\"'],
    [{"key": "v=alue"}, 'key="v=alue"'],
    [{"key": "va l ue"}, 'key="va l ue"'],
    [{"key": "va\\l\\ue"}, "key=va\\\\l\\\\ue"],
    [{"key": "va\nl\nue"}, "key=va\\nl\\nue"],
]


def test_dump():
    for original_value, dumped_value in CASES:
        assert logfmt_dump(original_value) == dumped_value


def test_load():
    for original_value, dumped_value in CASES:
        assert logfmt_load(dumped_value) == original_value
