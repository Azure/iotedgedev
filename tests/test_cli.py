from iotedgedev.cli import main
from .utility import get_cli_command_structure
import pytest

pytestmark = pytest.mark.unit


def test_cli_structure():
    # Arrange
    expected_structure = {
        "solution": {
            "new": None,
            "init": None,
            "e2e": None,
            "add": None,
            "build": None,
            "push": None,
            "deploy": None,
            "tag": None,
            "genconfig": None
        },
        "simulator": {
            "setup": None,
            "start": None,
            "stop": None,
            "modulecred": None
        },
        "iothub": {
            "deploy": None,
            "monitor": None,
            "setup": None
        },
        "docker": {
            "setup": None,
            "clean": None,
            "log": None
        },
        "new": None,
        "init": None,
        "add": None,
        "build": None,
        "push": None,
        "deploy": None,
        "tag": None,
        "genconfig": None,
        "setup": None,
        "start": None,
        "stop": None,
        "monitor": None,
        "log": None
    }
    # Act
    structure = get_cli_command_structure(main)

    # Assert
    assert structure == expected_structure
