from contextlib import contextmanager
from shutil import rmtree
from tempfile import mkdtemp


@contextmanager
def tempdir():
    """
    Create a temporary directory.
    """
    directory = mkdtemp()
    try:
        yield directory
    finally:
        rmtree(directory)
