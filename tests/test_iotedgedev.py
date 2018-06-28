import json
import os
import shutil
import pytest

from click.testing import CliRunner

root_dir = os.getcwd()
tests_dir = os.path.join(root_dir, "tests")
env_file = os.path.join(root_dir, ".env")
test_solution = "test_solution"
node_solution = "node_solution"
test_solution_dir = os.path.join(tests_dir, test_solution)
node_solution_dir = os.path.join(tests_dir, node_solution)


@pytest.fixture(scope="module", autouse=True)
def create_solution(request):

    cli = __import__("iotedgedev.cli", fromlist=['main'])
    # print cli
    # out, err = capsys.readouterr()
    # print out

    runner = CliRunner()
    os.chdir(tests_dir)
    result = runner.invoke(cli.main, ['solution', test_solution, '--module', 'filtermodule'])
    print(result.output)
    assert 'AZURE IOT EDGE SOLUTION CREATED' in result.output

    shutil.copyfile(env_file, os.path.join(test_solution_dir, '.env'))
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
    result = runner.invoke(cli.main, ['solution', '.', '--module', 'filtermodule'])
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
    result = runner.invoke(cli.main, ['solution', '.', '--module', 'filtermodule'])
    print(result.output)

    assert 'AZURE IOT EDGE SOLUTION CREATED' in result.output


@pytest.fixture
def test_solution_create_in_non_empty_dir(request):

    os.chdir(tests_dir)

    cli = __import__("iotedgedev.cli", fromlist=['main'])
    runner = CliRunner()
    result = runner.invoke(cli.main, ['solution', test_solution, '--module', 'filtermodule'])
    print(result.output)

    assert "Directory is not empty" in result.output


@pytest.fixture
def test_solution_create_in_empty_child_dir(request):

    os.chdir(test_solution_dir)

    dirname = "emptydir"
    os.makedirs(dirname)

    cli = __import__("iotedgedev.cli", fromlist=['main'])
    runner = CliRunner()
    result = runner.invoke(cli.main, ['solution', dirname, '--module', 'filtermodule'])
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

    result = runner.invoke(cli.main, ["addmodule", "_csharpmodule", "--template", "csharp"])
    print(result.output)
    assert "Module name cannot start or end with the symbol _" in result.output

    result = runner.invoke(cli.main, ["addmodule", "csharpmodule_", "--template", "csharp"])
    print(result.output)
    assert "Module name cannot start or end with the symbol _" in result.output

    result = runner.invoke(cli.main, ["addmodule", "csharp-module", "--template", "csharp"])
    print(result.output)
    assert "Module name can only contain alphanumeric characters and the symbol _" in result.output

    result = runner.invoke(cli.main, ["addmodule", "filtermodule", "--template", "csharp"])
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


@pytest.fixture
def test_start_runtime(request):

    os.chdir(test_solution_dir)

    cli = __import__("iotedgedev.cli", fromlist=['main'])
    runner = CliRunner()
    result = runner.invoke(cli.main, ['start'])
    print(result.output)

    assert 'Runtime started' in result.output


@pytest.fixture
def test_monitor(request, capfd):

    os.chdir(test_solution_dir)

    cli = __import__("iotedgedev.cli", fromlist=['main'])
    runner = CliRunner()
    result = runner.invoke(cli.main, ['monitor', '--timeout', '60000'])
    out, err = capfd.readouterr()
    print(out)
    print(err)
    print(result.output)

    assert 'timeCreated' in out


@pytest.fixture
def test_stop(request):

    os.chdir(test_solution_dir)

    cli = __import__("iotedgedev.cli", fromlist=['main'])
    runner = CliRunner()
    result = runner.invoke(cli.main, ['stop'])
    print(result.output)

    assert 'Runtime stopped' in result.output


def test_e2e(test_push_modules, test_deploy_modules, test_start_runtime, test_monitor, test_stop):
    print('Testing E2E')


@pytest.fixture
def setup_node_solution(request):

    shutil.copyfile(env_file, os.path.join(node_solution_dir, '.env'))
    os.chdir(node_solution_dir)

    def clean():
        os.chdir(root_dir)
    request.addfinalizer(clean)
    return


def test_node(setup_node_solution, test_push_modules, test_deploy_modules, test_start_runtime, test_monitor, test_stop):
    print('Testing Node Solution')


'''
def test_load_no_dotenv():

    dotenv_file = ".env.nofile"
    os.environ["DOTENV_FILE"] = dotenv_file

    # cli_inst =
    # runner = CliRunner()
    # result = runner.invoke(cli.main, ['--set-config'])
    # print result.output
    # assert result.exit_code == 0
    # assert '.env.test file not found on disk.' in result.output
    # assert 'PROCESSING' in result.output
'''


def add_module_and_verify(main, runner, template):
    module_name = template + "module"
    result = runner.invoke(main, ['addmodule', module_name, '--template', template])
    print(result.output)
    assert 'ADD COMPLETE' in result.output
    assert os.path.exists(os.path.join(os.environ["MODULES_PATH"], module_name))
    assert module_name in json.load(open(os.environ["DEPLOYMENT_CONFIG_TEMPLATE_FILE"]))["moduleContent"]["$edgeAgent"]["properties.desired"]["modules"]
