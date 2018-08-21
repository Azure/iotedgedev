import sys

PY35 = sys.version_info >= (3, 5)
PY3 = sys.version_info >= (3, 0)
PY2 = sys.version_info < (3, 0)

try:
    FileNotFoundError
except NameError:
    #py2
    FileNotFoundError = IOError