#!/bin/bash

# read IoTEdgeDev version from python __init__ file
export VERSION=$(cat ../iotedgedev/__init__.py | grep '__version__' | grep -oP "'\K[^']+")

PYTHON2="2.7.14"
PYTHON3="3.6.5"

function switch_docker
{
    echo "===== Switching Docker engine"
    echo "===== From: " $(docker version --format '{{.Server.Os}}')
    /c/Program\ Files/Docker/Docker/DockerCli.exe -SwitchDaemon
    echo "===== To: " $(docker version --format '{{.Server.Os}}')
}

function get_docker_mode
{
    echo $(docker version --format '{{.Server.Os}}')
}

function check_docker_expected_mode 
{
    local mode=$(get_docker_mode)    

    if [ $mode != $1 ]; then
        echo "===== ERROR: docker is not in expected mode: '$1'"
        exit 1
    fi    
}

function build_linux
{
    echo "===== Building Linux Based images"

    check_docker_expected_mode "linux"

    cd linux
    docker build -f Dockerfile -t microsoft/iotedgedev:$VERSION-linux -t microsoft/iotedgedev:latest-linux .

    cd ..
}

function build_windows
{
    echo "===== Building Windows Based images"
    
    check_docker_expected_mode "windows"

    cd windows

    echo "===== Building Windows Based image (Python $PYTHON3)"
    docker build --build-arg PYTHON_VERSION=$PYTHON3 -f Dockerfile -t microsoft/iotedgedev:$VERSION-windows -t microsoft/iotedgedev:latest-windows -t microsoft/iotedgedev:$VERSION-windows-py3 -t microsoft/iotedgedev:latest-windows-py3 .

    cd ..
}

mode=$(get_docker_mode)
echo "===== Docker is in '$mode' container mode"
if [ $mode = "windows" ]; then
    # Docker is in Windows Container mode
    build_windows
    switch_docker
    build_linux
    switch_docker
else
    # Docker is in Linux Container mode
    build_linux
    switch_docker
    build_windows
    switch_docker
fi

