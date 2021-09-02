import os
import uuid
from unittest import mock

import pytest
from iotedgedev.azurecli import AzureCli
from iotedgedev.envvars import EnvVars
from iotedgedev.output import Output
from iotedgedev.connectionstring import DeviceConnectionString

from .utility import get_platform_type, runner_invoke

pytestmark = pytest.mark.e2e

output = Output()
envvars = EnvVars(output)
test_solution_shared_lib_dir = os.path.join(os.getcwd(), "tests", "assets", "test_solution_shared_lib")


@pytest.mark.parametrize(
    "config, manifest",
    [
        ("layered_deployment.flattened_props.template.json", "layered_deployment.flattened_props.json"),
        ("layered_deployment.no_modules.template.json", "layered_deployment.no_modules.json"),
        ("deployment.template.json", f"deployment.{get_platform_type()}.json")
    ]
)
# Test that cmd line target condition (-t) overrides target condition from .env
@ mock.patch.dict(os.environ, {"IOTHUB_DEPLOYMENT_TARGET_CONDITION": "invalid_target"})
def test_iothub_deploy(config, manifest):
    # Arrange
    deployment_name = f'test-{uuid.uuid4()}'
    os.chdir(test_solution_shared_lib_dir)

    # Act
    result = runner_invoke(['build', '-f', config, '-P', get_platform_type()])
    result = runner_invoke(['iothub', 'deploy',
                            '-f', f'config/{manifest}',
                           '-n', deployment_name,
                            '-p', '10',
                            '-t', "tags.environment='dev'"
                            ])

    # Assert
    assert 'DEPLOYMENT COMPLETE' in result.output
    assert 'ERROR' not in result.output

    azure_cli = AzureCli(output, envvars)
    assert azure_cli.invoke_az_cli_outproc(["iot", "edge", "deployment", "delete", "-d", deployment_name, "-l", envvars.get_envvar("IOTHUB_CONNECTION_STRING")])


@ mock.patch.dict(os.environ, {"IOTHUB_DEPLOYMENT_TARGET_CONDITION": "tags.environment='dev'"})
def test_iothub_deploy_with_target_group_set_from_dotenv():
    # Arrange
    deployment_name = f'test-layered{uuid.uuid4()}'
    os.chdir(test_solution_shared_lib_dir)

    # Act
    result = runner_invoke(['build', '-f', "layered_deployment.flattened_props.template.json", '-P', get_platform_type()])
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
    result = runner_invoke(['build', '-f', "layered_deployment.flattened_props.template.json", '-P', get_platform_type()])
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


def test_iothub_deploy_and_add_tags():
    # Arrange
    tags = '{"environment":"dev","building":"9"}'
    deployment_name = f'test-{uuid.uuid4()}'
    os.chdir(test_solution_shared_lib_dir)

    # Act
    result = runner_invoke(['build', '-f', "layered_deployment.flattened_props.template.json", '-P', get_platform_type()])
    result = runner_invoke(['iothub', 'deploy',
                            '-f', 'config/layered_deployment.flattened_props.json',
                           '-n', deployment_name,
                            '-p', '10',
                            '-t', "tags.environment='dev'",
                            '-dt', tags
                            ])

    # Assert
    assert 'DEPLOYMENT COMPLETE' in result.output
    assert 'TAG UPDATE COMPLETE' in result.output
    assert tags in result.output
    assert 'ERROR' not in result.output

    azure_cli = AzureCli(output, envvars)

    assert azure_cli.invoke_az_cli_outproc(["iot", "edge", "deployment", "delete", "-d", deployment_name, "-l", envvars.get_envvar("IOTHUB_CONNECTION_STRING")])
    assert azure_cli.invoke_az_cli_outproc(["iot", "hub", "device-twin", "replace", "-d", DeviceConnectionString(envvars.get_envvar("DEVICE_CONNECTION_STRING")).device_id,
                                            "-l", envvars.get_envvar("IOTHUB_CONNECTION_STRING"), "--json", "tag_overwrite.json"])


def test_iothub_deploy_and_add_tags_retry_after_invalid_tag():
    # Arrange
    tags1 = 'invalid_tag'
    tags2 = '{"environment":"dev","building":"9"}'
    deployment_name = f'test-{uuid.uuid4()}'
    os.chdir(test_solution_shared_lib_dir)

    # Act
    result = runner_invoke(['build', '-f', "layered_deployment.flattened_props.template.json", '-P', get_platform_type()])
    result = runner_invoke(['iothub', 'deploy',
                            '-f', 'config/layered_deployment.flattened_props.json',
                           '-n', deployment_name,
                            '-p', '10',
                            '-t', "tags.environment='dev'",
                            '-dt', tags1
                            ])

    result_retry = runner_invoke(['iothub', 'deploy',
                                  '-f', 'config/layered_deployment.flattened_props.json',
                                  '-n', deployment_name,
                                  '-p', '10',
                                  '-t', "tags.environment='dev'",
                                  '-dt', tags2
                                  ])

    # Assert
    assert 'DEPLOYMENT COMPLETE' in result.output
    assert 'TAG UPDATE COMPLETE' not in result.output
    assert f"ERROR: Failed to add tag: '{tags1}' to device" in result.output

    assert 'DEPLOYMENT COMPLETE' not in result_retry.output
    assert 'TAG UPDATE COMPLETE' in result_retry.output
    assert tags2 in result_retry.output
    assert 'ERROR: Failed to deploy' in result_retry.output
    assert f'Message\': "ErrorCode:ConfigurationAlreadyExists;Configuration with id \'{deployment_name}\' already exist on IotHub.' in result_retry.output

    azure_cli = AzureCli(output, envvars)

    assert azure_cli.invoke_az_cli_outproc(["iot", "edge", "deployment", "delete", "-d", deployment_name, "-l", envvars.get_envvar("IOTHUB_CONNECTION_STRING")])
    assert azure_cli.invoke_az_cli_outproc(["iot", "hub", "device-twin", "replace", "-d", DeviceConnectionString(envvars.get_envvar("DEVICE_CONNECTION_STRING")).device_id,
                                            "-l", envvars.get_envvar("IOTHUB_CONNECTION_STRING"), "--json", "tag_overwrite.json"])
