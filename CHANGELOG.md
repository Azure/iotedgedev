# Changelog
All notable changes to this project since 0.82.0 will be documented in this file.

## [1.2.0] - 2019-02-25
### Changed
- Fix issue creating C modules when temp folder and target project folder are on different disks
- Fix issue connecting to Docker daemon with `tlsverify` enabled
- Preserve tag cases when generating deployment manifests

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