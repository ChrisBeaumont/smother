import json
import mock
import os

from coverage.control import Coverage

from smother.control import get_smother_filename  # nopep8
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


@mock.patch('smother.control.random')
@mock.patch('smother.control.socket')
@mock.patch('smother.control.os')
def test_parallel_mode_suffix(mock_os, mock_socket, mock_random):
    fake_pid = 12345
    fake_hostname = "the_host"
    fake_random_int = 99999
    mock_os.getpid.return_value = fake_pid
    mock_socket.gethostname.return_value = fake_hostname
    mock_random.randint.return_value = fake_random_int

    base_name = ".smother"
    fake_suffix = "the_host.12345.099999"
    assert get_smother_filename(base_name, False) == base_name
    assert (
        get_smother_filename(base_name, True) == base_name + "." + fake_suffix)


def test_convert_to_relative_paths():
    smother = Smother()
    smother.data = {
        'test1': {os.path.abspath('smother/tests/demo.py'): [8]}
    }

    expected_data = {
        'test1': {'smother/tests/demo.py': [8]}
    }

    assert Smother.convert_to_relative_paths(smother).data == expected_data
