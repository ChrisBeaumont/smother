import json
import os

from coverage.control import Coverage

from smother.control import Smother
from smother.tests.utils import tempdir


def test_append():
    a = {
        'test1': {'a': [1]},
    }

    b = {
        'test1': {'a': [2]},
        'test2': {'a': [3]}
    }

    combine = {
        'test1': {'a': [1, 2]},
        'test2': {'a': [3]},
    }

    with tempdir() as base:
        outpath = os.path.join(base, '.smother')

        smother = Smother()
        smother.data = a
        smother.write(outpath, append=True)

        smother = Smother()
        smother.data = b
        smother.write(outpath, append=True)

        assert Smother.load(outpath).data == combine


def test_write_coverage():

    a = {
        'test1': {'a': [1]},
        'test2': {'a': [2]},
    }

    expected = {'lines': {os.path.abspath('a'): [1, 2]}}

    with tempdir() as base:
        path = os.path.join(base, '.coverage')

        cov = Coverage(data_file=path)

        smother = Smother(cov)
        smother.data = a
        smother.write_coverage()

        header_len = 63
        with open(path) as infile:
            infile.seek(header_len)
            result = json.load(infile)

        assert result == expected


def test_iter_records_semantic():

    # Default coverage behavior is to emit absolute file paths.
    smother = Smother()
    smother.data = {
        'test1': {os.path.abspath('smother/tests/demo.py'): [8]}
    }

    expected = [('smother.tests.demo:foo', 'test1')]
    assert list(smother.iter_records(semantic=True)) == expected
