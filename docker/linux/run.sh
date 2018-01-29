#!/bin/bash
docker run -it -v /var/run/docker.sock:/var/run/docker.sock jongallant/iotedgedev:$1-linux