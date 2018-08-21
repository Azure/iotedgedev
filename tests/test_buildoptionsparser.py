import pytest
from iotedgedev.buildoptionsparser import BuildOptionsParser

pytestmark = pytest.mark.unit


def test_filter_build_options():
    build_options = [
        "--rm",
        "-f test",
        "--file test",
        "-t image",
        "--tag image"
    ]
    build_options_parser = BuildOptionsParser(build_options)
    assert not build_options_parser.parse_build_options()


def test_parse_to_dict():
    build_options = [
        "--add-host=github.com:192.30.255.112",
        "--add-host=ports.ubuntu.com:91.189.88.150",
        "--build-arg a=b",
        "--build-arg c=d",
        "--label e=f",
        "--label g"
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
        }
    }
    build_options_parser = BuildOptionsParser(build_options)
    assert sdk_options == build_options_parser.parse_build_options()


def test_parse_to_list():
    build_options = [
        "--cache-from a",
        "--cache-from b"
    ]
    sdk_options = {
        'cache_from': ['a', 'b']
    }
    build_options_parser = BuildOptionsParser(build_options)
    assert sdk_options == build_options_parser.parse_build_options()


def test_parse_val():
    build_options = [
        "--network bridge",
        "--platform Linux",
        "--shm-size 1000000",
        "--target target"
    ]
    sdk_options = {
        'network_mode': 'bridge',
        'platform': 'Linux',
        'shmsize': '1000000',
        'target': 'target'
    }
    build_options_parser = BuildOptionsParser(build_options)
    assert sdk_options == build_options_parser.parse_build_options()


def test_parse_container_limits():
    build_options = [
        "--cpu-shares 50",
        "--cpuset-cpus 0-1",
        "--memory 10000000",
        "--memory-swap 2000000"
    ]
    sdk_options = {
        'container_limits': {
            'cpushares': '50',
            'cpusetcpus': '0-1',
            'memory': '10000000',
            'memswap': '2000000'
        }
    }
    build_options_parser = BuildOptionsParser(build_options)
    assert sdk_options == build_options_parser.parse_build_options()


def test_parse_flag():
    build_options = [
        "--pull=true",
        "-q=false",
        "--no-cache"
    ]
    sdk_options = {
        'pull': True,
        'quiet': False,
        'nocache': True
    }
    build_options_parser = BuildOptionsParser(build_options)
    assert sdk_options == build_options_parser.parse_build_options()


def test_invalid_build_options():
    with pytest.raises(KeyError):
        build_options = [
            "--cgroup-parent",
            "--compress",
            "--cpu-period",
            "--cpuset-mems 10",
        ]
        build_options_parser = BuildOptionsParser(build_options)
        build_options_parser.parse_build_options()


def test_filtered_valid_build_options():
    build_options = [
        "--rm",
        "--file test",
        "--tag image",
        "--add-host=github.com:192.30.255.112",
        "--add-host=ports.ubuntu.com:91.189.88.150",
        "--cache-from a",
        "--cache-from b",
        "--network bridge",
        "--platform Linux",
        "--cpu-shares 50",
        "--memory 10000000",
        "--pull=true",
        "-q=false",
        "--no-cache"
    ]
    sdk_options = {
        'extra_hosts': {
            'github.com': '192.30.255.112',
            'ports.ubuntu.com': '91.189.88.150'
        },
        'cache_from': ['a', 'b'],
        'network_mode': 'bridge',
        'platform': 'Linux',
        'container_limits': {
            'cpushares': '50',
            'memory': '10000000',
        },
        'pull': True,
        'quiet': False,
        'nocache': True
    }
    build_options_parser = BuildOptionsParser(build_options)
    assert sdk_options == build_options_parser.parse_build_options()
