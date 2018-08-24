import pytest
import hashlib

from iotedgedev.decorators import suppress_all_exceptions
from iotedgedev.decorators import hash256_result

pytestmark = pytest.mark.unit


def test_suppress_all_exceptions():
    @suppress_all_exceptions()
    def test_valid():
        return 'Everything is OK'
    assert test_valid() == 'Everything is OK'

    @suppress_all_exceptions('fallback')
    def test_exception_fallback():
        raise Exception
    assert test_exception_fallback() == 'fallback'

    @suppress_all_exceptions()
    def test_exception_nofallback():
        raise Exception
    assert not test_exception_nofallback()


def test_hash256_result():
    @hash256_result
    def test_none():
        return None
    with pytest.raises(ValueError):
        test_none()

    @hash256_result
    def test_nostring():
        return 0
    with pytest.raises(ValueError):
        test_nostring()

    @hash256_result
    def test_valid():
        return "test"
    expect_hash = hashlib.sha256("test".encode('utf-8'))
    assert str(expect_hash.hexdigest()) == test_valid()
