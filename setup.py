#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""
import sys
from os import path

from setuptools import setup, find_packages

#with open('README.rst') as readme_file:
#    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'Click>=6.0',
    'docker==2.6.0',
    'python-dotenv',
    'requests',
    'azure-iot-edge-runtime-ctl', 
    'azure-cli', 
    'fstrings'
]

setup_requirements = [
    # TODO(jonbgallant): put setup requirements (distutils extensions, etc.) here
]

test_requirements = [
    # TODO: put package test requirements here
]


setup(
    name='azure-iot-edge-dev-tool',
    version='0.64.0',
    description="The Azure IoT Edge Dev Tool package greatly simplifies your IoT Edge development process by automating many of your routine manual tasks, such as building, deploying, pushing modules and configuring your IoT Edge Runtime.",
    long_description="See https://github.com/jonbgallant/azure-iot-edge-dev-tool for usage instructions.",
    author="Jon Gallant",
    author_email='info@jongallant.com',
    url='https://github.com/jonbgallant/azure-iot-edge-dev-tool',
    packages=find_packages(include=['iotedgedev']),
    entry_points={
        'console_scripts': [
            'iotedgedev=iotedgedev.cli:main'
        ]
    },
    include_package_data=True,
    install_requires=requirements,
    license="MIT license",
    zip_safe=False,
    keywords='azure iot edge dev tool',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    test_suite='tests',
    tests_require=test_requirements,
    setup_requires=setup_requirements,
)
