# Changelog
All notable changes to this project since 0.82.0 will be documented in this file.

## [3.3.0] - 2021-8-24
- Add support for layered deployment manifests when building, pushing and generating
- Add support for creating deployments in IoTHub via the new command: `iotedgedev iothub deploy`
- Add support for adding device tags via the new comand: `iotedgedev tag`

## [3.2.0] - 2021-7-30
- Added support for IoT Edge Runtime version 1.2
- Enable change of edgehub and edgeagent schema versions
- Added support for config generation, build and push off of a layered deployment manifest

## [3.1.0] - 2021-6-8
- Added support for IoT Edge Runtime version 1.1
- Enabled dynamic Edge runtime selection in CLI with -er flag

## [3.0.0] - 2021-01-27
- Remove support for Python2. Only Python 3.6 and 3.7 are currently supported.

## [2.2.0] - 2021-01-06
### Changed
- Remove explicit cryptography package install to resolve dependency conflicts so tests can run
- Add local registry support for Windows

## [2.1.6] - 2020-09-23
### Changed
- Fix warning about ConfigParser readfp deprecation

## [2.1.5] - 2020-08-18
### Changed
- Fix error caused by latest bcrypt on Azure Pipelines agent

## [2.1.4] - 2020-04-01
### Changed
- Fix configparser error from Azure Cli Core [[#426](https://github.com/Azure/iotedgedev/issues/426)]

## [2.1.3] - 2020-03-27
### Changed
- Fix genconfig does not fail when schema validation failed. [[#424](https://github.com/Azure/iotedgedev/issues/424)]

## [2.1.2] - 2020-01-14
### Changed
- Fix error when install on Azure Pipelines agent

## [2.1.1] - 2019-12-16
### Changed
- Fix getconfig fails if template contains a placeholder that is not enclosed in quotes.[[#414](https://github.com/Azure/iotedgedev/issues/414)]
- Fix wrong instruction to `iotedgedev iothub setup` with extra flags.[[#417](https://github.com/Azure/iotedgedev/issues/417)]
- Python 3.8 is not supported due to Azure CLI IoT extension issue [[#128](https://github.com/Azure/azure-iot-cli-extension/issues/128)]

## [2.1.0] - 2019-10-28
### Added
- Validate schema of deployment template and generated deployment manifest in `genconfig` command

### Changed
- Show progress info for docker commands

## [2.0.2] - 2019-07-31
### Changed
- Fix errors caused by latest lark-parser release.

## [2.0.1] - 2019-07-11
### Changed
- Fix build errors when some projects under modules folder have no module.json [[#396](https://github.com/Azure/iotedgedev/issues/396)]

## [2.0.0] - 2019-06-10
### Added
- Support relative path for module placeholder in deployment.template.json

### Changed
- Fix issue with 'cs' keyerror [[#387](https://github.com/Azure/iotedgedev/issues/387)]. Thanks for jporcenaluk's contribution.
- Drop support for ACTIVE_DOCKER_PLATFORMS environment variable

## [1.3.0] - 2019-04-25
### Added
- Add module twin support for simulator

### Changed
- Update azure-cli-core to fix module import error
- Fix applicationinsights incompatible version issue [[#383](https://github.com/Azure/iotedgedev/issues/383)]

## [1.2.0] - 2019-02-26
### Changed
- Fix issue creating C modules when temp folder and target project folder are on different disks [[#362](https://github.com/Azure/iotedgedev/pull/362)]
- Fix issue connecting to Docker daemon with `tlsverify` enabled [[#364](https://github.com/Azure/iotedgedev/pull/364)]
- Preserve tag cases when generating deployment manifests [[#372](https://github.com/Azure/iotedgedev/pull/372)]

## [1.1.0] - 2018-11-26
### Added
- Support parsing `createOptions` in JSON dictionary format
- Support multi-platform deployment manifest template, where modules' image placeholders are platform neutral (`${MODULE.filtermodule}` vs. `${MODULES.filtermodule.amd64}`). You can specify the platforms to build using the `--platform` parameter. By default, we provide "arm32v7", "amd64" and "windows-amd64" as the platform set since these are Azure IoT Edge supporting platforms today
- Add **deployment.debug.template.json** when creating new solutions. This template refers to the debug flavour image of the modules and has debug `createOptions` populated automatically. You can specify the deployment manifest template to build using the `--file` parameter

### Changed
- Default to JSON dictionary format for newly created modules' `createOptions`
- Show more clear message when failing to connect to Docker daemon

## [1.0.0] - 2018-11-01
### Added
- Support adding Java modules
- Support adding C modules
- Add OpenJDK and Maven to IoT Edge Dev Tool Container
- Add launch.json file for Python modules
- Add `registryCredentials` to deployment manifest template

### Changed
- Update .NET Core SDK in IoT Edge Dev Tool Container to version 2.1
- Improve Docker build and push command output to show more information
- Retry subscription prompt when multiple results are found
- Update launch.json file for C# modules to support .NET Core 2.1
- Fix misleading output when error deploying
- Fix error starting local registry with custom ports

## [0.82.0] - 2018-08-28
### Added
- New command to add modules to solution
- Support for adding and building Node.js and Python modules
- Integration with IoT Edge Simulator provided by the [iotedgehubdev CLI](https://pypi.org/project/iotedgehubdev/)
- Allow specifying name and template of the default module when creating new solutions
- Support for build options in `module.json` file
- Support for customized context path in `module.json` file
- Support for multiple registries in `.env` file
- Support for GA release of IoT Edge runtime in IoT Edge Dev Container
- Update `.vscode/launch.json` file when adding modules

### Changed
- Switch to Azure CLI IoT extension (>= 0.5.1) to monitor messages for Python >= 3.5 users
- Improve experience of creating Azure resources interactively
- Breaking changes (learn how to migrate [here](https://github.com/Azure/iotedgedev/wiki/migration-guides))
    - Updated command list and options
    - Updated logic to determine which module images to build
    - New module folder structure
    - Building code in Dockerfiles instead on building code natively

### Removed
- Support for `iotedgectl` and public preview runtime images

## [0.1.0] - 2017-12-29
### Added
- First release on PyPI.
