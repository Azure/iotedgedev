import os
import pytest
import uuid
from .utility import (
    get_platform_type,
    runner_invoke,
)
from iotedgedev.envvars import EnvVars
from iotedgedev.output import Output

pytestmark = pytest.mark.e2e

output = Output()
envvars = EnvVars(output)
test_solution_shared_lib_dir = os.path.join(os.getcwd(), "tests", "assets", "test_solution_shared_lib")


def test_add_tags():
    # Arrange
    os.chdir(test_solution_shared_lib_dir)

    # Act
    result = runner_invoke(['tag', '--tags', '{"environment":"dev","building":"9"}'])

    # Assert
    assert 'TAG UPDATE COMPLETE' in result.output
    assert '{"environment":"dev","building":"9"}' in result.output
    assert 'ERROR' not in result.output


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
    result = runner_invoke(['tag', '--tags', tags])

    # Assert
    assert f"ERROR: Failed to add tag: '{tags}' to device" in result.output


def test_error_missing_tag():
    # Arrange
    os.chdir(test_solution_shared_lib_dir)

    # Act
    with pytest.raises(Exception) as context:
        runner_invoke(['tag', '--tags'])

    # Assert
    assert "Error: Option '--tags' requires an argument." in str(context)
