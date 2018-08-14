import pytest
from iotedgedev.buildoptions import BuildOptions

pytestmark = pytest.mark.unit


def test_filter_build_options():
    build_options = [
        "--rm",
        "-f test",
        "--file test",
        "-t image",
        "--tag image",
    ]
    build_options_parser = BuildOptions(build_options)
    assert build_options_parser.filter_build_options(build_options) == []


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
    build_options_parser = BuildOptions(build_options)
    assert sdk_options == build_options_parser.parse_build_options()
