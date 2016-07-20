import json
from tempfile import NamedTemporaryFile

import pytest
from click.testing import CliRunner

from smother.cli import cli


CASES = [
    ('8', 'test1\n'),
    ('8-13', 'test1\ntest2\n'),
    ('bar', 'test2\n'),
    ('', 'test1\ntest2\ntest3\n')
]
NAMES = ['single', 'range', 'name', 'module']


@pytest.mark.parametrize('line,expected', CASES, ids=NAMES)
def test_lookup(line, expected):

    runner = CliRunner()
    result = runner.invoke(
        cli,
        ['-r', 'smother/tests/.smother', 'lookup',
         'smother.tests.demo:{}'.format(line)]
    )
    assert result.exit_code == 0
    assert result.output == expected


def test_combine():

    expected = {
        "test1": {
            "smother/tests/demo.py": [8]
        },
        "test2": {
            "smother/tests/demo.py": [11, 12]
        },
        "test3": {
            "smother/tests/demo.py": [1, 2, 3]
        },
        "test4": {
            "smother/tests/demo.py": [4]
        }
    }

    runner = CliRunner()

    with NamedTemporaryFile(mode='w+') as tf:
        result = runner.invoke(
            cli,
            ['combine',
             'smother/tests/.smother',
             'smother/tests/.smother_2',
             tf.name
             ]
        )

        assert result.exit_code == 0
        tf.seek(0)
        assert json.load(tf) == expected


def test_csv():
    expected = '\n'.join([
        'source_context, test_context',
        'smother/tests/demo.py:11,test2',
        'smother/tests/demo.py:4,test4',
        '',
    ])

    runner = CliRunner()

    with NamedTemporaryFile(mode='w+') as tf:
        result = runner.invoke(
            cli,
            ['-r', 'smother/tests/.smother_2',
             'csv',
             tf.name
             ]
        )
        assert result.exit_code == 0
        tf.seek(0)
        assert tf.read() == expected


def test_semantic_csv():
    expected = '\n'.join([
        'source_context, test_context',
        'smother.tests.demo,test4',
        'smother.tests.demo:bar,test2',
        '',
    ])

    runner = CliRunner()

    with NamedTemporaryFile(mode='w+') as tf:
        result = runner.invoke(
            cli,
            ['-r', 'smother/tests/.smother_2',
             '--semantic',
             'csv',
             tf.name
             ]
        )
        assert result.exit_code == 0
        tf.seek(0)
        assert tf.read() == expected
