## Smother

![logo](docs/_static/smother.png)

[![Build Status](https://travis-ci.org/ChrisBeaumont/smother.svg?branch=master)](https://travis-ci.org/ChrisBeaumont/smother)

Smother is a wrapper utility around [coverage.py](https://coverage.readthedocs.io/en/coverage-4.1/) that measures code coverage
separately for each test in a test suite. Its main features include:

 * Fast and reliable coverage tracking using [coverage.py](https://coverage.readthedocs.io/en/coverage-4.1/).
 * Ability to lookup which tests visit an arbitrary section of your application code.
 * Ability to convert version control diffs into a subset of affected tests to rerun.

## Demo

Smother contains plugins for nose and pytest, and behaves similarly to coverage.py:

```
py.test --smother=my_module test_suite/
or
nosetests --with-smother --smother-package=my_module test_suite/
```

These commands create a `.smother` file that can be queried by the `smother` CLI

```
smother lookup foo.bar          # which tests visited module foo.bar?
smother lookup foo.bar:120-122  # or just some lines in that file?
smother lookup foo.bar:baz      # or just the `baz` function?

smother diff                    # given local modifications to my repo, what tests might have broken?
smother diff | xargs py.test    # just run them!

smother to_coverage             # build a vanilla .coverage file from a .smother file
smother csv test.csv            # dump all (application, test) pairs to a file
```

## Why?

Smother was designed to make it easier to work with legacy codebases. Such codebases often have several properties that make rapid iteration difficult:

 * **Long-running test suites.** The initial codebase that smother was designed for took nearly 24 hours of CPU time to run its 11K tests. `smother diff` makes it easier to select a (hopefully much) smaller subset of
 tests to re-run to quickly identify possible regressions.
 * **Many different subsystems** -- most of which any single developer is unfamiliar with. `smother lookup` can be used to explore how and where particular modules are invoked in a test suite. These tests often reveal implicit contracts about code behavior that are not obvious from documentation alone.
 * **Scope creep**. Over time the abstractions in codebases become leakier,
 and logic between different subsystems becomes more heavily coupled. `smother csv` catalogs the coupling between source code units (lines, functions, or classes) and tests. Exploring this data often yields insights about
 which subsystems are well-encapsulated, and which would benefit from refactoring.

## Full Documentation

[Read the Docs](http://smother.readthedocs.io/en/latest/)
