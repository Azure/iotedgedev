# Azure IoT Edge Dev Tool

[![PyPI version](https://badge.fury.io/py/iotedgedev.svg)](https://badge.fury.io/py/iotedgedev)
[![Travis Build Status](https://travis-ci.org/Azure/iotedgedev.svg?branch=master)](https://travis-ci.org/Azure/iotedgedev)
[![Build Status](https://dev.azure.com/mseng/VSIoT/_apis/build/status/iotedgedev-master-ci?branchName=master)](https://dev.azure.com/mseng/VSIoT/_build/latest?definitionId=7884?branchName=master)

The **IoT Edge Dev Tool** greatly simplifies [Azure IoT Edge](https://azure.microsoft.com/en-us/services/iot-edge/) development down to simple commands driven by environment variables.

 - It gets you started with IoT Edge development with the [IoT Edge Dev Container](https://hub.docker.com/r/microsoft/iotedgedev/) and IoT Edge solution scaffolding that contains a default module and all the required configuration files.
 - It speeds up your inner-loop dev (dev, debug, test) by reducing multi-step build & deploy processes into one-line CLI commands as well as drives your outer-loop CI/CD pipeline. _You can use all the same commands in both stages of your development life-cycle._

## Overview
For the absolute fastest way to get started with IoT Edge Dev, please see the [Quickstart](#quickstart) section below.

For a more detailed overview of IoT Edge Dev Tool including setup and commands, please see the [Wiki](https://github.com/Azure/iotedgedev/wiki).

## Quickstart

> To set up development machines manually instead of using the IoT Edge Dev Container, please see the [Manual Development Machine Setup Wiki](https://github.com/Azure/iotedgedev/wiki/manual-dev-machine-setup).

This quickstart will run a container, create a solution, setup Azure resources, build and deploy modules to your device, setup and start the IoT Edge simulator, monitor messages flowing into IoT Hub, and finally deploy to the IoT Edge runtime.

<!-- Here's a 3 minute video walk-through of this Quickstart:

[![Azure IoT Edge Dev Tool: Quickstart](assets/edgedevtoolquickstartsmall.png)](https://aka.ms/iotedgedevquickstart) -->

The only thing you need to install is Docker. All of the other dev dependencies are included in the container. 

1. **Install [Docker CE](https://docs.docker.com/install/)**

    - For Windows, please follow [the document](https://docs.docker.com/docker-for-windows/#shared-drives) to open Docker Settings and setup a Shared Drive.
    - For macOS, please follow [the document](https://docs.docker.com/docker-for-mac/#file-sharing) to choose local directories to share with your containers.
    
    Note: If the device is behind the proxy server, you can set the [proxy manually](https://docs.docker.com/network/proxy/#configure-the-docker-client) 

1. **Run the IoT Edge Dev Container**

    Before you run the container, you will need to create a local folder to store your IoT Edge solution files.
    
    **Windows**
    ```
    mkdir c:\temp\iotedge
    docker run -ti -v /var/run/docker.sock:/var/run/docker.sock -v c:/temp/iotedge:/home/iotedge mcr.microsoft.com/iotedge/iotedgedev
    ```

    **Linux**
    ```
    sudo mkdir /home/iotedge
    sudo docker run -ti -v /var/run/docker.sock:/var/run/docker.sock -v ~/iotedge:/home/iotedge mcr.microsoft.com/iotedge/iotedgedev
    ```

    **macOS**
    ```
    mkdir ~/iotedge
    docker run -ti -v /var/run/docker.sock:/var/run/docker.sock -v ~/iotedge:/home/iotedge mcr.microsoft.com/iotedge/iotedgedev
    ```

1. **Initialize IoT Edge solution and setup Azure resources**

    `iotedgedev init`

    > `iotedgedev init` will create a solution and setup your Azure IoT Hub in a single command. The solution comes with a default C# module named `filtermodule`.

    <details>
    <summary>More information</summary>

    1. You will see structure of current folder like below:

    ```
        │  .env
        │  .gitignore
        │  deployment.debug.template.json
        │  deployment.template.json
        │
        ├─.vscode
        │      launch.json
        │
        └─modules
            └─filtermodule
                │  .gitignore
                │  Dockerfile.amd64
                │  Dockerfile.amd64.debug
                │  Dockerfile.arm32v7
                │  Dockerfile.windows-amd64
                │  filtermodule.csproj
                │  module.json
                │  Program.cs
    ```

    2. Open `.env` file, you will see the `IOTHUB_CONNECTION_STRING` and `DEVICE_CONNECTION_STRING` environment variables filled correctly.
    3. Open `deployment.template.json` file   
        1. You will see below section in the modules section:

        ```
        "filtermodule": {
            "version": "1.0",
            "type": "docker",
            "status": "running",
            "restartPolicy": "always",
            "settings": {
                "image": "${MODULES.filtermodule}",
                "createOptions": {}
            }
        }
        ```

        2. Two default routes are added:
        
        ```
        "routes": {
            "sensorTofiltermodule": "FROM /messages/modules/tempSensor/outputs/temperatureOutput INTO BrokeredEndpoint(\"/modules/filtermodule/inputs/input1\")",
            "filtermoduleToIoTHub": "FROM /messages/modules/filtermodule/outputs/* INTO $upstream"
        }
        ```

    4. You will see privacy statement like below:

        ```
        Welcome to iotedgedev!
        -------------------------
        Telemetry
        ---------
        The iotedgedev collects usage data in order to improve your experience.
        The data is anonymous and does not include commandline argument values.
        The data is collected by Microsoft.
        
        You can change your telemetry settings by updating 'collect_telemetry' to 'no' in ~/.iotedgedev/setting.ini
        ```

    </details>

1. **Build IoT Edge module images**

    `sudo iotedgedev build`
    
    > This step will build user modules in deployment.template.json targeting amd64 platform.

    <details>
    <summary>More information</summary>

    1. You will see a "BUILD COMPLETE" for each module and no error messages in the terminal output.
    1. Open `config/deployment.amd64.json` file, you will see the module image placeholders expanded correctly.
    1. Run `sudo docker image ls`, you will see the module images you just built.

    </details>

1. **Setup and start the IoT Edge Simulator to run the solution**

    `sudo iotedgedev start --setup --file config/deployment.amd64.json`

    <details>
    <summary>More information</summary>

    1. You will see an "IoT Edge Simulator has been started in solution mode." message at the end of the terminal output
    2. Run `sudo docker ps`, you will see your modules running as well as an edgeHubDev container

    </details>

1. **Monitor messages sent from IoT Edge Simulator to IoT Hub**

    `iotedgedev monitor`

    <details>
    <summary>More information</summary>

    1. You will see your expected messages sending to IoT Hub
    2. Stopping the monitor doesn't stop the simulator. It will continue running until it is explicitely stopped using `iotedgedev stop` and at that time all containers used by the simulator will be cleaned up.

    </details>

1. **Docker containers/images management**
    1. The containers used by the simulator will be cleaned up when the simulator stops running `iotedgedev stop`
    2. All remaining containers can be cleaned up using `iotedgedev docker clean -c`
    3. All remaining images can be cleaned up using `iotedgedev docker clean -i`

## Resources
Please refer to the [Wiki](https://github.com/Azure/iotedgedev/wiki) for details on setup, usage, and troubleshooting.

## Data/Telemetry
This project collects usage data and sends it to Microsoft to help improve our products and services. Read our [privacy statement](http://go.microsoft.com/fwlink/?LinkId=521839) to learn more. 
If you don’t wish to send usage data to Microsoft, you can change your telemetry settings by updating `collect_telemetry` to `no` in `~/.iotedgedev/settings.ini`.

## Contributing
This project welcomes contributions and suggestions. Please refer to the [Contributing file](CONTRIBUTING.md) for details on contributing changes.

Most contributions require you to agree to a Contributor License Agreement (CLA) declaring that you have the right to,
and actually do, grant us the rights to use your contribution. For details, visit
https://cla.microsoft.com.

When you submit a pull request, a CLA-bot will automatically determine whether you need
to provide a CLA and decorate the PR appropriately (e.g., label, comment). Simply follow the
instructions provided by the bot. You will only need to do this once across all repositories using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/)
or contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.
