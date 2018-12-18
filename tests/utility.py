import json
import re
import subprocess

from click.testing import CliRunner
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
    envvars.load(force=True)
    utility = Utility(envvars, output)
    docker_client = Docker(envvars, utility, output)
    docker_client.init_registry()
    return docker_client


def get_docker_os_type():
    os_type = get_docker_client().get_os_type().lower()
    return os_type


def get_platform_type():
    if get_docker_os_type() == 'windows':
        platform_type = 'windows-amd64'
    else:
        platform_type = 'amd64'
    return platform_type


def get_all_docker_containers():
    output = start_process(['docker', 'ps', '-a'], False)
    return output


def get_all_docker_images():
    output = start_process(['docker', 'image', 'ls'], False)
    return output


def remove_docker_container(container_name):
    output = start_process(['docker', 'rm', '-f', container_name], False)
    return output


def remove_docker_image(image_name):
    output = start_process(['docker', 'rmi', '-f', image_name], False)
    return output


def runner_invoke(args, expect_failure=False):
    runner = CliRunner()
    with runner.isolation(env={"DEFAULT_PLATFORM": get_platform_type()}):
        cli = __import__("iotedgedev.cli", fromlist=['main'])
        result = runner.invoke(cli.main, args)
        if (result.exit_code == 0) or (expect_failure is True):
            return result
        else:
            raise Exception(result.stdout)


def start_process(command, is_shell):
    process = subprocess.Popen(command, shell=is_shell,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = process.communicate()
    if process.returncode == 0:
        return str(output)
    else:
        raise Exception(error)


def update_file_content(file_path, actual_value, expected_value):
    with open(file_path, "r+") as f:
        stream_data = f.read()
        ret = re.sub(actual_value, expected_value, stream_data)
        f.seek(0)
        f.truncate()
        f.write(ret)
