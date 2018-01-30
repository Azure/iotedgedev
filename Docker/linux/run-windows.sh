#!/bin/bash
docker run -it -v /var/run/docker.sock:/var/run/docker.sock -v c:/temp/edgeprojects:/home jongallant/iotedgedev:$1-linux