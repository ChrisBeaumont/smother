from subprocess import CalledProcessError

import pytest
from mock import patch
from unidiff import PatchSet

from smother import git


def test_execute():
    git.execute(['echo', 'test']) == 'test\n'

    with pytest.raises(CalledProcessError):
        git.execute(['ls', 'does_not_exist'])


# Need to put as list to prevent editors from stripping trailing whitespace
diff = [
    "diff --git a/smother/diff.py b/smother/diff.py",
    "index 518bc25..bfc8943 100644",
    "--- a/smother/diff.py",
    "+++ b/smother/diff.py",
    "@@ -10,6 +10,7 @@ from unidiff.constants import LINE_TYPE_EMPTY",
    " from unidiff.constants import LINE_TYPE_REMOVED",
    " ",
    " from smother.interval import ContextInterval",
    "+from smother.python import InvalidPythonFile",
    " ",
    " ",
    " def dedup(func):"
]


def test_git_diff():
    with patch.object(git, 'execute') as mock:
        mock.return_value = '\n'.join(diff)

        result = git.git_diff()

    expected_cmd = [
        'git', '-c', 'diff.mnemonicprefix=no',
        'diff', '--no-color', '--no-ext-diff'
    ]

    mock.assert_called_once_with(expected_cmd)

    [[[a, b, c, d, e, f, g]]] = result
    assert a.is_context
    assert b.is_context
    assert c.is_context
    assert d.is_added
    assert e.is_context
    assert f.is_context
    assert g.is_context


def test_git_show():

    with patch.object(git, 'execute') as mock:
        git.git_show(None, 'a')
        mock.assert_called_once_with(['git', 'show', ':a'])

    with patch.object(git, 'execute') as mock:
        git.git_show('origin/master', 'a')
        mock.assert_called_once_with(['git', 'show', 'origin/master:a'])


@pytest.mark.integration
class TestGitDiffReporter(object):

    def test_old_file(self):

        reporter = git.GitDiffReporter('4279eac5', diff='skip')
        pf = reporter.old_file('a/smother/tests/demo.py')
        assert len(pf.source) == 153

    def test_new_file(self):

        reporter = git.GitDiffReporter('4279eac5', diff='skip')
        pf = reporter.new_file('b/smother/tests/demo.py')
        assert pf.source == open('smother/tests/demo.py').read()

    def test_patch_set(self):
        reporter = git.GitDiffReporter('07ac1490a')
        assert isinstance(reporter.patch_set, PatchSet)
