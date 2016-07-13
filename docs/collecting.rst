Collecting Smother Data
=======================

Smother is a wrapper around `coverage.py <https://coverage.readthedocs.io/en/coverage-4.1/>`_, and by itself is pretty dumb. It basically
runs coverage as normal, but stores the coverage output for each test
separately. This doesn't have a huge impact on the runtime of your test suite,
although the size of the report will be larger.

Building a smother report currently requires that your test suite
uses nose or pytest.

Installation
------------

::

    pip install smother

This installs the ``smother`` command line utility, as well as
plugins for nose and pytest.


Smother with pytest
-------------------

You can invoke ``py.test`` with a ``--smother`` keyword
listing which modules you want to track smother data for.

::

    py.test --smother=my_module

You can configure coverage-specific options by specifying a coveragerc file
(default is ``.coveragerc``, but you can override via the ``--smother-config`` option).

See ``py.test --help`` for more keywords

Smother with nose
-----------------

::

    nosetests --smother-package=my_module

See ``nosetests --help`` for more keywords.


Smother with Coverage
---------------------

Smother **cannot** be enabled the same time as coverage.py -- neither
will record the correct information given how they compete for python's
``settrace`` functionality. This means that you cannot run something like

::

    py.test --smother=foo --cover=foo`` or ``nosetests --smother-package=foo --cover-package=foo``.

Instead, you should run smother by itself, and then produce
a coverage file from a smother file

::

    smother to_coverage

This will create a .coverage file that you can then use normally with coverage.py
