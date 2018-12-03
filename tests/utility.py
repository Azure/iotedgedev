import json

from iotedgedev.dockercls import Docker
from iotedgedev.envvars import EnvVars
from iotedgedev.output import Output
from iotedgedev.utility import Utility

output = Output()
envvars = EnvVars(output)


def assert_list_equal(list1, list2):
    assert len(list1) == len(list2) and sorted(list1) == sorted(list2)


def assert_file_equal(file1, file2):
    with open(file1, "r") as f1:
        with open(file2, "r") as f2:
            assert f1.read() == f2.read()


def assert_json_file_equal(file1, file2):
    with open(file1, "r") as f1:
        with open(file2, "r") as f2:
            assert json.load(f1) == json.load(f2)


def get_docker_client():
    envvars.load()
    utility = Utility(envvars, output)
    docker_client = Docker(envvars, utility, output)
    return docker_client


def get_docker_os_type():
    if get_docker_client().get_os_type().lower() == 'windows':
        platform_type = 'windows-amd64'
    else:
        platform_type = 'amd64'
    return platform_type
