import os
import pytest
import shutil
import time

from iotedgedev.version import PY35
from iotedgedev.envvars import EnvVars
from iotedgedev.output import Output

from .utility import get_docker_os_type
from .utility import get_platform_type
from .utility import runner_invoke

pytestmark = pytest.mark.e2e

output = Output()
envvars = EnvVars(output)

env_file_name = envvars.get_dotenv_file()
env_file_path = envvars.get_dotenv_path(env_file_name)

root_dir = os.getcwd()
tests_dir = os.path.join(root_dir, 'tests')

test_solution = 'test_solution'
test_solution_dir = os.path.join(tests_dir, test_solution)


@pytest.fixture(scope="module", autouse=True)
def create_solution(request):
    os.chdir(tests_dir)
    result = runner_invoke(['solution', 'new', test_solution])

    assert 'AZURE IOT EDGE SOLUTION CREATED' in result.output

    shutil.copyfile(env_file_path, os.path.join(test_solution_dir, env_file_name))
    os.chdir(test_solution_dir)

    def clean():
        os.chdir(root_dir)
        time.sleep(5)
        shutil.rmtree(test_solution_dir, ignore_errors=True)
        shutil.rmtree(test_solution_dir+"_shared_lib", ignore_errors=True)
        runner_invoke(['simulator', 'stop'])

    request.addfinalizer(clean)

    return


@pytest.mark.skipif(get_docker_os_type() == 'windows', reason='Simulator does not support windows container')
def test_setup():
    result = runner_invoke(['simulator', 'setup'])

    assert 'Setup IoT Edge Simulator successfully.' in result.output


@pytest.mark.skipif(get_docker_os_type() == 'windows', reason='Simulator does not support windows container')
def test_setup_with_iothub():
    result = runner_invoke(['simulator', 'setup', '-i', os.getenv("IOTHUB_CONNECTION_STRING")])

    assert 'Setup IoT Edge Simulator successfully.' in result.output


@pytest.mark.skipif(get_docker_os_type() == 'windows', reason='Simulator does not support windows container')
def test_start_single():
    result = runner_invoke(['simulator', 'start', '-i', 'input1'])

    assert 'IoT Edge Simulator has been started in single module mode.' in result.output


@pytest.mark.skipif(get_docker_os_type() == 'windows', reason='Simulator does not support windows container')
def test_modulecred():
    result = runner_invoke(['simulator', 'modulecred'])

    assert 'EdgeHubConnectionString=HostName=' in result.output
    assert 'EdgeModuleCACertificateFile=' in result.output


@pytest.mark.skipif(get_docker_os_type() == 'windows', reason='Simulator does not support windows container')
def test_stop(capfd):
    runner_invoke(['simulator', 'stop'])
    out, err = capfd.readouterr()

    assert 'IoT Edge Simulator has been stopped successfully.' in out


@pytest.mark.skipif(get_docker_os_type() == 'windows', reason='Simulator does not support windows container')
def test_start_solution(capfd):
    result = runner_invoke(['simulator', 'start', '-s', '-b', '-f', 'deployment.template.json'])
    out, err = capfd.readouterr()

    assert 'BUILD COMPLETE' in result.output
    assert 'IoT Edge Simulator has been started in solution mode.' in out


@pytest.mark.skipif(get_docker_os_type() == 'windows', reason='Simulator does not support windows container')
def test_start_solution_with_setup(capfd):
    result = runner_invoke(['simulator', 'start', '--setup', '-s', '-b', '-f', 'deployment.template.json'])
    out, err = capfd.readouterr()

    assert 'Setup IoT Edge Simulator successfully.' in result.output
    assert 'BUILD COMPLETE' in result.output
    assert 'IoT Edge Simulator has been started in solution mode.' in out


@pytest.mark.skipif(get_docker_os_type() == 'windows', reason='Simulator does not support windows container')
def test_monitor(capfd):
    try:
        result = runner_invoke(['monitor', '--timeout', '30'])
        out, err = capfd.readouterr()
        # Assert output from simulator
        sim_match = 'timeCreated'

        if not PY35:
            assert 'Monitoring events from device' in out
            assert sim_match in out
        else:
            assert not err
            assert sim_match in result.output
    finally:
        test_stop(capfd)


@pytest.mark.skipif(get_docker_os_type() == 'windows', reason='Simulator does not support windows container')
def test_start_solution_with_deployment(capfd):
    platform_type = get_platform_type()
    deployment_file_path = os.path.join(test_solution_dir, 'config', 'deployment.' + platform_type + '.json')
    runner_invoke(['simulator', 'start', '-f', deployment_file_path])
    out, err = capfd.readouterr()

    assert 'IoT Edge Simulator has been started in solution mode.' in out
    test_monitor(capfd)
