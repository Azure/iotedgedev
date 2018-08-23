#!/bin/bash

# stop on error
set -e

function show_help
{
    echo "Usage:"
    echo "build.sh test|prod major|minor imagename [windows|linux]"
    echo "test: uses pypitest, prod: uses pypi"
    echo "major: bumpversion major, minor: bumpversion minor --no-commit --no-tag"
    echo "imagename: jongacr.azurecr.io/iotedgedev || microsoft/iotedgedev"
    echo "windows: builds only windows container, linux: builds only linux container. omit to build both."
    echo "NOTES: 1. You must have .pypirc in repo root with pypi and pypitest sections. 2. You must have .env file in root with connection strings set."
    
    exit 1
}

MODE="$1"
MAJOR_MINOR="$2"
IMAGE_NAME="$3"
PLATFORM="$4"

if [ -z "$MODE" ] || [ -z "$MAJOR_MINOR" ] || [ -z "$IMAGE_NAME" ]; then
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

    echo -e "\n===== Running Tox"
    tox
}

function get_version
{
    VERSION=$(cat ./iotedgedev/__init__.py | grep '__version__' | grep -oP "'\K[^']+")
    echo ${VERSION}
}

function run_bumpversion {
    echo -e "\n===== Bumping version"

    if [ "$MODE" = "prod" ]; then
        bumpversion $MAJOR_MINOR
    else
        bumpversion $MAJOR_MINOR --no-commit --no-tag --allow-dirty
    fi
}

function run_build_wheel
{
    echo -e "\n===== Building Python Wheel"
    python setup.py bdist_wheel 
}

function run_upload_pypi
{
    echo -e "\n===== Uploading to PyPi"
    PYPI=$([ "$MODE" = "prod" ] && echo "pypi" || echo "pypitest")
    twine upload -r ${PYPI} --config-file .pypirc dist/iotedgedev-$(get_version)-py2.py3-none-any.whl
}

function run_build_docker
{
    echo -e "\n===== Building Docker Containers"
    ./docker/tool/build-docker.sh $PLATFORM
}

function run_push_docker 
{
    echo -e "\n===== Pushing Docker Containers"
    ./docker/tool/push-docker.sh $IMAGE_NAME
}

function run_push_git
{
    echo -e "\n===== Pushing Tags to Git"

    if [ "$MODE" = "prod" ]; then
        git push --tags && git push
    fi
}

run_bumpversion
#run_tox
run_build_wheel
run_upload_pypi
run_build_docker
run_push_docker
run_push_git

echo -e "\n===== All done"
