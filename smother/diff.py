"""
Diff parser
"""
from abc import ABCMeta
from abc import abstractmethod
from abc import abstractproperty

import six
from functools import wraps

from more_itertools import unique_justseen
from unidiff.constants import LINE_TYPE_ADDED
from unidiff.constants import LINE_TYPE_CONTEXT
from unidiff.constants import LINE_TYPE_EMPTY
from unidiff.constants import LINE_TYPE_REMOVED

from smother.interval import ContextInterval
from smother.python import InvalidPythonFile


def dedup(func):

    @wraps(func)
    def wrapper(*args, **kwargs):
        return unique_justseen(func(*args, **kwargs))

    return wrapper


@dedup
def parse_intervals(diff_report):
    """
    Parse a diff into an iterator of Intervals.
    """

    for patch in diff_report.patch_set:
        try:
            old_pf = diff_report.old_file(patch.source_file)
            new_pf = diff_report.new_file(patch.target_file)
        except InvalidPythonFile:
            continue

        for hunk in patch:
            for line in hunk:
                if line.line_type == LINE_TYPE_ADDED:
                    idx = line.target_line_no
                    yield ContextInterval(new_pf.filename, new_pf.context(idx))
                elif line.line_type == LINE_TYPE_REMOVED:
                    idx = line.source_line_no
                    yield ContextInterval(old_pf.filename, old_pf.context(idx))
                elif line.line_type in (LINE_TYPE_EMPTY, LINE_TYPE_CONTEXT):
                    pass
                else:
                    raise AssertionError("Unexpected line type: %s" % line)


@six.add_metaclass(ABCMeta)
class DiffReporter(object):

    @abstractproperty
    def patch_set(self):
        pass

    @abstractmethod
    def old_file(self, path):
        """
        Given an old file name from a diff report, return a PythonFile
        """
        pass

    @abstractmethod
    def new_file(self, path):
        """
        Given a new file name from a diff report, return a PythonFile
        """
        pass

    def changed_intervals(self):
        return parse_intervals(self)
