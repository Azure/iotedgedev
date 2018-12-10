import os
import shutil

import pytest
from click.testing import CliRunner

from iotedgedev.compat import PY35
from iotedgedev.envvars import EnvVars
from iotedgedev.output import Output

from .utility import get_docker_os_type

pytestmark = pytest.mark.e2e

root_dir = os.getcwd()
tests_dir = os.path.join(root_dir, 'tests')
output = Output()
envvars = EnvVars(output)
env_file_name = envvars.get_dotenv_file()
env_file_path = envvars.get_dotenv_path(env_file_name)

test_solution = 'test_solution'
test_solution_dir = os.path.join(tests_dir, test_solution)


@pytest.fixture(scope="module", autouse=True)
def create_solution(request):
    cli = __import__('iotedgedev.cli', fromlist=['main'])

    runner = CliRunner()
    os.chdir(tests_dir)
    result = runner.invoke(cli.main, ['solution', 'new', test_solution])
    print(result.output)

    assert 'AZURE IOT EDGE SOLUTION CREATED' in result.output

    shutil.copyfile(env_file_path, os.path.join(test_solution_dir, env_file_name))
    os.chdir(test_solution_dir)

    def clean():
        os.chdir(root_dir)
        shutil.rmtree(test_solution_dir, ignore_errors=True)
        runner.invoke(cli.main, ['simulator', 'stop'])

    request.addfinalizer(clean)

    return


@pytest.mark.skipif(get_docker_os_type() == 'windows', reason='Simulator does not support windows container')
def test_setup():
    cli = __import__('iotedgedev.cli', fromlist=['main'])
    runner = CliRunner()

    result = runner.invoke(cli.main, ['simulator', 'setup'])
    print(result.output)

    assert 'Setup IoT Edge Simulator successfully.' in result.output


@pytest.mark.skipif(get_docker_os_type() == 'windows', reason='Simulator does not support windows container')
def test_start_single():
    cli = __import__('iotedgedev.cli', fromlist=['main'])
    runner = CliRunner()

    result = runner.invoke(cli.main, ['simulator', 'start', '-i', 'input1'])
    print(result.output)

    assert 'IoT Edge Simulator has been started in single module mode.' in result.output


@pytest.mark.skipif(get_docker_os_type() == 'windows', reason='Simulator does not support windows container')
def test_modulecred():
    cli = __import__('iotedgedev.cli', fromlist=['main'])
    runner = CliRunner()

    result = runner.invoke(cli.main, ['simulator', 'modulecred'])
    print(result.output)

    assert 'EdgeHubConnectionString=HostName=' in result.output
    assert 'EdgeModuleCACertificateFile=' in result.output


@pytest.mark.skipif(get_docker_os_type() == 'windows', reason='Simulator does not support windows container')
def test_stop(capfd):
    cli = __import__('iotedgedev.cli', fromlist=['main'])
    runner = CliRunner()

    result = runner.invoke(cli.main, ['simulator', 'stop'])
    print(result.output)
    out, err = capfd.readouterr()
    print(out)
    print(err)

    assert 'IoT Edge Simulator has been stopped successfully.' in out


@pytest.mark.skipif(get_docker_os_type() == 'windows', reason='Simulator does not support windows container')
def test_start_solution(capfd):
    cli = __import__('iotedgedev.cli', fromlist=['main'])
    runner = CliRunner()

    result = runner.invoke(cli.main, ['simulator', 'start', '-s', '-b', '-f', 'deployment.template.json'])
    print(result.output)
    print(result.exception)
    out, err = capfd.readouterr()
    print(out)
    print(err)

    assert 'BUILD COMPLETE' in result.output
    assert 'IoT Edge Simulator has been started in solution mode.' in out


@pytest.mark.skipif(get_docker_os_type() == 'windows', reason='Simulator does not support windows container')
def test_monitor(capfd):
    cli = __import__('iotedgedev.cli', fromlist=['main'])
    runner = CliRunner()
    result = runner.invoke(cli.main, ['monitor', '--timeout', '20'])
    out, err = capfd.readouterr()
    print(out)
    print(err)
    print(result.output)
    print(result.exception)

    # Assert output from simulator
    sim_match = 'timeCreated'

    if not PY35:
        assert 'Monitoring events from device' in out
        assert sim_match in out
    else:
        assert not err
        assert sim_match in result.output
