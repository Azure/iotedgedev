import json
import os
import pytest
import uuid
from .utility import (
    get_platform_type,
    runner_invoke,
)

from iotedgedev.envvars import EnvVars
from iotedgedev.output import Output
from iotedgedev.azurecli import AzureCli

pytestmark = pytest.mark.e2e

test_solution_shared_lib_dir = os.path.join(os.getcwd(), "tests", "assets", "test_solution_shared_lib")


def test_build_and_push():
    os.chdir(test_solution_shared_lib_dir)

    result = runner_invoke(['build', '--push', '-f', "layered_deployment.template_with_flattened_props.json", '-P', get_platform_type()])

    assert 'sample_module:0.0.1-RC' in result.output
    assert 'BUILD COMPLETE' in result.output
    assert 'PUSH COMPLETE' in result.output
    assert 'ERROR' not in result.output


def test_build_and_push_with_no_modules():
    os.chdir(test_solution_shared_lib_dir)

    result = runner_invoke(['build', '--push', '-f', "layered_deployment.template_with_no_modules.json", '-P', get_platform_type()])

    new_config_deployment_name = 'layered_deployment.template_with_no_modules.json'
    new_config_deployment_path = os.path.join(test_solution_shared_lib_dir, 'config', new_config_deployment_name)

    with open(new_config_deployment_path, "r") as f:
        content = json.load(f)

    set_property = content["content"]["modulesContent"]["exampleModule"]["properties.desired"]["foo"]

    assert 'ERROR' not in result.output
    assert 'bar-1.2' == set_property


def test_deploy():
    try:
        # Arrange
        deployment_name = f'test-{uuid.uuid4()}'
        output = Output()
        envvars = EnvVars(output)

        os.chdir(test_solution_shared_lib_dir)
        envvars.set_envvar("LAYERED_DEPLOYMENT_TARGET_CONDITION", "tags.environment='dev'")

        # Act
        result = runner_invoke(['build', '--push', '-f', "layered_deployment.template_with_flattened_props.json", '-P', get_platform_type()])
        result = runner_invoke(['deploy-layered',
                                '-f', 'config/layered_deployment.template_with_flattened_props.json',
                                '-n', deployment_name,
                                '-p', '10',
                                ])

        # Assert
        assert 'DEPLOYMENT COMPLETE' in result.output
        assert 'ERROR' not in result.output
    finally:
        # Cleanup
        del os.environ["LAYERED_DEPLOYMENT_TARGET_CONDITION"]
        azure_cli = AzureCli(output, envvars)
        envvars.load()

        assert azure_cli.invoke_az_cli_outproc(["iot", "edge", "deployment", "delete", "-d", deployment_name, "-n", envvars.IOTHUB_CONNECTION_INFO.iothub_host.hub_name])


# TODO: Add tests cases:
# - Verify error message is in the logs
# - Verify deployment doesn't fail with LAYERED_DEPLOYMENT_TARGET_CONDITION not set
# -
