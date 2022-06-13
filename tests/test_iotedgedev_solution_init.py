import os
import shutil
import uuid
from unittest import mock
from .utility import (runner_invoke)


def test_solution_init_without_name():
    result = runner_invoke(['solution', 'init'], True)

    assert "Directory is not empty" in result.output


def test_solution_init_with_invalid_name_non_empty_dir():
    dirname = f'test-{uuid.uuid4()}'
    os.makedirs(f'{dirname}/empty_dir')

    result = runner_invoke(['solution', 'init', dirname], True)

    assert "Directory is not empty" in result.output
    shutil.rmtree(dirname, ignore_errors=True)


def test_solution_init_with_valid_name():
    dirname = f'test-{uuid.uuid4()}'

    # Mock calls to additional commands, to avoid triggering user prompts
    with mock.patch('iotedgedev.utility.Utility.call_proc') as mock_call_proc:
        result = runner_invoke(['solution', 'init', dirname], True)

    assert 'AZURE IOT EDGE SOLUTION CREATED' in result.output
    mock_call_proc.assert_called_with(["iotedgedev", "iothub", "setup", "--update-dotenv"])
    assert mock_call_proc.call_count == 2
    shutil.rmtree(dirname, ignore_errors=True)
