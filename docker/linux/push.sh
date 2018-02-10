#!/bin/bash
winpty docker login
docker push jongallant/iotedgedev-deps:$1
docker push jongallant/iotedgedev-deps:$1-linux
docker push jongallant/iotedgedev-deps:latest
docker push jongallant/iotedgedev-deps:latest-linux
docker push jongallant/iotedgedev-dev:$1
docker push jongallant/iotedgedev-dev:$1-linux
docker push jongallant/iotedgedev-dev:latest
docker push jongallant/iotedgedev-dev:latest-linux
docker push jongallant/iotedgedev:$1
docker push jongallant/iotedgedev:$1-linux
docker push jongallant/iotedgedev:latest
docker push jongallant/iotedgedev:latest-linux
