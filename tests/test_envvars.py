import os
import sys
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
    envvar_clean_name = u'IOTEDGEDEV_ENVVAR_CLEAN_TEST'
    os.environ[envvar_clean_name] = u'test unicode string'

    envvars.clean()

    if not (sys.version_info > (3, 0)):
        assert isinstance(os.environ[envvar_clean_name], str)
