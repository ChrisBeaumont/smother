from smother.interval import ContextInterval
from smother.interval import LineInterval
from smother.interval import parse_intervals


path = 'smother/tests/demo.py'
module = 'smother.tests.demo'


def test_oneline_path():
    assert parse_intervals(module + ':5') == [LineInterval(path, 5, 6)]
    assert parse_intervals(module + ':12', as_context=True) == [
        ContextInterval(path, module + ':bar')]


def test_linerange_path():
    assert parse_intervals(module + ':5-7') == [LineInterval(path, 5, 7)]
    assert set(parse_intervals(module + ':10-12', as_context=True)) == {
        ContextInterval(path, module),
        ContextInterval(path, module + ':bar'),
    }


def test_context_path():
    assert parse_intervals(module + ':bar') == [
        LineInterval(path, 11, 13)]

    assert (
        parse_intervals(module + ':bar', as_context=True) ==
        [ContextInterval(path, module + ':bar')]
    )


def test_module_path():

    assert parse_intervals(module) == [
        LineInterval(path, 1, 13),
    ]

    assert parse_intervals(module, as_context=True) == [
        ContextInterval(path, module)
    ]


def test_init_module():

    assert parse_intervals('smother')[0].filename == 'smother/__init__.py'
    assert parse_intervals('smother:1') == [
        LineInterval('smother/__init__.py', 1, 2)
    ]
    assert parse_intervals('smother:1', as_context=True) == [
        ContextInterval('smother/__init__.py', 'smother')
    ]
