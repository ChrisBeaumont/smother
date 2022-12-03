import json
import os
import platform
from subprocess import check_call
from tempfile import NamedTemporaryFile

from smother.tests import demo

expected_nose = {
    "": {demo.__file__: [4, 7, 11]},
    "smother.tests.demo_testsuite:test_bar": {demo.__file__: [12]},
    "smother.tests.demo_testsuite:test_bar2": {demo.__file__: [12]},
}

expected_pytest = {
    "": {demo.__file__: [4, 7, 11]},
    "smother/tests/demo_testsuite.py::test_bar": {demo.__file__: [12]},
    "smother/tests/demo_testsuite.py::test_bar2": {demo.__file__: [12]},
}


if platform.python_implementation() == 'PyPy':
    # CPython marks the last of a multiline string. PyPy marks the first.
    expected_nose[""][demo.__file__] = [1, 7, 11]
    expected_pytest[""][demo.__file__] = [1, 7, 11]


def test_nose_collection():
    with NamedTemporaryFile() as report, open(os.devnull, 'w') as devnull:
        check_call(
            ['nosetests',
             'smother/tests/demo_testsuite.py',
             '--with-smother',
             '--smother-package=smother.tests.demo',
             '--smother-output={}'.format(report.name)
             ],
            stdout=devnull,
            stderr=devnull)

        report.seek(0)
        contents = report.read().decode('utf8')
        assert json.loads(contents) == expected_nose


def test_pytest_collection():
    with NamedTemporaryFile() as report, open(os.devnull, 'w') as devnull:
        check_call(
            ['py.test',
             'smother/tests/demo_testsuite.py',
             '--smother-cover',
             '--smother=smother.tests.demo',
             '--smother-output={}'.format(report.name)
             ],
            stdout=devnull,
            stderr=devnull)

        report.seek(0)
        contents = report.read().decode('utf8')
        assert json.loads(contents) == expected_pytest
