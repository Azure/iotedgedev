#!/bin/bash

# stop on error
set -e

function show_help
{
    echo "Usage:"
    echo "push-docker.sh [<version>]"
    echo ""
    echo "version: version to push. Automatically detected if not specified"
    exit 1
}

# iotedgetoolscontainerregistry.azure.io is the ACR that has a webhook to publish to MCR
# only this ACR should be used
ACR_LOGIN_SERVER="iotedgetoolscontainerregistry.azurecr.io"
IMAGE_NAME="iotedgedev"
VERSION="$1"

if [ "$VERSION" = "--help" ]; then    
    show_help
fi

if [ -z "$VERSION" ]; then
    echo -e "\n===== Detecting version"
    VERSION=$(cat ../../iotedgedev/__init__.py | grep '__version__' | grep -oP "'\K[^']+")
    echo "Detected version $VERSION"
fi

echo -e "\n===== Pushing Docker images"
docker push $ACR_LOGIN_SERVER/public/iotedge/$IMAGE_NAME:$VERSION-amd64
docker push $ACR_LOGIN_SERVER/public/iotedge/$IMAGE_NAME:$VERSION
docker push $ACR_LOGIN_SERVER/public/iotedge/$IMAGE_NAME:latest-amd64
docker push $ACR_LOGIN_SERVER/public/iotedge/$IMAGE_NAME:latest