#!/bin/bash

# stop on error
set -e

echo "===== Checking pre-requisistes"
IS_ADMIN=$(powershell '([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")')
if [ "$IS_ADMIN" = "False" ]; then        
    echo "build script must be run as administrator"
    exit 1
fi

#TODO
# check if running in administrator mode
# make sure docker is in linux mode
# stop and restart docker to make sure to avoid networking problem?

echo "===== Preventive cleanup"
rm __pycache__ -rf
rm .pytest_cache -rf
rm .tox -rf
rm .pytest_cache -rf
rm tests/__pycache__ -rf

echo "===== Running smoke tests"
tox

echo "===== Bumping version"
bumpversion minor

echo "===== Building Python Wheel"
python setup.py bdist_wheel 

echo "===== Uploading to PyPi"
VERSION=$(cat ./iotedgedev/__init__.py | grep '__version__' | grep -oP "'\K[^']+")
twine upload --repository-url https://test.pypi.org/legacy/  dist/iotedgedev-$VERSION-py2.py3-none-any.whl

echo "===== Building Docker images"
cd docker
./build-docker.sh

echo "===== Pushing Docker images"
#TODO

echo "===== Creating Multi-Arch Docker image"
#TODO

echo "===== Pushing Docker Multi-Arch image"
#TODO
