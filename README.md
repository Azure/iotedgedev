# Azure IoT Edge Dev Tool

[![PyPI version](https://badge.fury.io/py/iotedgedev.svg)](https://badge.fury.io/py/iotedgedev)
[![Build Status](https://dev.azure.com/Azure-IoT-DDE-EdgeExperience/IoTEdgeDev/_apis/build/status/Azure.iotedgedev?branchName=main)](https://dev.azure.com/Azure-IoT-DDE-EdgeExperience/IoTEdgeDev/_build/latest?definitionId=35&branchName=main)

The **IoT Edge Dev Tool** greatly simplifies [Azure IoT Edge](https://azure.microsoft.com/en-us/services/iot-edge/) development down to simple commands driven by environment variables.

- It gets you started with IoT Edge development with the [IoT Edge Dev Container](https://hub.docker.com/r/microsoft/iotedgedev/) and IoT Edge solution scaffolding that contains a default module and all the required configuration files.
- It speeds up your inner-loop dev (dev, debug, test) by reducing multi-step build & deploy processes into one-line CLI commands as well as drives your outer-loop CI/CD pipeline. _You can use all the same commands in both stages of your development life-cycle._

## Overview

For the absolute fastest way to get started with IoT Edge Dev, please see the [Quickstart](https://github.com/Azure/iotedgedev/wiki/quickstart) section below.

For a more detailed overview of IoT Edge Dev Tool including setup, commands and troubleshooting, please see the [Wiki](https://github.com/Azure/iotedgedev/wiki).

## Data/Telemetry

This project collects usage data and sends it to Microsoft to help improve our products and services. Read our [privacy statement](http://go.microsoft.com/fwlink/?LinkId=521839) to learn more.
If you don’t wish to send usage data to Microsoft, you can change your telemetry settings by updating `collect_telemetry` to `no` in `~/.iotedgedev/settings.ini`.

## Contributing

This project welcomes contributions and suggestions. Please refer to the [Contributing file](CONTRIBUTING.md) for details on contributing changes.

Most contributions require you to agree to a Contributor License Agreement (CLA) declaring that you have the right to,
and actually do, grant us the rights to use your contribution. For details, visit
<https://cla.microsoft.com>.

When you submit a pull request, a CLA-bot will automatically determine whether you need
to provide a CLA and decorate the PR appropriately (e.g., label, comment). Simply follow the
instructions provided by the bot. You will only need to do this once across all repositories using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/)
or contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.

## Support

The team monitors the issue section on regular basis and will try to assist with troubleshooting or questions related IoT Edge tools on a best effort basis.

A few tips before opening an issue. Try to generalize the problem as much as possible. Examples include

- Removing 3rd party components
- Reproduce the issue with provided deployment manifest used
- Specify whether issue is reproducible on physical device or simulated device or both
Also, Consider consulting on the [docker docs channel](https://github.com/docker/docker.github.io) for general docker questions.
