.. smother documentation master file, created by
   sphinx-quickstart on Wed Jul  6 14:31:29 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Smother Documentation
=====================

.. currentmodule:: smother

Smother is a tool to measure "who tests what" in a Python test suite. It
uses `coverage.py <https://coverage.readthedocs.io/en/coverage-4.1/>`_ to
track coverage separately for each test. This can be used to:

 * Lookup which tests visit a particular line of sourcecode.
 * Perform regression test selection -- given a diff of local modifications,
   enumerate which tests in a lengthy test suite might have broken.
 * Explore the amount of coupling between test and application code.
 * Accelerate fancier test techniques like `mutation testing <https://www.youtube.com/watch?v=jwB3Nn4hR1o>`_.

Quick Tour
----------

Here's a tour of using smother on smother's own test suite

::

    # runs test suite, builds a .smother report
    > py.test --smother=smother

    # which tests ran line 153 of module smother.python?
    > smother lookup smother.python:153

    smother/tests/test_cli.py::test_lookup[module]
    smother/tests/test_cli.py::test_lookup[name]
    smother/tests/test_cli.py::test_lookup[range]
    smother/tests/test_cli.py::test_lookup[single]
    smother/tests/test_cli.py::test_semantic_flatten
    ...

    # which tests visited the function PythonFile.line_count in that module?
    > smother lookup smother.python:PythonFile.line_count

    smother/tests/test_cli.py::test_lookup[module]
    smother/tests/test_interval.py::test_init_module
    smother/tests/test_interval.py::test_module_path

    # Hmm I've modified something locally
    > git diff
    @@ -175,6 +175,7 @@ class PythonFile(object):

         @property
         def line_count(self):
    +        assert False, "This is a new bug!"
             return len(self.lines)

    # What might have broken?
    > smother diff

    smother/tests/test_cli.py::test_lookup[module]
    smother/tests/test_interval.py::test_init_module
    smother/tests/test_interval.py::test_module_path

    # Run those tests!
    smother diff | xargs pytest  # 3 failures

    # Dump the report to a csv of <source context, test context>
    smother csv report.csv

    # Build a vanilla .coverage file
    smother to_coverage && coverage html


Contents:

.. toctree::
   :maxdepth: 2

   collecting.rst
   reporting.rst


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

