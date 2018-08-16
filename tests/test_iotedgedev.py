import json
import os
import shutil

import pytest
from click.testing import CliRunner
from dotenv import load_dotenv

from iotedgedev.compat import PY35
from iotedgedev.connectionstring import (DeviceConnectionString,
                                         IoTHubConnectionString)

from iotedgedev.envvars import EnvVars
from iotedgedev.output import Output

pytestmark = pytest.mark.e2e

root_dir = os.getcwd()
tests_dir = os.path.join(root_dir, "tests")
envvars = EnvVars(Output())
env_file_name = envvars.get_dotenv_file()
env_file_path = envvars.get_dotenv_path(env_file_name)

test_solution = "test_solution"
test_solution_dir = os.path.join(tests_dir, test_solution)


@pytest.fixture(scope="module", autouse=True)
def create_solution(request):

    cli = __import__("iotedgedev.cli", fromlist=['main'])
    # print cli
    # out, err = capsys.readouterr()
    # print out

    runner = CliRunner()
    os.chdir(tests_dir)
    result = runner.invoke(cli.main, ['solution', 'create', test_solution])
    print(result.output)
    assert 'AZURE IOT EDGE SOLUTION CREATED' in result.output

    shutil.copyfile(env_file_path, os.path.join(test_solution_dir, env_file_name))

    os.chdir(test_solution_dir)

    def clean():
        os.chdir(root_dir)
        shutil.rmtree(test_solution_dir, ignore_errors=True)
    request.addfinalizer(clean)
    return


@pytest.fixture
def test_solution_create_in_non_empty_current_path(request):

    os.chdir(test_solution_dir)

    cli = __import__("iotedgedev.cli", fromlist=['main'])
    runner = CliRunner()
    result = runner.invoke(cli.main, ['solution', 'create', '.'])
    print(result.output)

    assert "Directory is not empty" in result.output


@pytest.fixture
def test_solution_create_in_empty_current_path(request):

    os.chdir(test_solution_dir)

    dirname = "emptydir_current"
    os.makedirs(dirname)
    os.chdir(os.path.join(test_solution_dir, dirname))

    cli = __import__("iotedgedev.cli", fromlist=['main'])
    runner = CliRunner()
    result = runner.invoke(cli.main, ['solution', 'create', '.'])
    print(result.output)

    assert 'AZURE IOT EDGE SOLUTION CREATED' in result.output


@pytest.fixture
def test_solution_create_in_non_empty_dir(request):

    os.chdir(tests_dir)

    cli = __import__("iotedgedev.cli", fromlist=['main'])
    runner = CliRunner()
    result = runner.invoke(cli.main, ['solution', 'create', test_solution])
    print(result.output)

    assert "Directory is not empty" in result.output


@pytest.fixture
def test_solution_create_in_empty_child_dir(request):

    os.chdir(test_solution_dir)

    dirname = "emptydir"
    os.makedirs(dirname)

    cli = __import__("iotedgedev.cli", fromlist=['main'])
    runner = CliRunner()
    result = runner.invoke(cli.main, ['solution', 'create', dirname])
    print(result.output)

    assert 'AZURE IOT EDGE SOLUTION CREATED' in result.output


def test_module_add():
    """Test the addmodule command"""
    os.chdir(test_solution_dir)
    cli = __import__("iotedgedev.cli", fromlist=['main'])
    runner = CliRunner()

    add_module_and_verify(cli.main, runner, "csharp")
    add_module_and_verify(cli.main, runner, "nodejs")
    add_module_and_verify(cli.main, runner, "python")
    add_module_and_verify(cli.main, runner, "csharpfunction")


def test_module_add_invalid_name():
    """Test the addmodule command with invalid module name"""
    os.chdir(test_solution_dir)
    cli = __import__("iotedgedev.cli", fromlist=["main"])
    runner = CliRunner()

    result = runner.invoke(cli.main, ["solution", "add", "_csharpmodule", "--template", "csharp"])
    print(result.output)
    assert "Module name cannot start or end with the symbol _" in result.output

    result = runner.invoke(cli.main, ["solution", "add", "csharpmodule_", "--template", "csharp"])
    print(result.output)
    assert "Module name cannot start or end with the symbol _" in result.output

    result = runner.invoke(cli.main, ["solution", "add", "csharp-module", "--template", "csharp"])
    print(result.output)
    assert "Module name can only contain alphanumeric characters and the symbol _" in result.output

    result = runner.invoke(cli.main, ["solution", "add", "filtermodule", "--template", "csharp"])
    print(result.output)
    assert "already exists under" in result.output


@pytest.fixture
def test_push_modules(request):

    os.chdir(test_solution_dir)

    cli = __import__("iotedgedev.cli", fromlist=['main'])
    runner = CliRunner()
    result = runner.invoke(cli.main, ['push'])
    print(result.output)

    assert 'BUILD COMPLETE' in result.output
    assert 'PUSH COMPLETE' in result.output


@pytest.fixture
def test_deploy_modules(request):

    os.chdir(test_solution_dir)

    cli = __import__("iotedgedev.cli", fromlist=['main'])
    runner = CliRunner()
    result = runner.invoke(cli.main, ['deploy'])
    print(result.output)

    assert 'DEPLOYMENT COMPLETE' in result.output


def test_monitor(request, capfd):

    os.chdir(test_solution_dir)

    cli = __import__("iotedgedev.cli", fromlist=['main'])
    runner = CliRunner()
    result = runner.invoke(cli.main, ['monitor', '--timeout', '5'])
    out, err = capfd.readouterr()
    print(out)
    print(err)
    print(result.output)

    if not PY35:
        assert 'Monitoring events from device' in out
    else:
        assert not err


def test_e2e(test_push_modules, test_deploy_modules):
    print('Testing E2E')


def test_valid_env_iothub_connectionstring():
    envvars.load_dotenv()

    env_iothub_connectionstring = os.getenv("IOTHUB_CONNECTION_STRING")
    connectionstring = IoTHubConnectionString(env_iothub_connectionstring)
    assert connectionstring.HostName
    assert connectionstring.HubName
    assert connectionstring.SharedAccessKey
    assert connectionstring.SharedAccessKeyName


def test_valid_env_device_connectionstring():
    envvars.load_dotenv()
    env_device_connectionstring = os.getenv("DEVICE_CONNECTION_STRING")
    connectionstring = DeviceConnectionString(env_device_connectionstring)
    assert connectionstring.HostName
    assert connectionstring.HubName
    assert connectionstring.SharedAccessKey
    assert connectionstring.DeviceId

def add_module_and_verify(main, runner, template):
    module_name = template + "module"
    result = runner.invoke(main, ["solution", "add", module_name, '--template', template])
    print(result.output)
    assert 'ADD COMPLETE' in result.output
    assert os.path.exists(os.path.join(os.environ["MODULES_PATH"], module_name))
    assert module_name in json.load(open(os.environ["DEPLOYMENT_CONFIG_TEMPLATE_FILE"]))["modulesContent"]["$edgeAgent"]["properties.desired"]["modules"]
