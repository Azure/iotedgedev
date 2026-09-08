#!/usr/bin/env python
from setuptools import find_packages, setup


with open('CHANGELOG.md') as history_file:
    history = history_file.read()

requirements = [
    'click>=8.1.7',
    'bcrypt>=4.0.0',
    'docker >= 7.1.0',
    'python-dotenv',
    'requests >= 2.26.0',
    'fstrings',
    'azure-cli-core >= 2.80.0',
    'jsonschema >= 4.26.0, < 5.0.0',
    'iotedgehubdev >= 0.14.19',
    'applicationinsights == 0.11.9',
    'commentjson == 0.9.0',
    'pyyaml>=6.0',
    'pywin32>=312; sys_platform == "win32"',
    'more-itertools'
]

setup_requirements = [
]

test_requirements = [
]


setup(
    name='iotedgedev',
    version='3.3.8',
    description='The Azure IoT Edge Dev Tool greatly simplifies the IoT Edge development process by automating many routine manual tasks, such as building, deploying, pushing modules and configuring the IoT Edge Runtime.',
    long_description='See https://github.com/azure/iotedgedev for usage instructions.',
    author='Microsoft Corporation',
    author_email='vsciet@microsoft.com',
    url='https://github.com/azure/iotedgedev',
    packages=find_packages(include=['iotedgedev']),
    entry_points={
        'console_scripts': [
            'iotedgedev=iotedgedev.cli:main'
        ]
    },
    include_package_data=True,
    install_requires=requirements,
    license='MIT license',
    zip_safe=False,
    keywords='azure iot edge dev tool',
    python_requires='>=3.11, <3.15',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'Programming Language :: Python :: 3.14'
    ],
    test_suite='tests',
    tests_require=test_requirements,
    setup_requires=setup_requirements
)
