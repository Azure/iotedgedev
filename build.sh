#!/bin/bash

# stop on error
set -e

function show_help
{
    echo "Usage:"
    echo "build.sh <mode> <dockerhub> <pipyaccount>"
    echo ""
    echo "mode: test|prod"
    echo "dockerhub: docker hub name (eg:microsoft/iotedgedev) used for pushing created images"
    echo "pipyaccount: account name used to login into PyPi repository"
    exit 1
}

MODE="$1"
DOCKERHUB="$2"
PIPYUSER="$3"

if [ -z "$MODE" ] && [ -z "$DOCKERHUB" ]; then
    show_help
fi

echo -e "\n===== Setting up build environment"
if [ "$MODE" = "test" ]; then
    PIPYREPO="https://test.pypi.org/legacy/"
elif [ "$MODE" = "prod" ]; then
    PIPYREPO="https://pypi.org/legacy/"
else
    echo "ERROR> Build mode parameter not known. must be 'prod' or 'test'"
    exit 1
fi
echo "Building for: $MODE"
if [ -z "$DOCKERHUB" ]; then
    echo "ERROR> Build mode docker hub target not specified."
    exit 1
fi
echo "PyPi account used: $PIPYUSER"
if [ -z "$PIPYUSER" ]; then
    echo "ERROR> PyPi account name not specified."
    exit 1
fi
echo "Target Docker Hub: $DOCKERHUB"


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

echo -e "\n===== Preventive cleanup"
rm __pycache__ -rf
rm .pytest_cache -rf
rm .tox -rf
rm .pytest_cache -rf
rm tests/__pycache__ -rf

echo -e "\n===== Running smoke tests"
#tox

echo -e "\n===== Bumping version"
if [ "$MODE" = "prod" ]; then
    bumpversion minor
fi

echo -e "\n===== Detecting version"
VERSION=$(cat ./iotedgedev/__init__.py | grep '__version__' | grep -oP "'\K[^']+")

echo -e "\n===== Building Python Wheel"
python setup.py bdist_wheel 

echo -e "\n===== Uploading to PyPi"
twine upload -u $PIPYUSER --repository-url $PIPYREPO dist/iotedgedev-$VERSION-py2.py3-none-any.whl

echo -e "\n===== Building Docker images"
cd docker
./build-docker.sh

echo -e "\n===== Pushing Docker images"
docker push $DOCKERHUB:$VERSION-linux 
docker push $DOCKERHUB:latest-linux 
docker push $DOCKERHUB:$VERSION-windows 
docker push $DOCKERHUB:latest-windows 

echo -e "\n===== Creating Multi-Arch Docker image"
docker manifest create $DOCKERHUB:latest $DOCKERHUB:latest-linux $DOCKERHUB:latest-windows 

echo -e "\n===== Pushing Docker Multi-Arch image"
docker manifest push

echo -e "\n===== All done"
