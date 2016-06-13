import pytest

from smother.diff import parse_intervals
from smother.interval import LineInterval

HEADER = """\
diff --git a/x b/x
index f927dcf..b7a637f 100644
--- a/x
+++ b/x"""


one_deletion = """
@@ -1,1 +0,0 @@
-removed
"""

two_deletions = """
@@ -1,3 +1 @@
-removed
 kept
-removed
"""

linechange = """
@@ -1 +1 @@
-old
+new
"""

del_add = """
@@ -1,2 +1,2 @@
-old
 stay
+new
"""

add = """
@@ -1,1 +1,2 @@
 old
+new
"""

L = LineInterval

CASES = [
    (one_deletion, [L('x', 1, 2)]),
    (two_deletions, [L('x', 1, 2), L('x', 3, 4)]),
    (linechange, [L('x', 1, 2)]),
    (del_add, [L('x', 1, 2), L('x', 3, 4)]),
    (add, [L('x', 2, 3)]),
]


@pytest.mark.parametrize('diff,expected', CASES)
def test_parse(diff, expected):
    assert list(parse_intervals(HEADER + diff)) == expected
