import sys

PY35 = sys.version_info >= (3, 5)
PY3 = sys.version_info >= (3, 0)
PY2 = sys.version_info < (3, 0)

assert PY3, "Python 2 is no longer supported on this project. Please upgrade to Python 3.6 or higher."
