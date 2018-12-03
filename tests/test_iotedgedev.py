import json
import os
import shutil
import platform

import pytest
from click.testing import CliRunner

from iotedgedev.compat import PY35
from iotedgedev.connectionstring import (DeviceConnectionString,
                                         IoTHubConnectionString)
from iotedgedev.envvars import EnvVars
from iotedgedev.output import Output

from .utility import assert_json_file_equal
from .utility import get_docker_client

pytestmark = pytest.mark.e2e

root_dir = os.getcwd()
tests_dir = os.path.join(root_dir, "tests")
output = Output()
envvars = EnvVars(output)
env_file_name = envvars.get_dotenv_file()
env_file_path = envvars.get_dotenv_path(env_file_name)

test_solution = "test_solution"
test_solution_dir = os.path.join(tests_dir, test_solution)
launch_json_file = os.path.join(tests_dir, "assets", "launch.json")
launch_json_file_without_nodejs = os.path.join(tests_dir, "assets", "launch_without_nodejs.json")

test_solution_shared_lib = "test_solution_shared_lib"
test_solution_shared_lib_dir = os.path.join(tests_dir, "assets", test_solution_shared_lib)


def get_docker_os_type():
    if get_docker_client().get_os_type().lower() == 'windows':
        platform_type = 'windows-amd64'
    else:
        platform_type = 'amd64'
    return platform_type


@pytest.fixture(scope="function", autouse=True)
def create_solution(request):
    def clean():
        os.chdir(root_dir)
        shutil.rmtree(test_solution_dir, ignore_errors=True)

    clean()

    cli = __import__("iotedgedev.cli", fromlist=['main'])
    # print cli
    # out, err = capsys.readouterr()
    # print out

    runner = CliRunner()
    os.chdir(tests_dir)

    result = runner.invoke(cli.main, ['solution', 'new', test_solution])
    print(result.output)
    assert 'AZURE IOT EDGE SOLUTION CREATED' in result.output

    shutil.copyfile(env_file_path, os.path.join(test_solution_dir, env_file_name))

    os.chdir(test_solution_dir)

    request.addfinalizer(clean)
    return


@pytest.fixture
def test_solution_create_in_non_empty_current_path(request):

    os.chdir(test_solution_dir)

    cli = __import__("iotedgedev.cli", fromlist=['main'])
    runner = CliRunner()
    result = runner.invoke(cli.main, ['solution', 'new', '.'])
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
    result = runner.invoke(cli.main, ['solution', 'new', '.'])
    print(result.output)

    assert 'AZURE IOT EDGE SOLUTION CREATED' in result.output


@pytest.fixture
def test_solution_create_in_non_empty_dir(request):

    os.chdir(tests_dir)

    cli = __import__("iotedgedev.cli", fromlist=['main'])
    runner = CliRunner()
    result = runner.invoke(cli.main, ['solution', 'new', test_solution])
    print(result.output)

    assert "Directory is not empty" in result.output


@pytest.fixture
def test_solution_create_in_empty_child_dir(request):

    os.chdir(test_solution_dir)

    dirname = "emptydir"
    os.makedirs(dirname)

    cli = __import__("iotedgedev.cli", fromlist=['main'])
    runner = CliRunner()
    result = runner.invoke(cli.main, ['solution', 'new', dirname])
    print(result.output)

    assert 'AZURE IOT EDGE SOLUTION CREATED' in result.output


def test_module_add():
    """Test the addmodule command"""
    os.chdir(test_solution_dir)
    cli = __import__("iotedgedev.cli", fromlist=['main'])
    runner = CliRunner()

    add_module_and_verify(cli.main, runner, "c")
    add_module_and_verify(cli.main, runner, "csharp")
    add_module_and_verify(cli.main, runner, "java")

    if (platform.system().lower() == 'windows'):
        add_module_and_verify(cli.main, runner, "nodejs")
        launch_file = launch_json_file
    else:
        launch_file = launch_json_file_without_nodejs

    add_module_and_verify(cli.main, runner, "python")
    add_module_and_verify(cli.main, runner, "csharpfunction")

    assert_json_file_equal(os.path.join(os.getcwd(), ".vscode", "launch.json"), launch_file)


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
    result = runner.invoke(cli.main, ['push', '-P', get_docker_os_type()])
    print(result.output)
    print(result.exception)

    assert 'BUILD COMPLETE' in result.output
    assert 'PUSH COMPLETE' in result.output
    assert 'ERROR' not in result.output


@pytest.fixture
def test_deploy_modules(request):

    os.chdir(test_solution_dir)

    cli = __import__("iotedgedev.cli", fromlist=['main'])
    runner = CliRunner()

    result = runner.invoke(cli.main, ['deploy', '-f', os.path.join('config', 'deployment.' + get_docker_os_type() + '.json')])
    print(result.output)

    assert 'DEPLOYMENT COMPLETE' in result.output
    assert 'ERROR' not in result.output


def test_monitor(request, capfd):

    os.chdir(test_solution_dir)

    cli = __import__("iotedgedev.cli", fromlist=['main'])
    runner = CliRunner()
    result = runner.invoke(cli.main, ['monitor', '--timeout', '5'])
    out, err = capfd.readouterr()
    print(out)
    print(err)
    print(result.output)
    print(result.exception)

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
    assert connectionstring.iothub_host.name
    assert connectionstring.iothub_host.hub_name
    assert connectionstring.shared_access_key
    assert connectionstring.shared_access_key_name


def test_valid_env_device_connectionstring():
    envvars.load_dotenv()
    env_device_connectionstring = os.getenv("DEVICE_CONNECTION_STRING")
    connectionstring = DeviceConnectionString(env_device_connectionstring)
    assert connectionstring.iothub_host.name
    assert connectionstring.iothub_host.hub_name
    assert connectionstring.shared_access_key
    assert connectionstring.device_id


def test_shared_lib():
    os.chdir(test_solution_shared_lib_dir)

    cli = __import__("iotedgedev.cli", fromlist=['main'])
    runner = CliRunner()
    result = runner.invoke(cli.main, ['build', '-P', get_docker_os_type()])
    print(result.output)
    print(result.exception)

    assert 'BUILD COMPLETE' in result.output
    assert 'ERROR' not in result.output


def add_module_and_verify(main, runner, template):
    module_name = template + "module"
    result = runner.invoke(main, ["solution", "add", module_name, '--template', template])
    print(result.output)
    print(result.exception)
    assert 'ADD COMPLETE' in result.output
    assert os.path.exists(os.path.join(os.environ["MODULES_PATH"], module_name))
    assert module_name in json.load(open(os.environ["DEPLOYMENT_CONFIG_TEMPLATE_FILE"]))["modulesContent"]["$edgeAgent"]["properties.desired"]["modules"]
