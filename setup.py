#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""
import atexit
from subprocess import check_call
from setuptools import setup, find_packages
from setuptools.command.install import install
from setuptools.command.develop import develop


def _execute():
    check_call("pip install azure-cli --no-deps".split())

class PostInstall(install):
    def run(self):
        atexit.register(_execute)
        install.run(self)

class PostDevelop(develop):
    def run(self):
        atexit.register(_execute)
        develop.run(self)


# with open('README.rst') as readme_file:
#    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'Click>=6.0',
    'docker==3.0.0',
    'python-dotenv',
    'requests',
    'fstrings',
    'azure-iot-edge-runtime-ctl==1.0.0rc21',
    'azure-cli-iot',
    'azure-cli-profile',
    'azure-cli-extension',
    'azure-cli-configure',
    'azure-cli-resource',
    'azure-cli-cloud'
]

setup_requirements = [
    # TODO(jonbgallant): put setup requirements (distutils extensions, etc.) here
]

test_requirements = [
    # TODO: put package test requirements here
]


setup(
    name='azure-iot-edge-dev-cli',
    version='0.78.0',
    description="The Azure IoT Edge Dev CLI greatly simplifies the IoT Edge development process by automating many routine manual tasks, such as building, deploying, pushing modules and configuring the IoT Edge Runtime.",
    long_description="See https://github.com/azure/iot-edge-dev-cli for usage instructions.",
    author="Jon Gallant",
    author_email='info@jongallant.com',
    url='https://github.com/azure/iot-edge-dev-cli',
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
    keywords='azure iot edge dev cli',
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
    cmdclass={'install': PostInstall, 'develop': PostDevelop}
)
