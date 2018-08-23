# Changelog
All notable changes to this project since 1.0.0 will be documented in this file.

## [1.0.0] - 2017-08-23
### Added
- New command to add modules to solution
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
- Breaking changes (learn how to migrate [here](https://github.com/LazarusX/iotedgedev/wiki/migration-guides))
    - Updated command list and options
    - Updated logic to determine which module images to build
    - New module folder structure
    - Building code in Dockerfiles instead on building code natively

### Removed
- Support for `iotedgectl` and public preview runtime images