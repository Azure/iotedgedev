import json
import os
import pytest
from .utility import (
    get_platform_type,
    runner_invoke,
)

pytestmark = pytest.mark.e2e

tests_dir = os.path.join(os.getcwd(), "tests")
test_solution_shared_lib_dir = os.path.join(tests_dir, "assets", "test_solution_shared_lib")


#def test_build_and_push():
#    os.chdir(test_solution_shared_lib_dir)

#    result = runner_invoke(['build', '--push', '-f', "layered_deployment.template_with_flattened_props.json", '-P', get_platform_type()])
    # print(result.output)
    #assert 'sample_module:0.0.1-RC' in result.output
#    assert 'BUILD COMPLETE' in result.output
#    assert 'PUSH COMPLETE' in result.output
#    assert 'ERROR' not in result.output


def test_build_and_push_with_no_modules():
    os.chdir(test_solution_shared_lib_dir)

    result = runner_invoke(['build', '--push', '-f', "layered_deployment.template_with_no_modules.json", '-P', get_platform_type()])

    new_config_deployment_name = 'layered_deployment.template_with_no_modules.json'
    new_config_deployment_path = os.path.join(test_solution_shared_lib_dir, 'config', new_config_deployment_name)

    with open(new_config_deployment_path, "r") as f:
        content = json.load(f)

    set_property = content["content"]["modulesContent"]["exampleModule"]["properties.desired"]["foo"]

    assert 'ERROR' not in result.output
    assert 'bar-1.0' == set_property
