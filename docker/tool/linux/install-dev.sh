#!/bin/sh

# This script will be executed INSIDE the container

cd /home/iotedge/tool
pip install -r requirements_dev.txt
pip install -e .
cd /home/iotedge