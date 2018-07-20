import os

import pytest

from iotedgedev.envvars import EnvVars
from iotedgedev.output import Output
from iotedgedev.utility import Utility
from utility import assert_json_file_equal

pytestmark = pytest.mark.unit

tests_dir = os.path.join(os.getcwd(), "tests")
test_assets_dir = os.path.join(tests_dir, "assets")
test_file_1 = os.path.join(test_assets_dir, "deployment.template_1.json")
test_file_2 = os.path.join(test_assets_dir, "deployment.template_2.json")


@pytest.fixture
def utility():
    output = Output()
    envvars = EnvVars(output)
    envvars.load()
    return Utility(envvars, output)


def test_copy_template(utility, tmpdir):
    replacements = {
        "${MODULES.csharpmodule.amd64}": "localhost:5000/csharpmodule:0.0.1-amd64",
        "${MODULES.csharpfunction.amd64.debug}": "localhost:5000/csharpfunction:0.0.1-amd64.debug"
    }
    dest = tmpdir.join("deployment_template_1.dest.json").strpath
    utility.copy_template(test_file_1, dest, replacements=replacements, expandvars=False)
    assert_json_file_equal(test_file_2, dest)


def test_copy_template_expandvars(utility, tmpdir):
    replacements = {
        "${MODULES.csharpmodule.amd64}": "${CONTAINER_REGISTRY_SERVER}/csharpmodule:0.0.1-amd64",
        "${MODULES.csharpfunction.amd64.debug}": "${CONTAINER_REGISTRY_SERVER}/csharpfunction:0.0.1-amd64.debug"
    }
    os.environ["CONTAINER_REGISTRY_SERVER"] = "localhost:5000"
    dest = tmpdir.join("deployment_template_2.dest.json").strpath
    utility.copy_template(test_file_1, dest, replacements=replacements, expandvars=True)
    assert_json_file_equal(test_file_2, dest)
