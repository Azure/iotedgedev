#!/bin/bash

folder=$(echo $PWD | cut -d/ -f-6 | sed 's,/,//,g')

winpty docker run -it -v //var//run//docker.sock://var//run//docker.sock -v $folder://home//iotedge//tool mcr.microsoft.com/iotedge/iotedgedev:latest
