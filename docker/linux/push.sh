#!/bin/bash
winpty docker login
docker push microsoft/iotedgedev:$1
docker push microsoft/iotedgedev:$1-linux
docker push microsoft/iotedgedev:latest
docker push microsoft/iotedgedev:latest-linux
