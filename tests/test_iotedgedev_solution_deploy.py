import json
import os
import shutil
import time
from unittest import mock

import pytest
from iotedgedev.envvars import EnvVars
from iotedgedev.output import Output
from iotedgedev.version import PY35

from .utility import (get_docker_os_type,
                      get_platform_type, runner_invoke)

pytestmark = pytest.mark.e2e

output = Output()
envvars = EnvVars(output)

root_dir = os.getcwd()
tests_dir = os.path.join(root_dir, "tests")
tests_assets_dir = os.path.join(tests_dir, "assets")

env_file_name = envvars.get_dotenv_file()
env_file_path = envvars.get_dotenv_path(env_file_name)

launch_json_file = os.path.join(tests_dir, "assets", "launch.json")
launch_json_file_without_nodejs = os.path.join(tests_dir, "assets", "launch_without_nodejs.json")

test_solution = "test_solution"
test_solution_dir = os.path.join(tests_dir, test_solution)

test_solution_shared_lib = "test_solution_shared_lib"
test_solution_shared_lib_dir = os.path.join(tests_dir, "assets", test_solution_shared_lib)

templates = ["c", "csharp", "java", "nodejs", "python", "csharpfunction"]


def create_solution(template, custom_module_name=None):
    if custom_module_name is None:
        module_name = template + "module"
    else:
        module_name = custom_module_name
    result = runner_invoke(['new', test_solution, '-m', module_name, '-t', template])

    return result


def clean_folder(folder_path):
    os.chdir(tests_dir)
    time.sleep(5)
    shutil.rmtree(folder_path, ignore_errors=True)


@pytest.fixture
def prepare_solution_with_env():
    os.chdir(tests_dir)

    template = "csharp"
    module_name = "filtermodule"
    result = create_solution(template, module_name)
    if 'AZURE IOT EDGE SOLUTION CREATED' not in result.output:
        raise Exception(result.stdout)

    shutil.copyfile(env_file_path, os.path.join(test_solution_dir, env_file_name))

    os.chdir(test_solution_dir)

    yield prepare_solution_with_env
    clean_folder(test_solution_dir)

    return


def assert_solution_folder_structure(template):
    module_name = template + "module"

    expected_files = [".env", "deployment.template.json", "deployment.debug.template.json",
                      os.path.join(".vscode", "launch.json"),
                      os.path.join("modules", module_name, "Dockerfile.amd64"),
                      os.path.join("modules", module_name, "Dockerfile.amd64.debug"),
                      os.path.join("modules", module_name, "Dockerfile.arm32v7"),
                      os.path.join("modules", module_name, "module.json")]
    for expected_file in expected_files:
        assert os.path.exists(os.path.join(test_solution_dir, expected_file))

    expected_template_files = [os.environ["DEPLOYMENT_CONFIG_TEMPLATE_FILE"], os.environ["DEPLOYMENT_CONFIG_DEBUG_TEMPLATE_FILE"]]

    for expected_template_file in expected_template_files:
        with open(os.path.join(test_solution_dir, expected_template_file)) as f:
            content = json.load(f)

        assert module_name in content["modulesContent"]["$edgeAgent"]["properties.desired"]["modules"]
        assert module_name in content["modulesContent"]["$edgeAgent"]["properties.desired"]["modules"][module_name]["settings"]["image"]
        assert module_name in content["modulesContent"]["$edgeHub"]["properties.desired"]["routes"]["sensorTo" + module_name]
        assert module_name in content["modulesContent"]["$edgeHub"]["properties.desired"]["routes"][module_name + "ToIoTHub"]


def assert_module_folder_structure(template):
    module_name = template + "module"
    expected_template_files = [os.environ["DEPLOYMENT_CONFIG_TEMPLATE_FILE"], os.environ["DEPLOYMENT_CONFIG_DEBUG_TEMPLATE_FILE"]]

    for expected_template_file in expected_template_files:
        with open(expected_template_file) as f:
            content = json.load(f)

        assert module_name in content["modulesContent"]["$edgeAgent"]["properties.desired"]["modules"]
        assert module_name in content["modulesContent"]["$edgeAgent"]["properties.desired"]["modules"][module_name]["settings"]["image"]
        assert module_name in content["modulesContent"]["$edgeHub"]["properties.desired"]["routes"][module_name + "ToIoTHub"]

        if expected_template_file == os.environ["DEPLOYMENT_CONFIG_DEBUG_TEMPLATE_FILE"]:
            if module_name in ["cmodule", "pythonmodule", "nodejsmodule", "javamodule"]:
                assert "HostConfig" in content["modulesContent"]["$edgeAgent"]["properties.desired"]["modules"][module_name]["settings"]["createOptions"]


@pytest.fixture
def test_push_modules():
    result = runner_invoke(['push', '-P', get_platform_type()])

    assert 'BUILD COMPLETE' in result.output
    assert 'PUSH COMPLETE' in result.output
    assert 'ERROR' not in result.output


@pytest.fixture
def test_deploy_modules():
    if get_docker_os_type() == "windows":
        result = runner_invoke(['deploy', '-f', os.path.join('config', 'deployment.' + get_platform_type() + '.json')])
    else:
        result = runner_invoke(['deploy'])

    assert 'DEPLOYMENT COMPLETE' in result.output
    assert 'ERROR' not in result.output.replace('ERROR: Error while checking for extension', '')


@pytest.fixture
def test_monitor(capfd):
    runner_invoke(['monitor', '--timeout', '5'])

    out, err = capfd.readouterr()
    if not PY35:
        assert 'Monitoring events from device' in out
    else:
        assert not err


def get_connection_string_value(key: str) -> str:

    connection_string_values = os.environ["DEVICE_CONNECTION_STRING"].split(';')
    device_id = None

    for item in connection_string_values:
        if key in item:
            device_id = item.split('=')[1]

    return device_id


@ mock.patch.dict(os.environ, {"DEVICE_CONNECTION_STRING": f"HostName={get_connection_string_value('HostName')};DeviceId={get_connection_string_value('DeviceId')};=testaccesskey"})
def test_solution_deploy_with_sas_connection_string():
    # Arrange
    os.chdir(test_solution_shared_lib_dir)

    # Act
    result = runner_invoke(['solution', 'deploy'])

    # Assert
    assert 'DEPLOYMENT COMPLETE' in result.output
    assert 'ERROR' not in result.output


@ mock.patch.dict(os.environ, {"DEVICE_CONNECTION_STRING": f"HostName={get_connection_string_value('HostName')};DeviceId={get_connection_string_value('DeviceId')};x509=true;"})
def test_solution_deploy_with_x509_connection_string():
    # Arrange
    os.chdir(test_solution_shared_lib_dir)

    # Act
    runner_invoke(['build', '-f', "deployment.template.json", '-P', get_platform_type()])
    result = runner_invoke(['solution', 'deploy'])

    # Assert
    assert 'DEPLOYMENT COMPLETE' in result.output
    assert 'ERROR' not in result.output


@ mock.patch.dict(os.environ, {"DEVICE_CONNECTION_STRING": "HostName=test-iothub.azure-devices.net;SharedAccessKey=testaccesskey"})
def test_connection_string_no_device_id_throws_env_error():
    # Arrange
    os.chdir(test_solution_shared_lib_dir)

    # Act
    runner_invoke(['build', '-f', "deployment.template.json", '-P', get_platform_type()])
    with pytest.raises(Exception) as context:
        runner_invoke(['solution', 'deploy'])

    # Assert
    assert "ERROR: Environment Variable EDGE_DEVICE_ID not set." in str(context.value)
