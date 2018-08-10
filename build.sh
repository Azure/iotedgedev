#!/bin/bash

# stop on error
set -e

function show_help
{
    echo "Usage:"
    echo "build.sh <mode>"
    echo ""
    echo "mode: test|prod [windows|linux]"
    exit 1
}

MODE="$1"
PLATFORM="$2"

if [ -z "$MODE" ]; then
    show_help
fi

echo -e "\n===== Setting up build environment"
if [ "$MODE" = "test" ]; then
    echo "Environment: $MODE"
elif [ "$MODE" = "prod" ]; then
    echo "Environment: $MODE"
else
    echo "ERROR> Build mode parameter not known. must be 'prod' or 'test'"
    exit 1
fi

if [ ! -z $PLATFORM ]; then
    echo "Platform: $PLATFORM"
fi

echo -e "\n===== Checking pre-requisistes"
IS_ADMIN=$(powershell '([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")')
if [ "$IS_ADMIN" = "False" ]; then        
    echo "ERROR> Build script must be run as administrator"
    exit 1
fi

#TODO
# check if running in administrator mode
# make sure docker is in linux mode
# make sure docker supports manifest option
# stop and restart docker to make sure to avoid networking problem?
# check that dockerhub exists and is accessible
# check that pipy repo exists and is accessible
# make sure there are no pending changes in GIT otherwise bumpversion will complain

function run_tox {
    echo -e "\n===== Preventive cleanup"
    rm __pycache__ -rf
    rm .pytest_cache -rf
    rm .tox -rf
    rm .pytest_cache -rf
    rm tests/__pycache__ -rf

    echo -e "\n===== Running smoke tests"
    tox
}

function run_bumpversion {
    echo -e "\n===== Bumping version"
    bumpversion minor
}

function run_build
{
    echo -e "\n===== Building Python Wheel"
    python setup.py bdist_wheel 
}

function run_twine
{
    echo -e "\n===== Uploading to PyPi"
    twine upload -u $PIPYUSER --repository-url $PIPYREPO dist/iotedgedev-$VERSION-py2.py3-none-any.whl
}

function run_build_docker
{
    ./docker/build-docker.sh $PLATFORM
}

function run_push_docker 
{
    ./docker/push-docker.sh $1 $2
}


#run_tox
if [ "$MODE" = "prod" ]; then
    run_bumpversion
fi
run_build
#run_twine
run_build_docker
#run_push_docker

#./docker/push-docker.sh $DOCKERHUB

echo -e "\n===== All done"
