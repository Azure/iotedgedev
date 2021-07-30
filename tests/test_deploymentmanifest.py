import json
import os

import pytest

from iotedgedev.deploymentmanifest import DeploymentManifest
from iotedgedev.envvars import EnvVars
from iotedgedev.output import Output
from iotedgedev.utility import Utility

from .utility import assert_list_equal

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


def test_get_desired_property(deployment_manifest):
    deployment_manifest = deployment_manifest(test_file_1)
    props = deployment_manifest.get_desired_property("$edgeHub", "schemaVersion")
    assert props == "%EDGE_RUNTIME_VERSION"


def test_get_desired_property_nonexistent_module(deployment_manifest):
    deployment_manifest = deployment_manifest(test_file_1)
    with pytest.raises(KeyError):
        deployment_manifest.get_desired_property("nonexistentModule", "schemaVersion")


def test_get_desired_property_nonexistent_prop(deployment_manifest):
    deployment_manifest = deployment_manifest(test_file_1)
    with pytest.raises(KeyError):
        deployment_manifest.get_desired_property("$edgeHub", "nonexistentProp")


def test_get_user_modules(deployment_manifest):
    deployment_manifest = deployment_manifest(test_file_1)
    user_modules = list(deployment_manifest.get_user_modules().keys())
    assert_list_equal(user_modules, ["tempSensor", "csharpmodule", "csharpfunction"])


def test_get_system_modules(deployment_manifest):
    deployment_manifest = deployment_manifest(test_file_1)
    system_modules = list(deployment_manifest.get_system_modules().keys())
    assert_list_equal(system_modules, ["edgeAgent", "edgeHub"])


def test_get_all_modules(deployment_manifest):
    deployment_manifest = deployment_manifest(test_file_1)
    system_modules = list(deployment_manifest.get_all_modules().keys())
    assert_list_equal(system_modules, ["edgeAgent", "edgeHub", "tempSensor", "csharpmodule", "csharpfunction"])


def test_add_module_template(deployment_manifest):
    deployment_manifest = deployment_manifest(test_file_1)
    deployment_manifest.add_module_template("csharpmodule2")
    expected = json.loads(Utility.get_file_contents(test_file_3, expandvars=True))
    assert deployment_manifest.json == expected


def test_convert_create_options(deployment_manifest):
    deployment_manifest = deployment_manifest(test_file_1)

    temp_sensor_settings = deployment_manifest.json["modulesContent"]["$edgeAgent"]["properties.desired"]["modules"]["tempSensor"]["settings"]
    temp_sensor_create_options_copy = json.loads(json.dumps(temp_sensor_settings["createOptions"]))

    deployment_manifest.convert_create_options()
    assert deployment_manifest.json["modulesContent"]["$edgeAgent"]["properties.desired"]["systemModules"]["edgeAgent"]["settings"][
        "createOptions"] == ""
    assert json.loads(deployment_manifest.json["modulesContent"]["$edgeAgent"]["properties.desired"]["systemModules"]["edgeHub"]["settings"][
        "createOptions"]) == json.loads("{\"HostConfig\":{\"PortBindings\":{\"5671/tcp\":[{\"HostPort\":\"5671\"}],\"8883/tcp\":[{\"HostPort\":\"8883\"}],\"443/tcp\":[{\"HostPort\":\"443\"}]}}}")

    assert "createOptions" in temp_sensor_settings
    assert "createOptions01" in temp_sensor_settings
    assert "createOptions02" in temp_sensor_settings

    create_options_str = temp_sensor_settings["createOptions"] + temp_sensor_settings["createOptions01"] + temp_sensor_settings["createOptions02"]
    assert json.loads(create_options_str) == temp_sensor_create_options_copy


def test_expand_image_placeholders(deployment_manifest):
    deployment_manifest = deployment_manifest(test_file_1)
    deployment_manifest.expand_image_placeholders({"csharpmodule": "localhost:5000/csharpmodule:0.0.1-amd64"})
    assert deployment_manifest.json["modulesContent"]["$edgeAgent"]["properties.desired"]["modules"]["csharpmodule"]["settings"]["image"] == "localhost:5000/csharpmodule:0.0.1-amd64"


def test_get_image_placeholder():
    assert DeploymentManifest.get_image_placeholder("filtermodule") == "${MODULES.filtermodule}"
    assert DeploymentManifest.get_image_placeholder("filtermodule", True) == "${MODULES.filtermodule.debug}"
