import pytest
import sys

test_py2 = sys.version_info < (3, 0)

minversion = pytest.mark.skipif(test_py2, reason="Python 2 not supported. Skipping.")