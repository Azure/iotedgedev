import json
import os
import platform
import shutil
import time
from unittest import mock

import pytest
from iotedgedev.envvars import EnvVars
from iotedgedev.output import Output

from .utility import (get_all_docker_images, get_docker_os_type,
                      get_file_content, get_platform_type, runner_invoke,
                      update_file_content)

pytestmark = pytest.mark.e2e

output = Output()
envvars = EnvVars(output)

tests_dir = os.path.join(os.getcwd(), "tests")
tests_assets_dir = os.path.join(tests_dir, "assets")

env_file_name = envvars.get_dotenv_file()
env_file_path = envvars.get_dotenv_path(env_file_name)

launch_json_file = os.path.join(tests_dir, "assets", "launch.json")
launch_json_file_without_nodejs = os.path.join(tests_assets_dir, "launch_without_nodejs.json")
test_solution_shared_lib_dir = os.path.join(tests_assets_dir, "test_solution_shared_lib")


@pytest.fixture
def prepare_solution_with_env():
    os.chdir(tests_dir)
    test_solution = "test_solution"
    test_solution_dir = os.path.join(tests_dir, test_solution)
    template = "csharp"
    module_name = "filtermodule"
    result = runner_invoke(['new', test_solution, '-m', module_name, '-t', template])

    if 'AZURE IOT EDGE SOLUTION CREATED' not in result.output:
        raise Exception(result.stdout)

    shutil.copyfile(env_file_path, os.path.join(test_solution_dir, env_file_name))

    os.chdir(test_solution_dir)

    yield prepare_solution_with_env
    os.chdir(tests_dir)
    time.sleep(5)
    shutil.rmtree(test_solution_dir, ignore_errors=True)

    return


def test_solution_build_and_push_with_layered_deployment():
    # Arrange
    os.chdir(test_solution_shared_lib_dir)
    new_config_deployment_path = os.path.join(test_solution_shared_lib_dir, 'config', "layered_deployment.flattened_props.json")

    # Act
    result = runner_invoke(['build', '--push', '-f', "layered_deployment.flattened_props.template.json", '-P', get_platform_type()])

    # Assert
    assert os.path.exists(new_config_deployment_path)
    assert 'sample_module:0.0.1-RC' in result.output
    assert 'BUILD COMPLETE' in result.output
    assert 'PUSH COMPLETE' in result.output
    assert 'ERROR' not in result.output


def test_solution_build_and_push_with_layered_deployment_no_modules():
    # Arrange
    os.chdir(test_solution_shared_lib_dir)
    new_config_deployment_path = os.path.join(test_solution_shared_lib_dir, 'config', 'layered_deployment.no_modules.json')

    # Act
    result = runner_invoke(['build', '--push', '-f', "layered_deployment.no_modules.template.json", '-P', get_platform_type()])

    # Assert

    with open(new_config_deployment_path, "r") as f:
        content = json.load(f)

    set_property = content["content"]["modulesContent"]["exampleModule"]["properties.desired"]["foo"]

    assert 'ERROR' not in result.output
    assert 'bar-1.2' == set_property


def test_solution_build_and_push_with_platform():
    os.chdir(test_solution_shared_lib_dir)

    result = runner_invoke(['build', '-P', get_platform_type()])

    assert 'BUILD COMPLETE' in result.output
    assert 'PUSH COMPLETE' not in result.output
    assert 'sample_module:0.0.1-RC' in result.output
    assert 'sample_module_2:0.0.1-RC' in result.output
    assert 'ERROR' not in result.output

    result = runner_invoke(['push', '--no-build', '-P', get_platform_type()])

    assert 'PUSH COMPLETE' in result.output
    assert 'BUILD COMPLETE' not in result.output
    assert 'sample_module:0.0.1-RC' in result.output
    assert 'sample_module_2:0.0.1-RC' in result.output
    assert 'ERROR' not in result.output


def test_solution_build_and_push_with_different_cwd():
    cwd = os.path.join(test_solution_shared_lib_dir, 'config')
    if not os.path.exists(cwd):
        os.makedirs(cwd)
    os.chdir(cwd)

    result = runner_invoke(['build', '-f', '../deployment.template.json', '-P', get_platform_type()])

    assert 'BUILD COMPLETE' in result.output
    assert 'sample_module:0.0.1-RC' in result.output
    assert 'sample_module_2:0.0.1-RC' in result.output
    assert 'ERROR' not in result.output

    result = runner_invoke(['push', '-f', '../deployment.template.json', '--no-build', '-P', get_platform_type()])

    assert 'PUSH COMPLETE' in result.output
    assert 'sample_module:0.0.1-RC' in result.output
    assert 'sample_module_2:0.0.1-RC' in result.output
    assert 'ERROR' not in result.output


@pytest.mark.skipif(platform.system().lower() != 'windows', reason='The path is not valid in non windows platform')
def test_solution_build_and_push_with_escapedpath():
    os.chdir(test_solution_shared_lib_dir)

    result = runner_invoke(['build', '-f', 'deployment.escapedpath.template.json', '-P', get_platform_type()])

    assert 'BUILD COMPLETE' in result.output
    assert 'sample_module_2:0.0.1-RC' in result.output
    assert 'ERROR' not in result.output

    result = runner_invoke(['push', '--no-build', '-P', get_platform_type()])

    assert 'PUSH COMPLETE' in result.output
    assert 'sample_module_2:0.0.1-RC' in result.output
    assert 'ERROR' not in result.output


@mock.patch.dict(os.environ, {"VERSION": "0.0.2"})
def test_solution_build_with_version_and_build_options():
    os.chdir(test_solution_shared_lib_dir)
    module_json_file_path = os.path.join(test_solution_shared_lib_dir, "modules", "sample_module", "module.json")
    module_2_json_file_path = os.path.join(test_solution_shared_lib_dir, "sample_module_2", "module.json")
    try:
        update_file_content(module_json_file_path, '"version": "0.0.1-RC"', '"version": "${VERSION}"')
        update_file_content(module_json_file_path, '"buildOptions": (.*),', '"buildOptions": [ "--add-host=github.com:192.30.255.112", "--build-arg a=b" ],')
        update_file_content(module_2_json_file_path, '"version": "0.0.1-RC"', '"version": "${VERSION}"')
        update_file_content(module_2_json_file_path, '"buildOptions": (.*),', '"buildOptions": [ "--add-host=github.com:192.30.255.112", "--build-arg a=b" ],')

        result = runner_invoke(['build', '-P', get_platform_type()])

        assert 'BUILD COMPLETE' in result.output
        assert 'sample_module:0.0.2' in result.output
        assert 'sample_module_2:0.0.2' in result.output
        assert 'ERROR' not in result.output
        assert '0.0.2' in get_all_docker_images()

    finally:
        update_file_content(module_json_file_path, '"version": "(.*)"', '"version": "0.0.1-RC"')
        update_file_content(module_json_file_path, '"buildOptions": (.*),', '"buildOptions": [],')
        update_file_content(module_2_json_file_path, '"version": "(.*)"', '"version": "0.0.1-RC"')
        update_file_content(module_2_json_file_path, '"buildOptions": (.*),', '"buildOptions": [],')


def test_solution_build_without_schema_template():
    try:
        os.chdir(test_solution_shared_lib_dir)

        os.rename('deployment.template.json', 'deployment.template.backup.json')
        template_without_schema_version = os.path.join(tests_dir, "assets", "deployment.template_without_schema_template.json")
        shutil.copyfile(template_without_schema_version, 'deployment.template.json')

        update_file_content('deployment.template.json', '"image": "(.*)MODULES.sample_module}",', '"image": "${MODULES.sample_module.' + get_platform_type() + '}",')

        result = runner_invoke(['build'])

        assert 'BUILD COMPLETE' in result.output
        assert 'ERROR' not in result.output

        config_file_path = os.path.join(test_solution_shared_lib_dir, "config", "deployment.json")
        assert os.path.exists(config_file_path)

        content = get_file_content(config_file_path)
        assert "sample_module:0.0.1-RC-" + get_platform_type() in content
    finally:
        os.remove('deployment.template.json')
        os.rename('deployment.template.backup.json', 'deployment.template.json')


def test_solution_build_with_default_platform(prepare_solution_with_env):
    result = runner_invoke(['build'])

    module_name = "filtermodule"
    test_solution_config_dir = os.path.join('config', 'deployment.' + get_platform_type() + '.json')
    env_container_registry_server = os.getenv("CONTAINER_REGISTRY_SERVER")
    with open(test_solution_config_dir) as f:
        content = json.load(f)

    assert 'BUILD COMPLETE' in result.output
    assert 'ERROR' not in result.output
    assert env_container_registry_server + "/" + module_name + ":0.0.1-" + get_platform_type() in content[
        "modulesContent"]["$edgeAgent"]["properties.desired"]["modules"][module_name]["settings"]["image"]
    assert module_name in get_all_docker_images()


@pytest.mark.skipif(get_docker_os_type() == 'windows', reason='Debugger does not support C# in windows container')
def test_solution_build_with_debug_template():
    os.chdir(test_solution_shared_lib_dir)

    result = runner_invoke(['build', '-f', os.environ["DEPLOYMENT_CONFIG_DEBUG_TEMPLATE_FILE"], '-P', get_platform_type()])

    module_name = "sample_module"
    module_2_name = "sample_module_2"
    test_solution_shared_debug_config = os.path.join('config', 'deployment.debug.' + get_platform_type() + '.json')
    env_container_registry_server = os.getenv("CONTAINER_REGISTRY_SERVER")
    with open(test_solution_shared_debug_config) as f:
        content = json.load(f)

    assert 'BUILD COMPLETE' in result.output
    assert 'ERROR' not in result.output
    assert env_container_registry_server + "/" + module_name + ":0.0.1-RC-" + get_platform_type() + ".debug" in content[
        "modulesContent"]["$edgeAgent"]["properties.desired"]["modules"][module_name]["settings"]["image"]
    assert env_container_registry_server + "/" + module_2_name + ":0.0.1-RC-" + get_platform_type() + ".debug" in content[
        "modulesContent"]["$edgeAgent"]["properties.desired"]["modules"][module_2_name]["settings"]["image"]
    all_docker_images = get_all_docker_images()
    assert module_name in all_docker_images
    assert module_2_name in all_docker_images


# # TODO: The output of docker build logs is not captured by pytest, need to capture this before enable this test
# def test_docker_build_status_output():
#     prune_docker_images()
#     prune_docker_containers()
#     prune_docker_build_cache()
#     remove_docker_image("sample_module:0.0.1-RC")

#     os.chdir(test_solution_shared_lib_dir)

#     result = runner_invoke(['build', '-P', get_platform_type()])

#     assert re.match('\\[=*>\\s*\\]', result.output) is not None
