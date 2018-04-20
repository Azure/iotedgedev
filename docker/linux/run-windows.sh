#!/bin/bash

folder=$(echo $PWD | cut -d/ -f-6) | sed -e 's:/c:c\::g' | sed -e 's:/:\\:g'

docker run -it -v /var/run/docker.sock:/var/run/docker.sock -v $folder:/home/iotedge/tool microsoft/iotedgedev:latest-linux
