from difflib import unified_diff

import pytest
from unidiff import PatchSet

from smother.diff import parse_intervals
from smother.interval import ContextInterval as I
from smother.python import PythonFile


class TestDiffReport(object):

    def __init__(self, old, new):
        self.old = old
        self.new = new
        diff = unified_diff(
            old.splitlines(),
            new.splitlines(),
            fromfile='test.py',
            tofile='test.py',
        )
        self.patch_set = PatchSet(diff)

    def old_file(self, path):
        return PythonFile('test.py', source=self.old)

    def new_file(self, path):
        return PythonFile('test.py', source=self.new)


old = """
def foo():
    pass
    def bar():
        pass
    pass
"""

one_deletion = """
def foo():
    def bar():
        pass
    pass
"""

one_inner_addition = """
def foo():
    pass
    def bar():
        pass
        new=1
    pass
"""

one_outer_addition = """
def foo():
    pass
    def bar():
        pass
    new=1
    pass
"""

modification = """
def foo():
    pass
    def bar():
        new=1
    pass
"""

CASES = [
    ('one_deletion', one_deletion, [I('test.py', 'test:foo')]),
    ('one_inner_addition', one_inner_addition, [I('test.py', 'test:foo.bar')]),
    ('one_outer_addition', one_outer_addition, [I('test.py', 'test:foo')]),
    ('modification', modification, [I('test.py', 'test:foo.bar')])
]


@pytest.mark.parametrize('label,new,expected', CASES)
def test_parse(label, new, expected):
    diff = TestDiffReport(old, new)
    assert list(parse_intervals(diff)) == expected
