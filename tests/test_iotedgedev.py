import pytest
import os
import shutil

import click
from click.testing import CliRunner
from iotedgedev.envvars import EnvVars
from iotedgedev.output import Output
# from iotedgedev import cli

test_solution = "test_solution"
root_dir = os.getcwd()
nodesolution = "node_solution"


@pytest.fixture(scope="module", autouse=True)
def create_project(request):

    cli = __import__("iotedgedev.cli", fromlist=['main'])
    # print cli
    # out, err = capsys.readouterr()
    # print out

    runner = CliRunner()
    result = runner.invoke(cli.main, ['solution', test_solution])
    print (result.output)
    assert 'AZURE IOT EDGE SOLUTION CREATED' in result.output
    shutil.copyfile('.env', os.path.join(os.getcwd(), test_solution, '.env'))
    os.chdir(test_solution)

    def clean():
        os.chdir("..")
        shutil.rmtree(os.path.join(root_dir, test_solution), ignore_errors=True)
    request.addfinalizer(clean)
    return


@pytest.fixture
def test_build_modules(request):

    os.chdir(os.path.join(root_dir, test_solution))

    cli = __import__("iotedgedev.cli", fromlist=['main'])
    runner = CliRunner()
    result = runner.invoke(cli.main, ['build'])
    print (result.output)

    assert 'BUILD COMPLETE' in result.output


@pytest.fixture
def test_deploy_modules(request):

    os.chdir(os.path.join(root_dir, test_solution))

    cli = __import__("iotedgedev.cli", fromlist=['main'])
    runner = CliRunner()
    result = runner.invoke(cli.main, ['deploy'])
    print (result.output)

    assert 'DEPLOY COMPLETE' in result.output


@pytest.fixture
def test_start_runtime(request):

    os.chdir(os.path.join(root_dir, test_solution))

    cli = __import__("iotedgedev.cli", fromlist=['main'])
    runner = CliRunner()
    result = runner.invoke(cli.main, ['start'])
    print (result.output)

    assert 'Runtime started' in result.output


@pytest.fixture
def test_monitor(request, capfd):

    os.chdir(os.path.join(root_dir, test_solution))

    cli = __import__("iotedgedev.cli", fromlist=['main'])
    runner = CliRunner()
    result = runner.invoke(cli.main, ['monitor', '--timeout', '40000'])
    out, err = capfd.readouterr()
    print (out)
    print (err)
    print (result.output)

    assert 'application properties' in out


@pytest.fixture
def test_stop(request):

    os.chdir(os.path.join(root_dir, test_solution))

    cli = __import__("iotedgedev.cli", fromlist=['main'])
    runner = CliRunner()
    result = runner.invoke(cli.main, ['stop'])
    print (result.output)

    assert 'Runtime stopped' in result.output


def test_e2e(test_build_modules, test_deploy_modules, test_start_runtime, test_monitor, test_stop):
    print ('Testing E2E')


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
