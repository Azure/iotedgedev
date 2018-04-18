#!/bin/bash
export VERSION=$1
docker build -f Dockerfile -t microsoft/iotedgedev:$1 -t microsoft/iotedgedev:$1-nanoserver -t microsoft/iotedgedev:latest-nanoserver .
