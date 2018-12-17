import json
import os
import platform
import pytest
import shutil
import time

from iotedgedev.compat import PY35
from iotedgedev.connectionstring import (DeviceConnectionString,
                                         IoTHubConnectionString)
from iotedgedev.envvars import EnvVars
from iotedgedev.output import Output

from .utility import (assert_json_file_equal,
                      get_platform_type,
                      get_all_docker_images,
                      get_all_docker_containers,
                      remove_docker_container,
                      remove_docker_image,
                      get_docker_os_type,
                      runner_invoke)

pytestmark = pytest.mark.e2e

output = Output()
envvars = EnvVars(output)

root_dir = os.getcwd()
tests_dir = os.path.join(root_dir, "tests")

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


def add_module(template):
    module_name = template + "module"
    result = runner_invoke(["solution", "add", module_name, '--template', template])
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
        content = json.load(open(os.path.join(test_solution_dir, expected_template_file)))
        assert module_name in content["modulesContent"]["$edgeAgent"]["properties.desired"]["modules"]
        assert module_name in content["modulesContent"]["$edgeAgent"]["properties.desired"]["modules"][module_name]["settings"]["image"]
        assert module_name in content["modulesContent"]["$edgeHub"]["properties.desired"]["routes"]["sensorTo" + module_name]
        assert module_name in content["modulesContent"]["$edgeHub"]["properties.desired"]["routes"][module_name + "ToIoTHub"]


def assert_module_folder_structure(template):
    module_name = template + "module"
    expected_template_files = [os.environ["DEPLOYMENT_CONFIG_TEMPLATE_FILE"], os.environ["DEPLOYMENT_CONFIG_DEBUG_TEMPLATE_FILE"]]

    for expected_template_file in expected_template_files:
        content = json.load(open(expected_template_file))
        assert module_name in content["modulesContent"]["$edgeAgent"]["properties.desired"]["modules"]
        assert module_name in content["modulesContent"]["$edgeAgent"]["properties.desired"]["modules"][module_name]["settings"]["image"]
        assert module_name in content["modulesContent"]["$edgeHub"]["properties.desired"]["routes"][module_name + "ToIoTHub"]

        if expected_template_file == os.environ["DEPLOYMENT_CONFIG_DEBUG_TEMPLATE_FILE"]:
            if module_name in ["cmodule", "pythonmodule", "nodejsmodule", "javamodule"]:
                assert "HostConfig" in content["modulesContent"]["$edgeAgent"]["properties.desired"]["modules"][module_name]["settings"]["createOptions"]


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


def test_module_add(prepare_solution_with_env):
    launch_file = launch_json_file
    for template in templates:
        # Node.js modules is skipped on non-Windows for below known issue.
        # https://github.com/Azure/iotedgedev/issues/312
        # https://github.com/Azure/iotedgedev/issues/346
        if (template == "nodejs") and (platform.system().lower() != 'windows'):
            launch_file = launch_json_file_without_nodejs
        else:
            result = add_module(template)
            module_name = template + "module"
            assert 'ADD COMPLETE' in result.output
            assert os.path.exists(os.path.join(os.environ["MODULES_PATH"], module_name))
            assert_module_folder_structure(template)

    assert_json_file_equal(os.path.join(test_solution_dir, ".vscode", "launch.json"), launch_file)


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
    assert 'ERROR' not in result.output


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


def test_solution_build_with_platform():
    os.chdir(test_solution_shared_lib_dir)

    result = runner_invoke(['build', '-P', get_platform_type()])

    assert 'BUILD COMPLETE' in result.output
    assert 'ERROR' not in result.output


def test_solution_build_without_schema_template():
    try:
        os.chdir(test_solution_shared_lib_dir)

        os.rename('deployment.template.json', 'deployment.template.backup.json')
        template_without_schema_version = os.path.join(tests_dir, "assets", "deployment.template_without_schema.json")
        shutil.copyfile(template_without_schema_version, 'deployment.template.json')

        result = runner_invoke(['build', '-P', get_platform_type()])

        assert 'BUILD COMPLETE' in result.output
        assert 'ERROR' not in result.output
    finally:
        os.remove('deployment.template.json')
        os.rename('deployment.template.backup.json', 'deployment.template.json')


def test_create_new_solution():
    os.chdir(tests_dir)

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


def test_solution_build_with_default_platform(prepare_solution_with_env):
    result = runner_invoke(['build'])

    module_name = "filtermodule"
    test_solution_config_dir = os.path.join('config', 'deployment.' + get_platform_type() + '.json')
    env_container_registry_server = os.getenv("CONTAINER_REGISTRY_SERVER")

    assert 'BUILD COMPLETE' in result.output
    assert 'ERROR' not in result.output
    assert env_container_registry_server + "/" + module_name + ":0.0.1-" + get_platform_type() in json.load(open(test_solution_config_dir))[
        "modulesContent"]["$edgeAgent"]["properties.desired"]["modules"][module_name]["settings"]["image"]
    assert module_name in get_all_docker_images()


@pytest.mark.skipif(get_docker_os_type() == 'windows', reason='Debugger does not support C# in windows container')
def test_solution_build_with_debug_template():
    os.chdir(test_solution_shared_lib_dir)

    result = runner_invoke(['build', '-f', os.environ["DEPLOYMENT_CONFIG_DEBUG_TEMPLATE_FILE"], '-P', get_platform_type()])

    module_name = "sample_module"
    test_solution_shared_debug_config = os.path.join('config', 'deployment.debug.' + get_platform_type() + '.json')
    env_container_registry_server = os.getenv("CONTAINER_REGISTRY_SERVER")

    assert 'BUILD COMPLETE' in result.output
    assert 'ERROR' not in result.output
    assert env_container_registry_server + "/" + module_name + ":0.0.1-" + get_platform_type() + ".debug" in json.load(open(test_solution_shared_debug_config))[
        "modulesContent"]["$edgeAgent"]["properties.desired"]["modules"][module_name]["settings"]["image"]
    assert module_name in get_all_docker_images()


def test_solution_push_with_default_platform(prepare_solution_with_env):
    result = runner_invoke(['push'])

    module_name = "filtermodule"
    test_solution_config_dir = os.path.join('config', 'deployment.' + get_platform_type() + '.json')
    env_container_registry_server = os.getenv("CONTAINER_REGISTRY_SERVER")

    assert 'BUILD COMPLETE' in result.output
    assert 'PUSH COMPLETE' in result.output
    assert 'ERROR' not in result.output
    assert env_container_registry_server + "/" + module_name + ":0.0.1-" + get_platform_type() in json.load(open(test_solution_config_dir))[
        "modulesContent"]["$edgeAgent"]["properties.desired"]["modules"][module_name]["settings"]["image"]
    assert module_name in get_all_docker_images()


def test_generate_deployment_manifest():
    test_solution_build_with_platform()

    original_config_deployment_name = 'deployment.' + get_platform_type() + '.json'
    original_config_deployment_path = os.path.join(test_solution_shared_lib_dir, 'config', original_config_deployment_name)
    updated_config_deployment_name = 'deployment.' + get_platform_type() + '.backup.json'
    updated_config_deployment_path = os.path.join(test_solution_shared_lib_dir, 'config', updated_config_deployment_name)

    if os.path.exists(updated_config_deployment_path):
        os.remove(updated_config_deployment_path)
    os.rename(original_config_deployment_path, updated_config_deployment_path)

    if get_docker_os_type() == "windows":
        result = runner_invoke(['genconfig', '-P', get_platform_type()])
    else:
        result = runner_invoke(['genconfig'])

    assert 'ERROR' not in result.output
    assert_json_file_equal(original_config_deployment_path, updated_config_deployment_path)


@pytest.mark.skipif(get_docker_os_type() == 'windows', reason='windows container does not support local registry image')
def test_push_modules_to_local_registry(prepare_solution_with_env):
    env_container_registry_server = os.getenv("CONTAINER_REGISTRY_SERVER")
    try:
        module_name = "filtermodule"

        if module_name in get_all_docker_images():
            remove_docker_image(module_name)

        local_registry = "localhost:5000"
        envvars.set_envvar("CONTAINER_REGISTRY_SERVER", local_registry)

        result = runner_invoke(['push', '-P', get_platform_type()])
        if result.exit_code == 0:
            assert 'BUILD COMPLETE' in result.output
            assert 'PUSH COMPLETE' in result.output
            assert 'ERROR' not in result.output
            assert local_registry + "/" + module_name in get_all_docker_images()
        else:
            raise Exception(result.stdout)
    finally:
        envvars.set_envvar("CONTAINER_REGISTRY_SERVER", env_container_registry_server)
        if "registry" in get_all_docker_containers():
            remove_docker_container("registry")
        if "registry" in get_all_docker_images():
            remove_docker_image("registry:2")
