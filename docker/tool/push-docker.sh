#!/bin/bash

# stop on error
set -e

# make sure we're in docker folder
original_folder=$PWD

if [ -z $"echo $PWD | grep /docker$" ]; then 
    in_docker_folder=1
else
    in_docker_folder=0
    cd docker
fi

function show_help
{
    echo "Usage:"
    echo "push-docker.sh <dockerhub> [<version>]"
    echo ""
    echo "dockerhub: docker hub name (eg:microsoft/iotedgedev) used for pushing created images"    
    echo "version: version to push. Automatically detected if not specified"
    exit 1
}

if [ "$1" = "--help" ]; then
    show_help
fi

DOCKERHUB="$1"

if [ -z "$DOCKERHUB" ]; then
    show_help
fi

if [ -z "$2" ]; then
    echo -e "\n===== Detecting version"
    VERSION=$(cat ../../iotedgedev/__init__.py | grep '__version__' | grep -oP "'\K[^']+")
    echo "Detected version $VERSION"
else
    VERSION="$2"
fi

echo -e "\n===== Pushing Docker images"
docker push $DOCKERHUB:$VERSION-linux 
docker push $DOCKERHUB:latest-linux 
docker push $DOCKERHUB:$VERSION-windows 
docker push $DOCKERHUB:latest-windows 

echo -e "\n===== Creating Multi-Arch Docker image"
docker manifest create $DOCKERHUB:latest $DOCKERHUB:latest-linux $DOCKERHUB:latest-windows 

echo -e "\n===== Pushing Docker Multi-Arch image"
docker manifest push

if [ in_docker_folder = 0 ]; then
    cd original_folder
fi