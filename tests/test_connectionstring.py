import pytest

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


def test_empty_connectionstring():
    connectionstring = ConnectionString(emptystring)
    assert not connectionstring.data


def test_empty_iothub_connectionstring():
    connectionstring = IoTHubConnectionString(emptystring)
    assert not connectionstring.data


def test_empty_device_connectionstring():
    connectionstring = DeviceConnectionString(emptystring)
    assert not connectionstring.data


def test_valid_connectionstring():
    connectionstring = ConnectionString(valid_connectionstring)
    assert connectionstring.HostName == "testhub.azure-devices.net"
    assert connectionstring.HubName == "testhub"
    assert connectionstring.SharedAccessKey == "gibberish"


def test_valid_iothub_connectionstring():
    connectionstring = IoTHubConnectionString(valid_iothub_connectionstring)
    assert connectionstring.HostName == "ChaoyiTestIoT.azure-devices.net"
    assert connectionstring.HubName == "ChaoyiTestIoT"
    assert connectionstring.SharedAccessKeyName == "iothubowner"
    assert connectionstring.SharedAccessKey == "moregibberish"


def test_valid_devicehub_connectionstring():
    connectionstring = DeviceConnectionString(valid_device_connectionstring)
    assert connectionstring.HostName == "testhub.azure-devices.net"
    assert connectionstring.HubName == "testhub"
    assert connectionstring.DeviceId == "testdevice"
    assert connectionstring.SharedAccessKey == "othergibberish"


def test_invalid_connectionstring():
    connectionstring = ConnectionString(invalid_connectionstring)
    assert connectionstring.HubName != "testhub"


def test_invalid_iothub_connectionstring():
    with pytest.raises(KeyError):
        IoTHubConnectionString(invalid_iothub_connectionstring)


def test_invalid_devicehub_connectionstring():
    connectionstring = DeviceConnectionString(invalid_device_connectionstring)
    assert connectionstring.HostName == "testhub.azure-devices.net"
    assert connectionstring.HubName == "testhub"
    assert not connectionstring.DeviceId
    assert connectionstring.SharedAccessKey == "othergibberish"


def test_hash_connection_str_hostname():
    assert IoTHubConnectionString(valid_iothub_connectionstring).hash_hostname() \
        == ("6b8fcfea09003d5f104771e83bd9ff54c592ec2277ec1815df91dd64d1633778", "azure-devices.net")
    assert IoTHubConnectionString(emptystring).hash_hostname() == ("", "")
    assert IoTHubConnectionString(empty_hostname_iothub_connectionstring).hash_hostname() == ("", "")
