import json
import os

import pytest

from iotedgedev.deploymentmanifest import DeploymentManifest
from iotedgedev.envvars import EnvVars
from iotedgedev.output import Output
from iotedgedev.utility import Utility

pytestmark = pytest.mark.unit

tests_dir = os.path.join(os.getcwd(), "tests")
test_assets_dir = os.path.join(tests_dir, "assets")
test_file_1 = os.path.join(test_assets_dir, "deployment.template_1.json")
test_file_2 = os.path.join(test_assets_dir, "deployment.template_2.json")
test_file_3 = os.path.join(test_assets_dir, "deployment.template_3.json")


@pytest.fixture
def deployment_manifest():
    output = Output()
    envvars = EnvVars(output)
    envvars.load()
    utility = Utility(envvars, output)

    def _deployment_manifest(path):
        return DeploymentManifest(envvars, output, utility, path, True)

    return _deployment_manifest


def test_get_modules_to_process(deployment_manifest):
    deployment_manifest = deployment_manifest(test_file_1)
    modules_to_process = deployment_manifest.get_modules_to_process()
    assert modules_to_process == [("csharpmodule", "amd64"), ("csharpfunction", "amd64.debug")]


def test_get_modules_to_process_empty(deployment_manifest):
    deployment_manifest = deployment_manifest(test_file_2)
    modules_to_process = deployment_manifest.get_modules_to_process()
    assert modules_to_process == []


def test_add_module_template(deployment_manifest):
    deployment_manifest = deployment_manifest(test_file_1)
    deployment_manifest.add_module_template("csharpmodule2")
    with open(test_file_3, "r") as expected:
        assert deployment_manifest.json == json.load(expected)
