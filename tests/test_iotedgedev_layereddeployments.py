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


def test_build_and_push_with_no_modules():
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
    assert 'bar-1.0' == set_property


@pytest.mark.parametrize(
    "config",
    [
        "layered_deployment.flattened_props.template.json",
        "layered_deployment.no_modules.template.json",
        "deployment.template.json"
    ]
)
def test_deployment(config):
    try:
        # Arrange
        deployment_name = f'test-{uuid.uuid4()}'
        os.chdir(test_solution_shared_lib_dir)
        # Test that cmd line target condition (-t) overrides target condition from .env
        envvars.set_envvar("LAYERED_DEPLOYMENT_TARGET_CONDITION", "invalid_target")

        # Act
        result = runner_invoke(['build', '--push', '-f', config, '-P', get_platform_type()])
        result = runner_invoke(['deployment',
                                '-f', f'config/{config.replace("template.", "")}',
                                '-n', deployment_name,
                                '-p', '10',
                                '-t', "tags.environment='dev'"
                                ])

        # Assert
        assert 'DEPLOYMENT COMPLETE' in result.output
        assert 'ERROR' not in result.output
    finally:
        # Cleanup

        del os.environ["LAYERED_DEPLOYMENT_TARGET_CONDITION"]
    azure_cli = AzureCli(output, envvars)
    assert azure_cli.invoke_az_cli_outproc(["iot", "edge", "deployment", "delete", "-d", deployment_name, "-l", envvars.get_envvar("IOTHUB_CONNECTION_STRING")])


def test_deployment_with_target_group_set_from_dotenv():
    try:
        # Arrange
        deployment_name = f'test-layered{uuid.uuid4()}'
        os.chdir(test_solution_shared_lib_dir)
        envvars.set_envvar("LAYERED_DEPLOYMENT_TARGET_CONDITION", "tags.environment='dev'")

        # Act
        result = runner_invoke(['build', '--push', '-f', "layered_deployment.flattened_props.template.json", '-P', get_platform_type()])
        result = runner_invoke(['deployment',
                                '-f', 'config/layered_deployment.flattened_props.json',
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


def test_deployment_error_from_az_cli_bubbled_up():
    # Arrange
    os.chdir(test_solution_shared_lib_dir)

    # Act
    result = runner_invoke(['build', '--push', '-f', "layered_deployment.flattened_props.template.json", '-P', get_platform_type()])
    result = runner_invoke(['deployment',
                            '-f', 'config/layered_deployment.flattened_props.json',
                            '-n', "test-layered-deployment",
                            '-p', '10',
                            '-t', "invalid_target_group"
                            ])

    # Assert
    assert "ERROR: {'Message': 'ErrorCode:ArgumentInvalid;BadRequest'," in result.output


def test_deployment_error_missing_name():
    with pytest.raises(Exception) as context:
        # Act
        runner_invoke(['deployment', '-n', "test"])

    # Assert
    assert "Error: Missing option '--priority' / '-p'." in str(context)


def test_deployment_error_missing_priority():
    with pytest.raises(Exception) as context:
        # Act
        runner_invoke(['deployment', '-n', "test"])

    # Assert
    assert "Error: Missing option '--priority' / '-p'." in str(context)


def test_deployment_error_missing_target_condition():

    with pytest.raises(Exception) as context:
        # Act
        runner_invoke(['deployment', '-n', "test", '-p', '10'])

    # Assert
    assert "ERROR: Environment Variable LAYERED_DEPLOYMENT_TARGET_CONDITION not set. Either add to .env file or to your system's Environment Variables" in str(context.value)
