import json

from portalocker import Lock


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

    def write(self, outpath, append=False):
        """
        Write Smother results to a file.

        Parameters
        ----------
        outpath : str
            Path to write report to
        append : bool
            If True, read an existing smother report from `outpath`
            and combine it with this file before writing.

        Note
        ----
        Append mode is atomic, and can be run in a multithreaded
        or multiprocess test environment.
        """
        with Lock(outpath, mode='a+', truncate=None, timeout=5) as fh:

            if append:
                fh.seek(0)
                other = Smother.load(fh)
                self |= other

            fh.seek(0)
            fh.truncate()  # required to overwrite data in a+ mode
            json.dump(self.data, fh)

    @classmethod
    def load(cls, file_or_path):
        if not isinstance(file_or_path, file):
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
        for filename, start, stop in regions:
            for context, hits in self.data.items():
                if context in result:
                    continue

                for lineno in hits.get(filename, []):
                    if (lineno >= start) and (lineno < stop):
                        result.add(context)
                        break
                    elif lineno >= stop:
                        break

        return QueryResult(result)
