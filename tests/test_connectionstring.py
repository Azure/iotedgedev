import pytest

try:
    from iotedgedev.version import PY3
except AssertionError as e:
    print("AssertionError: This is a Python 2 environment. All tests will be skipped.")

from .version import minversion

if PY3:
    from iotedgedev.connectionstring import (ConnectionString,
                                             DeviceConnectionString,
                                             IoTHubConnectionString)

pytestmark = pytest.mark.unit

emptystring = ""
valid_connectionstring = "HostName=testhub.azure-devices.net;SharedAccessKey=gibberish"
valid_iothub_connectionstring = "HostName=ChaoyiTestIoT.azure-devices.net;SharedAccessKeyName=iothubowner;SharedAccessKey=moregibberish"
valid_device_connectionstring = "HostName=testhub.azure-devices.net;DeviceId=testdevice;SharedAccessKey=othergibberish"
invalid_connectionstring = "HostName=azure-devices.net;SharedAccessKey=gibberish"
invalid_iothub_connectionstring = "HostName=testhub.azure-devices.net;SharedAccessKey=moregibberish"
invalid_device_connectionstring = "HostName=testhub.azure-devices.net;DeviceId=;SharedAccessKey=othergibberish"
empty_hostname_iothub_connectionstring = "HostName=;SharedAccessKeyName=iothubowner;SharedAccessKey=moregibberish"

@minversion
def test_empty_connectionstring():
    connectionstring = ConnectionString(emptystring)
    assert not connectionstring.data


@minversion
def test_empty_hostname_iothub_connectionstring():
    connectionstring = ConnectionString(empty_hostname_iothub_connectionstring)
    assert connectionstring.iothub_host.name == ""
    assert connectionstring.iothub_host.hub_name == ""
    assert connectionstring.shared_access_key == "moregibberish"
    assert connectionstring.iothub_host.name_hash == ""


@minversion
def test_empty_iothub_connectionstring():
    connectionstring = IoTHubConnectionString(emptystring)
    assert not connectionstring.data


@minversion
def test_empty_device_connectionstring():
    connectionstring = DeviceConnectionString(emptystring)
    assert not connectionstring.data


@minversion
def test_valid_connectionstring():
    connectionstring = ConnectionString(valid_connectionstring)
    assert connectionstring.iothub_host.name == "testhub.azure-devices.net"
    assert connectionstring.iothub_host.hub_name == "testhub"
    assert connectionstring.shared_access_key == "gibberish"


@minversion
def test_valid_iothub_connectionstring():
    connectionstring = IoTHubConnectionString(valid_iothub_connectionstring)
    assert connectionstring.iothub_host.name == "ChaoyiTestIoT.azure-devices.net"
    assert connectionstring.iothub_host.hub_name == "ChaoyiTestIoT"
    assert connectionstring.shared_access_key_name == "iothubowner"
    assert connectionstring.shared_access_key == "moregibberish"
    assert connectionstring.iothub_host.name_hash == "6b8fcfea09003d5f104771e83bd9ff54c592ec2277ec1815df91dd64d1633778"


@minversion
def test_valid_devicehub_connectionstring():
    connectionstring = DeviceConnectionString(valid_device_connectionstring)
    assert connectionstring.iothub_host.name == "testhub.azure-devices.net"
    assert connectionstring.iothub_host.hub_name == "testhub"
    assert connectionstring.device_id == "testdevice"
    assert connectionstring.shared_access_key == "othergibberish"


@minversion
def test_invalid_connectionstring():
    connectionstring = ConnectionString(invalid_connectionstring)
    assert connectionstring.iothub_host.hub_name != "testhub"


@minversion
def test_invalid_iothub_connectionstring():
    with pytest.raises(KeyError):
        IoTHubConnectionString(invalid_iothub_connectionstring)


@minversion
def test_invalid_devicehub_connectionstring():
    connectionstring = DeviceConnectionString(invalid_device_connectionstring)
    assert connectionstring.iothub_host.name == "testhub.azure-devices.net"
    assert connectionstring.iothub_host.hub_name == "testhub"
    assert not connectionstring.device_id
    assert connectionstring.shared_access_key == "othergibberish"
