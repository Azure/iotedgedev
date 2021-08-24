import os
import uuid
from unittest import mock

import pytest
from iotedgedev.azurecli import AzureCli
from iotedgedev.envvars import EnvVars
from iotedgedev.output import Output

from .utility import get_platform_type, runner_invoke

pytestmark = pytest.mark.e2e

output = Output()
envvars = EnvVars(output)
test_solution_shared_lib_dir = os.path.join(os.getcwd(), "tests", "assets", "test_solution_shared_lib")


@pytest.mark.parametrize(
    "config",
    [
        "layered_deployment.flattened_props.template.json",
        "layered_deployment.no_modules.template.json",
        "deployment.template.json"
    ]
)
# Test that cmd line target condition (-t) overrides target condition from .env
@mock.patch.dict(os.environ, {"IOTHUB_DEPLOYMENT_TARGET_CONDITION": "invalid_target"})
def test_iothub_deploy(config):
    # Arrange
    deployment_name = f'test-{uuid.uuid4()}'
    os.chdir(test_solution_shared_lib_dir)

    # Act
    result = runner_invoke(['build', '--push', '-f', config, '-P', get_platform_type()])
    result = runner_invoke(['iothub', 'deploy',
                            '-f', f'config/{config.replace("template.", "")}',
                            '-n', deployment_name,
                            '-p', '10',
                            '-t', "tags.environment='dev'"
                            ])

    # Assert
    assert 'DEPLOYMENT COMPLETE' in result.output
    assert 'ERROR' not in result.output

    azure_cli = AzureCli(output, envvars)
    assert azure_cli.invoke_az_cli_outproc(["iot", "edge", "deployment", "delete", "-d", deployment_name, "-l", envvars.get_envvar("IOTHUB_CONNECTION_STRING")])


@mock.patch.dict(os.environ, {"IOTHUB_DEPLOYMENT_TARGET_CONDITION": "tags.environment='dev'"})
def test_iothub_deploy_with_target_group_set_from_dotenv():
    # Arrange
    deployment_name = f'test-layered{uuid.uuid4()}'
    os.chdir(test_solution_shared_lib_dir)

    # Act
    result = runner_invoke(['build', '--push', '-f', "layered_deployment.flattened_props.template.json", '-P', get_platform_type()])
    result = runner_invoke(['iothub', 'deploy',
                            '-f', 'config/layered_deployment.flattened_props.json',
                            '-n', deployment_name,
                            '-p', '10',
                            ])

    # Assert
    assert 'DEPLOYMENT COMPLETE' in result.output
    assert 'ERROR' not in result.output

    azure_cli = AzureCli(output, envvars)

    assert azure_cli.invoke_az_cli_outproc(["iot", "edge", "deployment", "delete", "-d", deployment_name, "-l", envvars.get_envvar("IOTHUB_CONNECTION_STRING")])


def test_iothub_deploy_error_from_az_cli_bubbled_up():
    # Arrange
    os.chdir(test_solution_shared_lib_dir)

    # Act
    result = runner_invoke(['build', '--push', '-f', "layered_deployment.flattened_props.template.json", '-P', get_platform_type()])
    result = runner_invoke(['iothub', 'deploy',
                            '-f', 'config/layered_deployment.flattened_props.json',
                            '-n', "test-layered-deployment",
                            '-p', '10',
                            '-t', "invalid_target_group"
                            ])

    # Assert
    assert "ERROR: {'Message': 'ErrorCode:ArgumentInvalid;BadRequest'," in result.output


def test_iothub_deploy_error_missing_name():
    # Act
    with pytest.raises(Exception) as context:
        runner_invoke(['iothub', 'deploy', '-n', "test"])

    # Assert
    assert "Error: Missing option '--priority' / '-p'." in str(context)


def test_iothub_deploy_error_missing_priority():
    # Act
    with pytest.raises(Exception) as context:
        runner_invoke(['iothub', 'deploy', '-n', "test"])

    # Assert
    assert "Error: Missing option '--priority' / '-p'." in str(context)


def test_iothub_deploy_error_missing_target_condition():
    # Act
    with pytest.raises(Exception) as context:
        runner_invoke(['iothub', 'deploy', '-n', "test", '-p', '10'])

    # Assert
    assert "ERROR: Environment Variable IOTHUB_DEPLOYMENT_TARGET_CONDITION not set. Either add to .env file or to your system's Environment Variables" in str(context.value)
