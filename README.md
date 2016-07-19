## Smother

Smother is a wrapper utility around [coverage.py](https://coverage.readthedocs.io/en/coverage-4.1/) that measures code coverage
separately for each test in a test suite. It's main features include:

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