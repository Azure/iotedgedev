import pytest
from iotedgedev.version import PY3

minversion = pytest.mark.skipif(not PY3, reason="Python 2 not supported. Skipping.")