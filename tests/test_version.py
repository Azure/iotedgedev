import pytest

from .version import test_py2, py2_test

pytestmark = pytest.mark.e2e

@py2_test
def test_version_assertion_error():
    with pytest.raises(AssertionError, match="Python 2 is no longer supported on this project. Please upgrade to Python 3.6 or higher.")
        from iotedgedev import version