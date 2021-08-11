import os
import pytest
from .utility import (
    get_platform_type,
    runner_invoke,
)

pytestmark = pytest.mark.unit

tests_dir = os.path.join(os.getcwd(), "tests")
test_assets_dir = os.path.join(tests_dir, "assets")
test_file_1 = os.path.join(test_assets_dir, "layered_deployment.template.json")
test_solution_shared_lib_dir = os.path.join(tests_dir, "assets", "test_solution_shared_lib")


def test_build_and_push():
    os.chdir(test_solution_shared_lib_dir)

    result = runner_invoke(['build', '--push', '-f', '../layered_deployment.template.json', '-P', get_platform_type()])

    assert 'sample_module:0.0.1-RC' in result.output
    assert 'BUILD COMPLETE' in result.output
    assert 'PUSH COMPLETE' in result.output
    assert 'ERROR' not in result.output
