from difflib import unified_diff

import pytest
from unidiff import PatchSet

from smother.diff import DiffReporter
from smother.interval import ContextInterval
from smother.python import PythonFile


class TestDiffReporter(DiffReporter):

    def __init__(self, old, new):
        self.old = old
        self.new = new
        diff = unified_diff(
            old.splitlines(),
            new.splitlines(),
            fromfile='test.py',
            tofile='test.py',
        )
        self._diff = diff

    @property
    def patch_set(self):
        return PatchSet(self._diff)

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

I = ContextInterval
CASES = [
    (one_deletion, [I('test.py', 'test:foo')]),
    (one_inner_addition, [I('test.py', 'test:foo.bar')]),
    (one_outer_addition, [I('test.py', 'test:foo')]),
    (modification, [I('test.py', 'test:foo.bar')])
]
IDS = ['deletion', 'inner_addition', 'outer_addition', 'modification']


@pytest.mark.parametrize('new,expected', CASES, ids=IDS)
def test_parse(new, expected):
    diff = TestDiffReporter(old, new)
    assert list(diff.changed_intervals()) == expected
