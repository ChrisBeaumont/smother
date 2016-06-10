import json

from coverage.control import Coverage


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

    def write(self, outfile):
        json.dump(self.data, outfile)

    @classmethod
    def load(cls, filename='.smother'):
        with open(filename) as infile:
            data = json.load(infile)

        result = cls()
        result.data = data
        return result

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
