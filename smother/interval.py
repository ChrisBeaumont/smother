"""
   Datastructures to represent code regions.
"""
import re
from collections import namedtuple

from smother.python import PythonFile

NUMBER_RE = re.compile('([0-9]+)(?:-([0-9]+))?')


class Interval(object):
    """
    Abstract base class to represent a region of code.
    """

    def intersects(self, python_file, lines):
        """
        Test whether a `PythonFile` and list of line numbers
        intersects the given Interval.
        """
        raise NotImplementedError()


class LineInterval(namedtuple('LineInterval', 'filename start stop'),
                   Interval):
    """
    Interval defined by a right-open interval of 1-offset line numbers.
    """
    def intersects(self, python_file, lines):

        assert python_file.filename == self.filename

        for line in lines:
            if (line >= self.start) and (line < self.stop):
                return True
        return False


class ContextInterval(namedtuple('ContextInterval', 'filename context'),
                      Interval):
    """
    Interval defined by a `context` identifier within a file.
    """

    def intersects(self, python_file, lines):
        assert python_file.filename == self.filename

        for line in lines:
            if python_file.context(line) == self.context:
                return True
        return False


def parse_intervals(path, as_context=False):
    """
    Parse path strings into a collection of Intervals.

    `path` is a string describing a region in a file. It's format is

        dotted.module.name:[line | start-stop | context]

    `dotted.module.name` is a python module
    `line` is a single line number in the module (1-offset)
    `start-stop` is a right-open interval of line numbers
    `context` is a '.' delimited, nested name of a class or function.
        For example FooClass.method_a.inner_method

    identifies the innermost function in code like

    class FooClass:
        def method_a(self):
            def inner_method():
                pass

    Parameters
    ----------
    path : str
        Region description (see above)
    as_context : bool (optional, default=False)
        If `True`, return `ContextInterval`s instead of `LineInterval`s.
        If `path` provides a line number or range, the result will include
        all contexts that intersect this line range.

    Returns
    -------
    list of `Interval`s
    """

    def _regions_from_range():
        if as_context:
            ctxs = list(set(pf.lines[start - 1: stop - 1]))
            return [
                ContextInterval(filename, ctx)
                for ctx in ctxs
            ]
        else:
            return [LineInterval(filename, start, stop)]

    if ':' in path:
        path, subpath = path.split(':')
    else:
        subpath = ''

    pf = PythonFile.from_modulename(path)
    filename = pf.filename
    rng = NUMBER_RE.match(subpath)

    if rng:  # specified a line or line range
        start, stop = map(int, rng.groups(0))
        stop = stop or start + 1
        return _regions_from_range()
    elif not subpath:  # asked for entire module
        if as_context:
            return [ContextInterval(filename, pf.prefix)]
        start, stop = 1, pf.line_count + 1
        return _regions_from_range()
    else:  # specified a context name
        context = pf.prefix + ':' + subpath
        if context not in pf.lines:
            raise ValueError("%s is not a valid context for %s"
                             % (context, pf.prefix))
        if as_context:
            return [ContextInterval(filename, context)]
        else:
            start, stop = pf.context_range(context)
            return [LineInterval(filename, start, stop)]
