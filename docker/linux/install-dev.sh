#!/bin/sh
cd /home/tool
pip install -r requirements_dev.txt
pip install -e .
cd /home