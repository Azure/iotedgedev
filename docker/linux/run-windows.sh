#!/bin/bash

folder=$(echo $PWD | cut -d/ -f-6)

docker run -it -v /var/run/docker.sock:/var/run/docker.sock -v $folder:/iotedge microsoft/iotedgedev:latest-linux