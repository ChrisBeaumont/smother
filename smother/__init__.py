import json
from collections import defaultdict

import six
from portalocker import Lock

from smother.python import InvalidPythonFile
from smother.python import PythonFile


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

    def write(self, outpath, append=False, timeout=60):
        """
        Write Smother results to a file.

        Parameters
        ----------
        outpath : str
            Path to write report to
        append : bool
            If True, read an existing smother report from `outpath`
            and combine it with this file before writing.
        timeout : int
            Time in seconds to wait to acquire a file lock, before
            raising an error.

        Note
        ----
        Append mode is atomic, and can be run in a multithreaded
        or multiprocess test environment.
        """
        lock = Lock(
            outpath, mode='a+',
            truncate=None,
            timeout=timeout,
            fail_when_locked=False
        )

        with lock as fh:

            if append:
                fh.seek(0)
                other = Smother.load(fh)
                self |= other

            fh.seek(0)
            fh.truncate()  # required to overwrite data in a+ mode
            json.dump(self.data, fh)

    @classmethod
    def load(cls, file_or_path):
        if isinstance(file_or_path, six.string_types):
            infile = open(file_or_path)
        else:
            infile = file_or_path

        try:
            data = json.load(infile)
        except ValueError:
            data = {}
        finally:
            # close the file if we opened it
            if infile != file_or_path:
                infile.close()

        result = cls()
        result.data = data
        return result

    def __ior__(self, other):
        for ctx, cover in other.data.items():
            for src, lines in cover.items():
                old = self.data.setdefault(ctx, {}).setdefault(src, [])
                self.data[ctx][src] = sorted(set(old + lines))
        return self

    def query_context(self, regions):

        result = set()

        for region in regions:
            try:
                pf = PythonFile(region.filename)
            except InvalidPythonFile:
                continue

            for test_context, hits in self.data.items():
                if test_context in result:
                    continue

                if region.intersects(pf, hits.get(region.filename, [])):
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

    def iter_records(self, semantic=False):

        inverted = self._invert()
        for src, coverage in six.iteritems(inverted):
            if semantic:
                pf = PythonFile(src)

            source2test = defaultdict(set)
            for test_context, lines in six.iteritems(coverage):
                for line in lines:
                    if semantic:
                        # coverage line count is 1-based
                        try:
                            src_context = pf.lines[line - 1]
                        except IndexError:
                            import ipdb; ipdb.set_trace()
                    else:
                       src_context = "{}:{}".format(src, line)
                    source2test[src_context].add(test_context)

            for src_context in sorted(source2test):
                for test_context in sorted(source2test[src_context]):
                    yield src_context, test_context
