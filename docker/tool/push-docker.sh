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
    echo "push-docker.sh <dockerhub> <platform> [<version>]"
    echo ""
    echo "dockerhub: docker hub name (eg:microsoft/iotedgedev) used for pushing created images"    
    echo "platform: linux|windows|empty"
    echo "version: version to push. Automatically detected if not specified"
    exit 1
}

IMAGE_NAME="$1"
PLATFORM="$2"
VERSION="$3"

if [ "$IMAGE_NAME" = "--help" ]; then    
    echo "Usage:"
    echo "push-docker.sh imagename [linux|windows]"
    exit 1
fi

if [ -z "$VERSION" ]; then
    echo -e "\n===== Detecting version"
    VERSION=$(cat ../iotedgedev/__init__.py | grep '__version__' | grep -oP "'\K[^']+")
    echo "Detected version $VERSION"
fi

docker push $IMAGE_NAME:$VERSION-amd64 
docker push $IMAGE_NAME:latest-amd64 

#TODO add windows container support.  For now we only push linux.
#docker push $IMAGE_NAME:$VERSION-windows-amd64
#docker push $IMAGE_NAME:latest-windows-amd64

echo -e "\n===== Creating Multi-Arch Docker image"
#docker manifest create $IMAGE_NAME:latest $IMAGE_NAME:latest-amd64 $IMAGE_NAME:latest-windows-amd64 
docker manifest create --insecure $IMAGE_NAME:latest $IMAGE_NAME:latest-amd64 

echo -e "\n===== Pushing Docker Multi-Arch image"
docker manifest push --purge $IMAGE_NAME:latest

if [ in_docker_folder = 0 ]; then
    cd original_folder
fi