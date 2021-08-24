import os
from unittest import mock

import pytest
from iotedgedev.envvars import EnvVars
from iotedgedev.output import Output

pytestmark = pytest.mark.unit


def test_get_envvar__valid():
    envvars = EnvVars(Output())
    deployment_template = envvars.get_envvar("DEPLOYMENT_CONFIG_TEMPLATE_FILE")
    assert deployment_template is not None


def test_get_envvar__invalid():
    envvars = EnvVars(Output())
    testerval = envvars.get_envvar("TESTER")
    assert not testerval


def test_load_valid():
    envvars = EnvVars(Output())
    envvars.load()
    assert envvars.DEPLOYMENT_CONFIG_TEMPLATE_FILE == "deployment.template.json"


def test_verify_envvar_has_val__valid():
    envvars = EnvVars(Output())
    envvars.load()
    result = envvars.verify_envvar_has_val("DEPLOYMENT_CONFIG_TEMPLATE_FILE", envvars.DEPLOYMENT_CONFIG_TEMPLATE_FILE)
    assert not result


def test_get_envvar_key_if_val__valid():
    envvars = EnvVars(Output())
    assert envvars.get_envvar_key_if_val("DEPLOYMENT_CONFIG_TEMPLATE_FILE")


def test_get_envvar_key_if_val__invalid():
    envvars = EnvVars(Output())
    assert not envvars.get_envvar_key_if_val("TESTER")


def test_set_envvar():
    envvars = EnvVars(Output())
    registry_server = envvars.get_envvar("DEPLOYMENT_CONFIG_TEMPLATE_FILE")
    envvars.set_envvar("DEPLOYMENT_CONFIG_TEMPLATE_FILE", "deployment.template_new.json")
    new_registry_server = envvars.get_envvar("DEPLOYMENT_CONFIG_TEMPLATE_FILE")
    assert new_registry_server == "deployment.template_new.json"
    envvars.set_envvar("DEPLOYMENT_CONFIG_TEMPLATE_FILE", registry_server)


def test_envvar_clean():
    EnvVars(Output())
    envvar_clean_name = u"IOTEDGEDEV_ENVVAR_CLEAN_TEST"
    os.environ[envvar_clean_name] = u"test unicode string"


@pytest.mark.parametrize(
    "command, command_list",
    [
        ("solution new test_solution", ["init", "e2e", "solution new", "new", "simulator stop"]),
        ("solution new", ["init", "e2e", "solution new", "new", "simulator stop"]),
        ("", ["init", "e2e", "", "new", "simulator stop"]),
    ]
)
def test_in_command_list_true(command, command_list):
    envvars = EnvVars(Output())
    assert envvars.in_command_list(command, command_list)


@pytest.mark.parametrize(
    "command, command_list",
    [
        ("solution add filtermodule", ["init", "e2e", "solution new", "new", "simulator stop"]),
        ("solution addotherstuff filtermodule", ["init", "e2e", "solution add", "new", "simulator stop"]),
        ("", ["init", "e2e", "solution new", "new", "simulator stop"]),
        ("solution new test_solution", ["init", "e2e", "", "new", "simulator stop"])
    ]
)
def test_in_command_list_false(command, command_list):
    envvars = EnvVars(Output())
    assert not envvars.in_command_list(command, command_list)


@pytest.mark.parametrize(
    "command",
    [
        "iothub setup --update-dotenv",
        ""
    ]
)
def test_is_terse_command_true(command):
    envvars = EnvVars(Output())
    assert envvars.is_terse_command(command)


def test_is_terse_command_false():
    envvars = EnvVars(Output())
    assert not envvars.is_terse_command("solution add")


def test_default_container_registry_server_key_exists():
    envvars = EnvVars(Output())
    envvars.load()
    assert "CONTAINER_REGISTRY_SERVER" in os.environ


@pytest.mark.parametrize(
    "envvar",
    [
        "CONTAINER_REGISTRY_SERVER",
        "CONTAINER_REGISTRY_USERNAME",
        "CONTAINER_REGISTRY_PASSWORD"

    ]
)
def test_default_envvar_value_exists(envvar):
    envvars = EnvVars(Output())
    server = envvars.get_envvar(envvar)
    assert server is not None


def test_container_registry_server_key_missing_sys_exit():
    envvars = EnvVars(Output())
    with pytest.raises(ValueError):
        envvars.get_envvar("CONTAINER_REGISTRY_SERVER_UNITTEST", required=True)


@pytest.mark.parametrize(
    "envvar",
    [
        "CONTAINER_REGISTRY_SERVER",
        "CONTAINER_REGISTRY_USERNAME",
        "CONTAINER_REGISTRY_PASSWORD"

    ]
)
def test_unique_envvar_tokens(envvar):
    unique = set()
    envvar_lenght = len(envvar)
    is_unique = True
    envvars = EnvVars(Output())
    envvars.load()
    for key in os.environ:
        if key.startswith(envvar):
            token = key[envvar_lenght:]
            if token not in unique:
                unique.add(token)
            else:
                is_unique = False
    assert is_unique


@mock.patch.dict(os.environ, {
    "CONTAINER_REGISTRY_SERVER_UNITTEST": "unittest.azurecr.io",
    "CONTAINER_REGISTRY_USERNAME_UNITTEST": "username",
    "CONTAINER_REGISTRY_PASSWORD_UNITTEST": "password"
})
def test_additional_container_registry_map_is_set_from_environ():
    envvars = EnvVars(Output())
    envvars.load()
    assert len(envvars.CONTAINER_REGISTRY_MAP) == 2
    assert 'UNITTEST' in envvars.CONTAINER_REGISTRY_MAP.keys()
    assert envvars.CONTAINER_REGISTRY_MAP['UNITTEST'].server == 'unittest.azurecr.io'
    assert envvars.CONTAINER_REGISTRY_MAP['UNITTEST'].username == 'username'
    assert envvars.CONTAINER_REGISTRY_MAP['UNITTEST'].password == 'password'
