import pytest

from iotedgedev.decorators import suppress_all_exceptions

pytestmark = pytest.mark.unit


@pytest.fixture
def error_function():
    def _error_function(exception, fallback_return):
        @suppress_all_exceptions(fallback_return=fallback_return)
        def _inner_error_function(exception):
            if not exception:
                return 'Everything is OK'
            else:
                raise exception()
        return _inner_error_function(exception)
    return _error_function


def test_suppress_all_exceptions(error_function):
    err_fn = error_function(Exception, 'fallback')
    assert err_fn == 'fallback'

    err_fn = error_function(None, 'fallback')
    assert err_fn == 'Everything is OK'

    err_fn = error_function(ImportError, 'fallback for ImportError')
    assert err_fn == 'fallback for ImportError'

    err_fn = error_function(None, None)
    assert err_fn == 'Everything is OK'
