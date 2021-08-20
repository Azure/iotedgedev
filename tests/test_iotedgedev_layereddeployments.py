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

output = Output()
envvars = EnvVars(output)
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
    assert 'bar-1.0' == set_property


@pytest.mark.parametrize(
    "config",
    [
        "layered_deployment.template_with_flattened_props.json",
        "layered_deployment.template_with_no_modules.json"
    ]
)
def test_deploy(config):
    try:
        # Arrange
        deployment_name = f'test-{uuid.uuid4()}'
        os.chdir(test_solution_shared_lib_dir)
        # Test that cmd line target condition (-t) overrides target condition from .env
        envvars.set_envvar("LAYERED_DEPLOYMENT_TARGET_CONDITION", "invalid_target")

        # Act
        result = runner_invoke(['build', '--push', '-f', config, '-P', get_platform_type()])
        result = runner_invoke(['deployment',
                                '-f', f'config/{config}',
                                '-n', deployment_name,
                                '-p', '10',
                                '-t', "tags.environment='dev'"
                                ])

        # Assert
        assert 'DEPLOYMENT COMPLETE' in result.output
        assert 'ERROR' not in result.output
    finally:
        # Cleanup
        azure_cli = AzureCli(output, envvars)

        del os.environ["LAYERED_DEPLOYMENT_TARGET_CONDITION"]
        assert azure_cli.invoke_az_cli_outproc(["iot", "edge", "deployment", "delete", "-d", deployment_name, "-l", envvars.get_envvar("IOTHUB_CONNECTION_STRING")])


def test_deploy_with_target_group_set_from_dotenv():
    try:
        # Arrange
        deployment_name = f'test-{uuid.uuid4()}'
        os.chdir(test_solution_shared_lib_dir)
        envvars.set_envvar("LAYERED_DEPLOYMENT_TARGET_CONDITION", "tags.environment='dev'")

        # Act
        result = runner_invoke(['build', '--push', '-f', "layered_deployment.template_with_flattened_props.json", '-P', get_platform_type()])
        result = runner_invoke(['deployment',
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

        assert azure_cli.invoke_az_cli_outproc(["iot", "edge", "deployment", "delete", "-d", deployment_name, "-l", envvars.get_envvar("IOTHUB_CONNECTION_STRING")])


def test_deploy_error_from_az_cli_bubbled_up():
    # Arrange
    deployment_name = f'test-{uuid.uuid4()}'
    os.chdir(test_solution_shared_lib_dir)

    # Act
    result = runner_invoke(['build', '--push', '-f', "layered_deployment.template_with_flattened_props.json", '-P', get_platform_type()])
    result = runner_invoke(['deployment',
                            '-f', 'config/layered_deployment.template_with_flattened_props.json',
                            '-n', deployment_name,
                            '-p', '10',
                            '-t', "invalid_target_group"
                            ])

    # Assert
    assert "ERROR: {'Message': 'ErrorCode:ArgumentInvalid;BadRequest'," in result.output


def test_deploy_error_missing_name():
    with pytest.raises(Exception) as context:
        # Act
        runner_invoke(['deployment', '-n', "test"])

    # Assert
    assert "Error: Missing option '--priority' / '-p'." in str(context)


def test_deploy_error_missing_priority():
    with pytest.raises(Exception) as context:
        # Act
        runner_invoke(['deployment', '-n', "test"])

    # Assert
    assert "Error: Missing option '--priority' / '-p'." in str(context)


def test_deploy_error_missing_target_condition():

    with pytest.raises(Exception) as context:
        # Act
        runner_invoke(['deployment', '-n', "test", '-p', '10'])

    # Assert
    assert "ERROR: Environment Variable LAYERED_DEPLOYMENT_TARGET_CONDITION not set. Either add to .env file or to your system's Environment Variables" in str(context.value)
