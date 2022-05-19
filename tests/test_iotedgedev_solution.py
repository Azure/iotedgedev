import json
import os
import platform
import shutil
import time
from unittest import mock
from webbrowser import get

import pytest
from iotedgedev.connectionstring import (DeviceConnectionString,
                                         IoTHubConnectionString)
from iotedgedev.envvars import EnvVars
from iotedgedev.output import Output
from iotedgedev.version import PY35

from .utility import (assert_json_file_equal, get_all_docker_containers,
                      get_all_docker_images, get_docker_os_type,
                      get_platform_type, remove_docker_container,
                      remove_docker_image, runner_invoke)

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


def test_solution_create_in_non_empty_current_path(prepare_solution_with_env):
    result = runner_invoke(['solution', 'new', '.'], True)

    assert "Directory is not empty" in result.output


def test_solution_create_in_empty_current_path(prepare_solution_with_env):
    dirname = "emptydir_current"
    os.makedirs(dirname)
    os.chdir(os.path.join(test_solution_dir, dirname))

    result = runner_invoke(['solution', 'new', '.'])

    assert 'AZURE IOT EDGE SOLUTION CREATED' in result.output


def test_solution_create_in_non_empty_dir(prepare_solution_with_env):
    os.chdir(tests_dir)

    result = runner_invoke(['solution', 'new', test_solution], True)

    assert "Directory is not empty" in result.output


def test_solution_create_in_empty_child_dir(prepare_solution_with_env):
    dirname = "emptydir"
    os.makedirs(dirname)

    result = runner_invoke(['solution', 'new', dirname])

    assert 'AZURE IOT EDGE SOLUTION CREATED' in result.output


def test_solution_create_valid_runtime_tag():
    dirname = "empty_dir"
    os.makedirs(dirname)

    result = runner_invoke(['solution', 'new', dirname, '-er', '1.1'])

    assert 'AZURE IOT EDGE SOLUTION CREATED' in result.output
    shutil.rmtree(dirname, ignore_errors=True)


def test_solution_create_invalid_runtime_tag():
    result = runner_invoke(['solution', 'new', "empty_invalid_dir", '-er', '6'])

    assert '-edge-runtime-version `6` is not valid' in result.output


def test_module_add(prepare_solution_with_env):
    launch_file = launch_json_file
    for template in templates:
        # Node.js modules is skipped on non-Windows for below known issue.
        # https://github.com/Azure/iotedgedev/issues/312
        # https://github.com/Azure/iotedgedev/issues/346
        if (template == "nodejs") and (platform.system().lower() != 'windows'):
            launch_file = launch_json_file_without_nodejs
        else:
            module_name = template + "module"
            result = runner_invoke(["solution", "add", module_name, '--template', template])
            assert 'ADD COMPLETE' in result.output
            assert os.path.exists(os.path.join(os.environ["MODULES_PATH"], module_name))
            assert_module_folder_structure(template)

    assert_json_file_equal(os.path.join(test_solution_dir, ".vscode", "launch.json"), launch_file)


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


def test_module_add_invalid_name(prepare_solution_with_env):
    """Test the addmodule command with invalid module name"""

    result = runner_invoke(["solution", "add", "_csharpmodule", "--template", "csharp"], True)
    assert "Module name cannot start or end with the symbol _" in result.output

    result = runner_invoke(["solution", "add", "csharpmodule_", "--template", "csharp"], True)
    assert "Module name cannot start or end with the symbol _" in result.output

    result = runner_invoke(["solution", "add", "csharp-module", "--template", "csharp"], True)
    assert "Module name can only contain alphanumeric characters and the symbol _" in result.output

    result = runner_invoke(["solution", "add", "filtermodule", "--template", "csharp"], True)
    assert "already exists under" in result.output


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


def test_e2e(prepare_solution_with_env, test_push_modules, test_deploy_modules, test_monitor):
    print("Testing e2e with env file")


def get_connection_string_value(key: str) -> str:

    connection_string_values = os.environ["DEVICE_CONNECTION_STRING"].split(';')
    device_id = None

    for item in connection_string_values:
        if key in item:
            device_id = item.split('=')[1]

    return device_id


def test_valid_env_iothub_connectionstring():
    """Test for loading data of env file"""

    env_iothub_connectionstring = os.getenv("IOTHUB_CONNECTION_STRING")
    connectionstring = IoTHubConnectionString(env_iothub_connectionstring)

    assert connectionstring.iothub_host.name
    assert connectionstring.iothub_host.hub_name
    assert connectionstring.shared_access_key
    assert connectionstring.shared_access_key_name


def test_valid_env_device_connectionstring():
    """Test for loading data of env file"""

    env_device_connectionstring = os.getenv("DEVICE_CONNECTION_STRING")
    connectionstring = DeviceConnectionString(env_device_connectionstring)

    assert connectionstring.iothub_host.name
    assert connectionstring.iothub_host.hub_name
    assert connectionstring.shared_access_key
    assert connectionstring.device_id


def test_create_new_solution():
    os.chdir(tests_dir)
    clean_folder(test_solution_dir)

    for template in templates:
        # Node.js modules is skipped on non-Windows for below known issue.
        # https://github.com/Azure/iotedgedev/issues/312
        # https://github.com/Azure/iotedgedev/issues/346
        if (template == "nodejs") and (platform.system().lower() != 'windows'):
            continue
        else:
            result = create_solution(template)
            assert_solution_folder_structure(template)
            assert 'AZURE IOT EDGE SOLUTION CREATED' in result.output
            clean_folder(test_solution_dir)


def test_solution_push_with_default_platform(prepare_solution_with_env):
    result = runner_invoke(['push'])

    module_name = "filtermodule"
    test_solution_config_dir = os.path.join('config', 'deployment.' + get_platform_type() + '.json')
    env_container_registry_server = os.getenv("CONTAINER_REGISTRY_SERVER")
    with open(test_solution_config_dir) as f:
        content = json.load(f)

    assert 'BUILD COMPLETE' in result.output
    assert 'PUSH COMPLETE' in result.output
    assert 'ERROR' not in result.output
    assert env_container_registry_server + "/" + module_name + ":0.0.1-" + get_platform_type() in content[
        "modulesContent"]["$edgeAgent"]["properties.desired"]["modules"][module_name]["settings"]["image"]
    assert module_name in get_all_docker_images()


def test_generate_deployment_manifest():
    try:
        os.chdir(test_solution_shared_lib_dir)
        shutil.copyfile(env_file_path, os.path.join(test_solution_shared_lib_dir, env_file_name))

        new_config_deployment_name = 'deployment.' + get_platform_type() + '.json'
        new_config_deployment_path = os.path.join(test_solution_shared_lib_dir, 'config', new_config_deployment_name)

        if get_docker_os_type() == "windows":
            result = runner_invoke(['genconfig', '-P', get_platform_type()])
        else:
            result = runner_invoke(['genconfig'])

        assert 'ERROR' not in result.output

        with open(new_config_deployment_path, "r") as f:
            content = json.load(f)

        module_image_name = content["modulesContent"]["$edgeAgent"]["properties.desired"]["modules"][
            "sample_module"]["settings"]["image"]
        module_2_image_name = content["modulesContent"]["$edgeAgent"]["properties.desired"]["modules"][
            "sample_module_2"]["settings"]["image"]
        env_container_registry_server = os.getenv("CONTAINER_REGISTRY_SERVER")
        assert env_container_registry_server + "/sample_module:0.0.1-RC-" + get_platform_type() == module_image_name
        assert env_container_registry_server + "/sample_module_2:0.0.1-RC-" + get_platform_type() == module_2_image_name

    finally:
        os.remove(os.path.join(test_solution_shared_lib_dir, env_file_name))


def test_validate_deployment_template_and_manifest_failed():
    try:
        deployment_file_name = "deployment.template_invalidresult.json"
        os.chdir(tests_assets_dir)
        shutil.copyfile(env_file_path, os.path.join(tests_assets_dir, env_file_name))

        if get_docker_os_type() == "windows":
            result = runner_invoke(['genconfig', '-P', get_platform_type(), '-f', deployment_file_name])
        else:
            result = runner_invoke(['genconfig', '-f', deployment_file_name])

        assert "ERROR" not in result.output
        # File name should be printed
        assert "Validating generated deployment manifest %s" % os.path.join("config", deployment_file_name) in result.output
        # All schema errors should be detected, not only the first error
        assert "Warning: Deployment manifest schema error: 'address' is a required property. "
        "Property path:modulesContent->$edgeAgent->properties.desired->runtime->settings->registryCredentials->test" in result.output
        assert "Warning: Deployment manifest schema error: 1 is not of type 'string'. "
        "Property path:modulesContent->$edgeAgent->properties.desired->runtime->settings->registryCredentials->test->username" in result.output
        # Schema errors resulted by expanding environment variables should be detected
        assert "Warning: Deployment manifest schema error: '' does not match '^[^\\s]+$'. "
        "Property path:modulesContent->$edgeAgent->properties.desired->runtime->settings->registryCredentials->test2->address" in result.output
        assert "Warning: Deployment manifest schema validation failed" in result.output
        assert "Deployment manifest schema validation passed" not in result.output
        assert "Validating createOptions for module csharpmodule" in result.output
        assert "createOptions of module csharpmodule validation passed" in result.output
        assert "Warning: createOptions of module edgeAgent should be an object" in result.output
        assert "Warning: Errors found during createOptions validation" in result.output
        assert "Validation for all createOptions passed" not in result.output

    finally:
        os.remove(os.path.join(tests_assets_dir, env_file_name))


@mock.patch.dict(os.environ, {"CONTAINER_REGISTRY_PASSWORD": "nonempty"})
def test_validate_deployment_template_and_manifest_success():
    try:
        deployment_file_name = "deployment.template.json"
        os.chdir(test_solution_shared_lib_dir)
        shutil.copyfile(env_file_path, os.path.join(test_solution_shared_lib_dir, env_file_name))

        if get_docker_os_type() == "windows":
            result = runner_invoke(['genconfig', '-P', get_platform_type(), '-f', deployment_file_name])
        else:
            result = runner_invoke(['genconfig', '-f', deployment_file_name])

        assert "ERROR" not in result.output
        assert "Deployment manifest schema validation passed" in result.output
        assert "Warning: Deployment manifest schema validation failed" not in result.output
        assert "Validation for all createOptions passed" in result.output
        assert "Warning: Errors found during createOptions validation" not in result.output

    finally:
        os.remove(os.path.join(test_solution_shared_lib_dir, env_file_name))


def test_validate_create_options_failed():
    os.chdir(tests_assets_dir)
    deployment_file_name = "deployment.manifest_invalid.json"

    if get_docker_os_type() == "windows":
        result = runner_invoke(['genconfig', '-P', get_platform_type(), '-f', deployment_file_name])
    else:
        result = runner_invoke(['genconfig', '-f', deployment_file_name])

    assert "ERROR" not in result.output
    assert "Warning: Length of createOptions01 in module tempSensor exceeds 512" in result.output
    assert "Warning: Length of createOptions02 in module tempSensor exceeds 512" in result.output
    assert "Warning: createOptions of module csharpmodule is not a valid JSON string" in result.output
    assert "Warning: createOptions of module csharpfunction should be an object" in result.output
    assert "Warning: createOptions of module csharpfunction2 is not a valid JSON string" in result.output
    assert "No settings or createOptions property found in module edgeAgent. Skip createOptions validation." in result.output
    assert "createOptions of module edgeHub validation passed" in result.output
    assert "Warning: Errors found during createOptions validation" in result.output


@pytest.mark.parametrize(
    "deployment_file_name",
    ["deployment.manifest_invalid.json", "deployment.manifest_invalid_schema.json", "deployment.manifest_invalid_createoptions.json"]
)
def test_fail_gen_config_on_validation_error(deployment_file_name):
    os.chdir(tests_assets_dir)

    with pytest.raises(Exception) as context:
        if get_docker_os_type() == "windows":
            result = runner_invoke(['genconfig', '-P', get_platform_type(), '-f', deployment_file_name, '--fail-on-validation-error'])
        else:
            result = runner_invoke(['genconfig', '-f', deployment_file_name, '--fail-on-validation-error'])

    if get_docker_os_type() == "windows":
        result = runner_invoke(['genconfig', '-P', get_platform_type(), '-f', deployment_file_name])
    else:
        result = runner_invoke(['genconfig', '-f', deployment_file_name])

    assert "ERROR: Deployment manifest validation failed. Please see previous logs for more details." in str(context.value)
    assert "ERROR" not in result.output


@mock.patch.dict(os.environ, {"TTL": "7200"})
def test_gen_config_with_non_string_placeholder():
    os.chdir(tests_assets_dir)
    deployment_file_name = "deployment.template.non_str_placeholder.json"
    if get_docker_os_type() == "windows":
        result = runner_invoke(['genconfig', '-P', get_platform_type(), '-f', deployment_file_name, '--fail-on-validation-error'])
    else:
        result = runner_invoke(['genconfig', '-f', deployment_file_name, '--fail-on-validation-error'])

    assert "ERROR" not in result.output


@mock.patch.dict(os.environ, {"CONTAINER_REGISTRY_SERVER": "localhost:5000"})
@pytest.mark.skipif(get_docker_os_type() == 'windows', reason='windows container does not support local registry image')
def test_push_modules_to_local_registry(prepare_solution_with_env):
    try:
        module_name = "filtermodule"

        if module_name in get_all_docker_images():
            remove_docker_image(module_name)

        result = runner_invoke(['push', '-P', get_platform_type()])

        assert 'ERROR' not in result.output
        assert result.exit_code == 0
        assert 'BUILD COMPLETE' in result.output
        assert 'PUSH COMPLETE' in result.output
        assert f"localhost:5000/{module_name in get_all_docker_images()}"
    finally:
        if "registry" in get_all_docker_containers():
            remove_docker_container("registry")
        if "registry" in get_all_docker_images():
            remove_docker_image("registry:2")
