import pytest
from iotedgedev.buildoptions import parse_build_options

pytestmark = pytest.mark.unit


def test_parse_build_options():
    build_options = [
        "--add-host=github.com:192.30.255.112",
        "--add-host=ports.ubuntu.com:91.189.88.150",
        "--rm",
        "-f test",
        "--file test",
        "-t image",
        "--tag image",
        "--build-arg a=b",
        "--build-arg c=d",
        "--label e=f",
        "--label g",
        "--cache-from a",
        "--cache-from b"
    ]
    sdk_options = {
        'extra_hosts': {
            'github.com': '192.30.255.112',
            'ports.ubuntu.com': '91.189.88.150'
        },
        'rm': True,
        'dockerfile': 'test',
        'tag': 'image',
        'buildargs': {
            'a': 'b',
            'c': 'd'
        },
        'labels': {
            'e': 'f',
            'g': ''
        },
        'cache_from': ['a', 'b']
    }
    assert sdk_options == parse_build_options(build_options)
