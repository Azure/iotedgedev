#!/bin/bash
docker run -it -v /var/run/docker.sock:/var/run/docker.sock -v c:/temp/iotedge:/iotedge microsoft/iotedgedev