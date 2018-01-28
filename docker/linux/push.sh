#!/bin/bash
winpty docker login
docker push jongallant/iotedgedev:$1-deps-linux
docker push jongallant/iotedgedev:latest-deps-linux
docker push jongallant/iotedgedev:$1-linux
docker push jongallant/iotedgedev:latest-linux