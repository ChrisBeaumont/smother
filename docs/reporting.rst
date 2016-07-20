Working with Smother Data
=========================


Querying
--------

Once you have build a ``.smother`` file, you can query it in
a variety of ways. It's main usage is to lookup which tests
ran a particular section of code. This is what ``smother lookup``
is for. The lookup command takes a description of a code section
in a variety of formats:

::

    # module name. Matches the entire module
    smother lookup smother.python

    # module_name:line_number. Matches 1 line
    smother lookup smother.python:50

    # line range
    smother lookup smother.python:50-60

    # module:class_or_function
    smother lookup smother.python:PythonFile

    # module:nested_class_or_function
    smother lookup smother.python:PythonFile.line_count


Smother determines which line range each section corresponds to,
and prints out all of the tests which visited that region.

Semantic vs Literal Mode
------------------------

By default, the code sections above are converted to a range of line
numbers, and smother looks for tests which also visit these line numbers.
However smother also takes a ``--semantic`` keyword. In semantic mode,
regions are expanded into the smallest function, class, or module
definition that contains the entire region. For example, consider
a `particular line in smother's source <https://github.com/ChrisBeaumont/smother/blob/9244410fa9100eb03f68be436b3fc54991258c93/smother/python.py#L34>`_.
The following lines all expand to the same section of code in semantic mode:

::

    smother --semantic lookup smother.python:34
    smother --semantic lookup smother.python:24-38
    smother --semantic lookup smother.python:Visitor.__init__


This is primarily useful for diff reporting and CSV output (below), but can
be enabled manually in any context.

Diff Reporting
--------------

A common use case for smother is to determine, given a code change,
which tests might have broken. If the code is in a git repository,
smother provides a ``diff`` command to do this:

::

    smother diff
    smother diff origin/master

The behavior of the diff command is as follows:

  * Determine which semantic regions were modified (deleted) in the old version of the code.
  * Determine which semantic regions were modified (added) in the new version of the code.
  * Take the union of these semantic regions -- call this ``U``.
  * Report which tests visited region ``U``, assuming that the smother report was generated against the old version of the code.

Note that semantic mode is implied by the ``diff`` command.

CSV Dumps
---------

Smother provides a ``csv`` command to dump each ``(source,test)`` pair
to a CSV file. Each source record will be a line number or,
if ``--semantic`` mode is enabled, a semantic region (module, class, or
function block). This can be used to more easily analyze the coupling
between app and test logic.

Coverage Reports
----------------
the ``to_coverage`` command converts a `.smother` datafile into a ``coverage.py`` datafile, for use with ``coverage``.
