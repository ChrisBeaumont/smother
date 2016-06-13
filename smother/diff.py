"""
Diff parser
"""
import os
from functools import wraps

from more_itertools import unique_justseen
from unidiff import PatchSet


from smother.interval import LineInterval


def dedup(func):

    @wraps(func)
    def wrapper(*args, **kwargs):
        return unique_justseen(func(*args, **kwargs))

    return wrapper


@dedup
def parse_intervals(diff):
    """
    Parse a diff into an iterator of Intervals.
    """
    """
    patch_set = PatchSet(diff)

    for patch_file in patch_set:
        filepath = patch_file.source_path
        for hunk in patch_file:
            for line in hunk:
                line = line.source_line_no
                yield LineInterval(filepath, line, line + 1)
    """
    # I have no idea what I'm doing.
    filepath = None
    current_line = gutter_line = None

    for line in diff.splitlines():
        if line.startswith('diff'):
            # diff --git a/old_path b/new_path
            #              --------
            filepath = line.split(' ')[2][2:]
        elif line.startswith('@@'):
            # @@ -96,6 +96,7 @@
            #     --
            current_line = int(line.split(' ')[1].split(',')[0][1:])
            gutter_line = current_line
        elif line.startswith('+++'):
            continue
        elif line.startswith('---'):
            continue
        elif line.startswith('index'):
            continue
        elif line.startswith('new'):
            continue
        elif line.startswith('+'):
            yield LineInterval(filepath, gutter_line, gutter_line + 1)
            gutter_line = min(gutter_line + 1, current_line)
            # don't increment line here, we didn't consume a line
            # in the original file.
        elif line.startswith('-'):
            yield LineInterval(filepath, current_line, current_line + 1)
            current_line += 1
        elif line.startswith(' '):
            current_line += 1
            gutter_line = current_line
        else:
            raise AssertionError("Unexpected diff line: %r" % line)
