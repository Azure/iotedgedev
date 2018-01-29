#!/bin/bash
docker run -it -v /var/run/docker.sock:/var/run/docker.sock jongallant/iotedgedev-deps:$1-linux