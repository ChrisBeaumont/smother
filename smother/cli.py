import inspect
import os
import re
from importlib import import_module

import click
from diff_cover.diff_reporter import GitDiffReporter
from diff_cover.git_diff import GitDiffTool
from more_itertools import unique_justseen

from smother import Smother


"""
Implementation Goals

* [x] Give a filename:lineno, return all tests
* [x] Give a diff, return all tests
* [x] Given an import identifier, return all tests
* [x] Given a test set, run them
* Interactive browser
* Looker/tableau export (list of pairs of context names)
* [ ] Collect website smother report
"""


# grammar = Grammar(
#     """
#     full_path = (path ":" subpath) / path
#     path = (attr_name "." path) / attr_name
#     subpath = path / position_path
#     position_path = range / number
#
#     range = number "-" number
#
#     attr_name = ~"[_a-z][_a-z0-9]*"i
#     number = ~"[0-9]+"
#     """
# )

"""
How to parse a git diff

Extract starting line number for the `-`
@@ -97,7 +97,9 @@ class BaseNotesModel(Model):

start_line = 97
current_line = 97

for each line:
    if is a deletion:
        add current_line to result set
        current_line++
    elif is an addition:
        continue
        add current_line to result set
        do not increment
    else:  # unchanged
        current_line++
"""


"""
class Visitor(NodeVisitor):

    grammar = grammar

    def visit_full_path(self, node, children):

        if len(children) == 3:
            module, _, attr = children
            return module, attr
        else:
            assert len(children) == 1
            return children[0], None

    def visit_subpath(self, node, children):
        return children[0]

    def visit_number(self, node, children):
        return int(node.text)

    def visit_range(self, node, children):
        start, _, stop = children
        return (start, stop)

    def visit_attr_name(self, node, children):
        return node.text

    def visit_path(self, node, children):
        return node.text

    def generic_visit(self, node, children):
        if len(children) == 1:
            return children[0]
        return children
"""

PATH_RE = re.compile('^([a-zA-Z0-9_\.]+)(?::([a-zA-Z0-9_\.-]+))?$')
NUMBER_RE = re.compile('([0-9]+)(?:-([0-9]+))?')


def _get_regions(path):
    try:
        module, subpath = PATH_RE.match(path).groups('')
        node = import_module(module)
    except ImportError:
        raise ValueError("Invalid path: %s" % path)

    match = NUMBER_RE.match(subpath)
    if match:
        start, stop = map(int, match.groups(0))
        stop = stop or start + 1
        src = inspect.getsourcefile(node)
        return [(path, start, stop)]
    else:
        try:
            for attr in filter(None, subpath.split('.')):
                node = getattr(node, attr)
        except AttributeError:
            raise ValueError("Invalid path: %s" % path)

        src, offset = inspect.getsourcelines(node)
        path = inspect.getabsfile(node)
        return [(path, offset, offset + len(src))]


def _ranges_from_diff(diff):
    # XXX edge cases aren't quite right here
    #     a single modified line emits 2 lines of ranges
    filepath = None
    current_line = None
    for line in diff.splitlines():
        if line.startswith('diff'):
            # diff --git a/old_path b/new_path
            #              --------
            filepath = os.path.abspath(line.split(' ')[2][2:])
        elif line.startswith('@@'):
            # @@ -96,6 +96,7 @@
            #     --
            current_line = int(line.split(',')[0][4:])
        elif line.startswith('+++'):
            continue
        elif line.startswith('---'):
            continue
        elif line.startswith('index'):
            continue
        elif line.startswith('new'):
            continue
        elif line.startswith('+'):
            yield filepath, current_line, current_line + 1
            # don't increment line here, we didn't consume a line
            # in the original file.
        elif line.startswith('-'):
            yield filepath, current_line, current_line + 1
            current_line += 1
        elif line.startswith(' '):
            current_line += 1
        else:
            raise AssertionError("Unexpected diff line: %s" % line)


def _get_diff_regions(branch):
    reporter = GitDiffReporter(branch, git_diff=GitDiffTool())
    for diff in reporter._get_included_diff_results():
        for rng in unique_justseen(_ranges_from_diff(diff)):
            yield rng


@click.group()
def cli():
    pass


def _report_from_regions(regions):
    regions = list(regions)
    smother = Smother.load()
    result = smother.query_context(regions)
    result.report()


@cli.command()
@click.argument("path")
def lookup(path):

    regions = _get_regions(path)
    _report_from_regions(regions)


@cli.command()
@click.argument("branch", default="")
def diff(branch):

    regions = _get_diff_regions(branch)
    _report_from_regions(regions)


@cli.command()
@click.argument('src', nargs=-1, type=click.Path())
@click.argument('dst', nargs=1, type=click.Path())
def combine(src, dst):

    result = None
    for infile in src:
        sm = Smother.load(infile)
        if not result:
            result = sm
        else:
            result |= sm

    result.write(dst)


if __name__ == "__main__":
    cli()
