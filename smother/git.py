from subprocess import CalledProcessError
from subprocess import PIPE
from subprocess import Popen

from unidiff import PatchSet

from smother.diff import DiffReporter
from smother.python import PythonFile


def execute(cmd):
    """Run a shell command and return stdout"""
    proc = Popen(cmd, stdout=PIPE)
    stdout, _ = proc.communicate()
    if proc.returncode != 0:
        raise CalledProcessError(proc.returncode, " ".join(cmd))

    return stdout.decode('utf8')


def git_diff(ref=None):
    cmd = [
        'git',
        '-c', 'diff.mnemonicprefix=no',
        'diff',
        ref,
        '--no-color',
        '--no-ext-diff'
    ]

    data = execute(list(filter(None, cmd)))
    return PatchSet(data.splitlines())


def git_show(ref, path):

    ref = ref or ''
    cmd = [
        'git',
        'show',
        "{}:{}".format(ref, path),
    ]
    return execute(cmd)


class GitDiffReporter(DiffReporter):

    def __init__(self, ref='HEAD', diff=None):
        self.ref = ref
        self._patch_set = diff or git_diff(ref)

    @property
    def patch_set(self):
        return self._patch_set

    def old_file(self, path):
        if path == '/dev/null':
            return

        # git diff may prefix the path with a/
        if path.startswith('a/'):
            filename = path[2:]
        else:
            filename = path

        source = git_show(self.ref, filename)
        return PythonFile(filename, source=source)

    def new_file(self, path):
        if path == '/dev/null':
            return

        # git diff may prefix the path with b/
        if path.startswith('b/'):
            filename = path[2:]
        else:
            filename = path

        return PythonFile(filename)
