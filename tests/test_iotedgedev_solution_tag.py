import os
import pytest
from .utility import (
    runner_invoke,
)
from iotedgedev.azurecli import AzureCli
from iotedgedev.envvars import EnvVars
from iotedgedev.output import Output
from iotedgedev.connectionstring import DeviceConnectionString
from unittest import mock

pytestmark = pytest.mark.e2e

output = Output()
envvars = EnvVars(output)
test_solution_shared_lib_dir = os.path.join(os.getcwd(), "tests", "assets", "test_solution_shared_lib")


# Test that cmd line tags (--tags) overrides DEVICE_TAGS from .env
@ mock.patch.dict(os.environ, {"DEVICE_TAGS": "invalid_target"})
def test_add_tags():
    # Arrange
    os.chdir(test_solution_shared_lib_dir)

    # Act
    result = runner_invoke(['solution', 'tag', '--tags', '{"environment":"dev","building":"9"}'])

    # Assert
    assert 'TAG UPDATE COMPLETE' in result.output
    assert '{"environment":"dev","building":"9"}' in result.output
    assert 'ERROR' not in result.output

    azure_cli = AzureCli(output, envvars)

    assert azure_cli.invoke_az_cli_outproc(["iot", "hub", "device-twin", "replace", "-d", DeviceConnectionString(envvars.get_envvar("DEVICE_CONNECTION_STRING")).device_id,
                                            "-l", envvars.get_envvar("IOTHUB_CONNECTION_STRING"), "--json", "tag_overwrite.json"])


@pytest.mark.parametrize(
    "tags",
    [
        "tags.environment='dev'",
        "dev"
    ]
)
def test_add_invalid_tag(tags):
    # Arrange
    os.chdir(test_solution_shared_lib_dir)

    # Act
    result = runner_invoke(['solution', 'tag', '--tags', tags])

    # Assert
    assert f"ERROR: Failed to add tag: '{tags}' to device" in result.output


def test_error_missing_tag():
    # Arrange
    os.chdir(test_solution_shared_lib_dir)

    # Act
    with pytest.raises(Exception) as context:
        runner_invoke(['solution', 'tag', '--tags'])

    # Assert
    assert "Error: Option '--tags' requires an argument." in str(context)


@ mock.patch.dict(os.environ, {"DEVICE_TAGS": '{"environment":"dev","building":"9"}'})
def test_default_tag_from_env():
    # Arrange
    os.chdir(test_solution_shared_lib_dir)

    # Act
    result = runner_invoke(['solution', 'tag'])

    # Assert
    assert 'TAG UPDATE COMPLETE' in result.output
    assert '{"environment":"dev","building":"9"}' in result.output
    assert 'ERROR' not in result.output

    azure_cli = AzureCli(output, envvars)

    assert azure_cli.invoke_az_cli_outproc(["iot", "hub", "device-twin", "replace", "-d", DeviceConnectionString(envvars.get_envvar("DEVICE_CONNECTION_STRING")).device_id,
                                            "-l", envvars.get_envvar("IOTHUB_CONNECTION_STRING"), "--json", "tag_overwrite.json"])


def test_missing_default_tag_from_env():
    # Arrange
    os.chdir(test_solution_shared_lib_dir)

    # Act
    with pytest.raises(Exception) as context:
        runner_invoke(['solution', 'tag'])

    # Assert
    assert "ERROR: Environment Variable DEVICE_TAGS not set. Either add to .env file or to your system's Environment Variables" in str(context)
