import os

import pytest

from iotedgedev.envvars import EnvVars
from iotedgedev.output import Output
from iotedgedev.utility import Utility

from .utility import assert_list_equal, assert_file_equal, assert_json_file_equal

pytestmark = pytest.mark.unit

tests_dir = os.path.join(os.getcwd(), "tests")
test_assets_dir = os.path.join(tests_dir, "assets")
test_file_1 = os.path.join(test_assets_dir, "deployment.template_1.json")
test_file_2 = os.path.join(test_assets_dir, "deployment.template_2.json")
test_file_4 = os.path.join(test_assets_dir, "deployment.template_4.json")


@pytest.fixture
def utility():
    output = Output()
    envvars = EnvVars(output)
    envvars.load()
    return Utility(envvars, output)


def test_ensure_dir(request, utility):
    before_ensure = os.listdir(tests_dir)
    utility.ensure_dir(test_assets_dir)
    after_ensure = os.listdir(tests_dir)
    assert_list_equal(before_ensure, after_ensure)

    new_dir = "new_dir"
    utility.ensure_dir(new_dir)
    assert os.path.exists(new_dir)

    def clean():
        if os.path.exists(new_dir):
            os.rmdir(new_dir)
    request.addfinalizer(clean)


def test_copy_from_template_dir(utility, tmpdir):
    src_file = "deployment.template.json"
    dest_dir = tmpdir.strpath
    dest_file = tmpdir.join(src_file).strpath
    utility.copy_from_template_dir(src_file, dest_dir, replacements={"%MODULE%": "filtermodule"})
    assert_file_equal(dest_file, test_file_4)


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


def test_in_asterisk_list(utility):
    assert utility.in_asterisk_list("filtermodule", "pipemodule, filtermodule")


def test_in_asterisk_list_empty(utility):
    assert not utility.in_asterisk_list("filtermodule", "")


def test_in_asterisk_list_asterisk(utility):
    assert utility.in_asterisk_list("filtermodule", "*")


def test_del_key(utility):
    dict_ = {
        "1": 0,
        "2": {
            "3": 0,
            "4": "foo",
            "5": {
                "6": 0
            }
        }
    }

    assert utility.del_key("not a dict", ["1", "2"]) is None
    assert utility.del_key(dict_, ["2", "5"]) == {"6": 0}
    assert utility.del_key(dict_, ["1", "non_existent_key"]) is None
    assert utility.del_key(dict_, ["2", "non_existent_key"]) is None

    expected = {
        "1": 0,
        "2": {
            "3": 0,
            "4": "foo"
        }
    }

    assert dict_ == expected


def test_get_sha256_hash():
    assert Utility.get_sha256_hash("foo") == "2c26b46b68ffc68ff99b453c1d30413413422d706483bfa0f98a5e886266e7ae"


def test_get_deployment_manifest_name():
    assert Utility.get_deployment_manifest_name("config/deployment.template.json", "0.0.1", "amd64") == "deployment.json"
    assert Utility.get_deployment_manifest_name("deployment.template.json", "0.0.1", "amd64") == "deployment.json"
    assert Utility.get_deployment_manifest_name("deployment.debug.template.json", "0.0.1", "amd64") == "deployment.debug.json"
    assert Utility.get_deployment_manifest_name("config/deployment.template.json", "1.0.0", "amd64") == "deployment.amd64.json"
    assert Utility.get_deployment_manifest_name("deployment.template.json", "1.0.0", "amd64") == "deployment.amd64.json"
    assert Utility.get_deployment_manifest_name("deployment.debug.template.json", "1.0.0", "amd64") == "deployment.debug.amd64.json"

    os.environ["DEPLOYMENT_CONFIG_FILE"] = "foo.json"
    assert Utility.get_deployment_manifest_name("deployment.debug.template.json", "1.0.0", "amd64") == "foo.json"
