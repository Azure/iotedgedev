# Changelog
All notable changes to this project since 0.82.0 will be documented in this file.

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