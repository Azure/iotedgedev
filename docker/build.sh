#!/bin/bash

# read IoTEdgeDev version from python __init__ file
export VERSION=$(cat ../iotedgedev/__init__.py | grep '__version__' | grep -oP "'\K[^']+")

PYTHON2="2.7.14"
PYTHON3="3.6.5"

build_linux=1
build_windows=1

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
    docker build --build-arg PYTHON2_VERSION=$PYTHON2 --build-arg PYTHON3_VERSION=$PYTHON3 -f Dockerfile -t microsoft/iotedgedev:$VERSION-windows -t microsoft/iotedgedev:latest-windows .

    cd ..
}

if [ $1 = "--help" ]; then    
    echo "Usage:"
    echo "build.sh [linux|windows]"
    exit 1
fi

if [ $1 = "linux" ]; then
    build_windows=0
    echo "===== Building Linux image only"
fi

if [ $1 = "windows" ]; then
    build_linux=0
    echo "===== Building Windows image only"
fi

mode=$(get_docker_mode)
echo "===== Docker is in '$mode' container mode"
if [ $mode = "windows" ]; then
    # Docker is in Windows Container mode
    if [ $build_windows = "1" ]; then
        build_windows
    fi
    if [ $build_linux = "1" ]; then
        switch_docker
        build_linux
        switch_docker
    fi
else
    # Docker is in Linux Container mode
    if [ $build_linux -eq "1" ]; then    
        build_linux
    fi
    if [ $build_windows -eq "1" ]; then    
        switch_docker
        build_windows
        switch_docker
    fi
fi