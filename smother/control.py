import json
import os
from collections import defaultdict
from contextlib import contextmanager

import six
from portalocker import Lock

from smother.python import InvalidPythonFile
from smother.python import PythonFile


@contextmanager
def noclose(file):
    """
    A "no-op" contextmanager that prevents files from closing.
    """
    try:
        yield file
    finally:
        pass


class QueryResult(object):
    def __init__(self, contexts):
        self.contexts = contexts

    def report(self):
        print("\n".join(sorted(self.contexts)))


class Smother(object):

    def __init__(self, coverage=None):
        self.coverage = coverage
        self.data = {}

    def start(self):
        self.coverage.collector.reset()
        self.coverage.start()

    def save_context(self, label):
        self.data[label] = {
            key: sorted(map(int, val.keys()))
            for key, val in self.coverage.collector.data.items()
        }

    def write_coverage(self):
        # coverage won't write data if it hasn't been started.
        self.coverage.start()
        self.coverage.stop()
        data = {}
        for cover in six.itervalues(self.data):
            for path, lines in six.iteritems(cover):
                data.setdefault(path, {}).update(
                    {line: None for line in lines}
                )

        self.coverage.collector.data = data
        self.coverage.save()

    def write(self, file_or_path, append=False, timeout=10):
        """
        Write Smother results to a file.

        Parameters
        ----------
        fiile_or_path : str
            Path to write report to
        append : bool
            If True, read an existing smother report from `outpath`
            and combine it with this file before writing.
        timeout : int
            Time in seconds to wait to acquire a file lock, before
            raising an error.

        Note
        ----
        Append mode is atomic when file_or_path is a path,
        and can be safely run in a multithreaded or
        multiprocess test environment.
        """
        if isinstance(file_or_path, six.string_types):
            outfile = Lock(
                file_or_path, mode='a+',
                truncate=None,
                timeout=timeout,
                fail_when_locked=False
            )
        else:
            outfile = noclose(file_or_path)

        with outfile as fh:

            if append:
                fh.seek(0)
                try:
                    other = Smother.load(fh)
                except ValueError:  # no smother data
                    pass
                else:
                    self |= other

            fh.seek(0)
            fh.truncate()  # required to overwrite data in a+ mode
            json.dump(self.data, fh)

    @classmethod
    def load(cls, file_or_path):
        if isinstance(file_or_path, six.string_types):
            infile = open(file_or_path)
        else:
            infile = noclose(file_or_path)

        with infile as fh:
            data = json.load(fh)

        result = cls()
        result.data = data
        return result

    def __ior__(self, other):
        for ctx, cover in other.data.items():
            for src, lines in cover.items():
                old = self.data.setdefault(ctx, {}).setdefault(src, [])
                self.data[ctx][src] = sorted(set(old + lines))
        return self

    def query_context(self, regions, file_factory=PythonFile):
        """
        Return which set of test contexts intersect a set of code regions.


        Parameters
        ----------
        regions: A sequence of Intervals

        file_factory: Callable (optional, default PythonFile)
            A callable that takes a filename and
            returns a PythonFile object.

        Returns
        -------
        A QueryResult
        """
        result = set()

        for region in regions:
            try:
                pf = file_factory(region.filename)
            except InvalidPythonFile:
                continue

            # region and/or coverage report may use paths
            # relative to this directory. Ensure we find a match
            # if they use different conventions.
            paths = {
                os.path.abspath(region.filename),
                os.path.relpath(region.filename)
            }
            for test_context, hits in six.iteritems(self.data):
                if test_context in result:
                    continue

                for path in paths:
                    if region.intersects(pf, hits.get(path, [])):
                        result.add(test_context)

        return QueryResult(result)

    def _invert(self):
        """
        Invert coverage data from {test_context: {file: line}}
        to {file: {test_context: line}}
        """
        result = defaultdict(dict)
        for test_context, src_context in six.iteritems(self.data):
            for src, lines in six.iteritems(src_context):
                result[src][test_context] = lines
        return result

    def iter_records(self, semantic=False, sort=True):

        inverted = self._invert()
        for src, coverage in six.iteritems(inverted):
            if semantic:
                try:
                    pf = PythonFile(src)
                except IOError:
                    continue

            source2test = defaultdict(set)
            for test_context, lines in six.iteritems(coverage):
                for line in lines:
                    if semantic:
                        # coverage line count is 1-based
                        src_context = pf.context(line)
                    else:
                        src_context = "{}:{}".format(src, line)
                    source2test[src_context].add(test_context)

            for src_context in sorted(source2test) if sort else source2test:
                test_contexts = source2test[src_context]
                if sort:
                    test_contexts = sorted(test_contexts)
                for test_context in test_contexts:
                    yield src_context, test_context
