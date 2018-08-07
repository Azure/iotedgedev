import os
import sys
from iotedgedev.compat import PY2
import pytest

from iotedgedev.envvars import EnvVars
from iotedgedev.output import Output

pytestmark = pytest.mark.unit


def test_valid_get_envvar():
    output = Output()
    envvars = EnvVars(output)
    loglevel = envvars.get_envvar("RUNTIME_LOG_LEVEL")
    assert loglevel == "info" or "debug"


def test_invalid_get_envvar():
    output = Output()
    envvars = EnvVars(output)
    testerval = envvars.get_envvar("TESTER")
    assert not testerval


def test_valid_load():
    output = Output()
    envvars = EnvVars(output)
    envvars.load()
    assert envvars.RUNTIME_LOG_LEVEL == "info" or "debug"


def test_valid_verify_envvar_has_val():
    output = Output()
    envvars = EnvVars(output)
    envvars.load()
    result = envvars.verify_envvar_has_val("RUNTIME_LOG_LEVEL", envvars.RUNTIME_LOG_LEVEL)
    assert not result


def test_valid_get_envvar_key_if_val():
    output = Output()
    envvars = EnvVars(output)
    assert envvars.get_envvar_key_if_val("RUNTIME_LOG_LEVEL")


def test_invalid_get_envvar_key_if_val():
    output = Output()
    envvars = EnvVars(output)
    assert not envvars.get_envvar_key_if_val("TESTER")


def test_set_envvar():
    output = Output()
    envvars = EnvVars(output)
    loglevel = envvars.get_envvar("RUNTIME_LOG_LEVEL")
    envvars.set_envvar("RUNTIME_LOG_LEVEL", "debug")
    setlevel = envvars.get_envvar("RUNTIME_LOG_LEVEL")
    assert setlevel == "debug"
    envvars.set_envvar("RUNTIME_LOG_LEVEL", loglevel)


def test_envvar_clean():
    output = Output()
    envvars = EnvVars(output)
    envvar_clean_name = u"IOTEDGEDEV_ENVVAR_CLEAN_TEST"
    os.environ[envvar_clean_name] = u"test unicode string"

    envvars.clean()

    if PY2:
        assert isinstance(os.environ[envvar_clean_name], str)


def test_in_command_list_true_1():
    output = Output()
    envvars = EnvVars(output)
    assert envvars.in_command_list("solution create test_solution", ["init", "e2e", "solution create", "create", "simulator stop"])


def test_in_command_list_true_2():
    output = Output()
    envvars = EnvVars(output)
    assert envvars.in_command_list("solution create", ["init", "e2e", "solution create", "create", "simulator stop"])


def test_in_command_list_false_1():
    output = Output()
    envvars = EnvVars(output)
    assert not envvars.in_command_list("solution add filtermodule", ["init", "e2e", "solution create", "create", "simulator stop"])


def test_in_command_list_false_2():
    output = Output()
    envvars = EnvVars(output)
    assert not envvars.in_command_list("solution addotherstuff filtermodule", ["init", "e2e", "solution add", "create", "simulator stop"])


def test_in_command_list_empty_1():
    output = Output()
    envvars = EnvVars(output)
    assert not envvars.in_command_list("", ["init", "e2e", "solution create", "create", "simulator stop"])


def test_in_command_list_empty_2():
    output = Output()
    envvars = EnvVars(output)
    assert not envvars.in_command_list("solution create test_solution", ["init", "e2e", "", "create", "simulator stop"])


def test_in_command_list_empty_3():
    output = Output()
    envvars = EnvVars(output)
    assert envvars.in_command_list("", ["init", "e2e", "", "create", "simulator stop"])


def test_is_bypass_command_true():
    output = Output()
    envvars = EnvVars(output)
    assert envvars.is_bypass_command("solution create EdgeSolution")


def test_is_bypass_command_false():
    output = Output()
    envvars = EnvVars(output)
    assert not envvars.is_bypass_command("solution add")


def test_is_bypass_command_empty():
    output = Output()
    envvars = EnvVars(output)
    assert not envvars.is_bypass_command("")


def test_is_terse_command_true():
    output = Output()
    envvars = EnvVars(output)
    assert envvars.is_terse_command("iothub setup --update-dotenv")


def test_is_terse_command_false():
    output = Output()
    envvars = EnvVars(output)
    assert not envvars.is_terse_command("solution create")


def test_is_terse_command_empty():
    output = Output()
    envvars = EnvVars(output)
    assert envvars.is_terse_command("")
