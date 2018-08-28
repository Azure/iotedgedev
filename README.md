# Azure IoT Edge Dev Tool

[![Travis Build Status](https://travis-ci.org/Azure/iotedgedev.svg?branch=master)](https://travis-ci.org/Azure/iotedgedev)
[![VSTS Build Status](https://iotedgedev.visualstudio.com/iotedgedev-main/_apis/build/status/iotedgedev-master-ci)](https://iotedgedev.visualstudio.com/iotedgedev-main/_build/latest?definitionId=6)

The **IoT Edge Dev Tool** greatly simplifies [Azure IoT Edge](https:/azure.microsoft.com/en-us/services/iot-edge/) development down to simple commands driven by environment variables.

 - It gets you started with IoT Edge development with the [IoT Edge Dev Container](quickstart) and IoT Edge solution scaffolding that contains a default module and all the required configuration files.
 - It speeds up your inner-loop dev (dev, debug, test) by reducing multi-step build & deploy processes into one-line CLI commands as well as drives your outer-loop CI/CD pipeline. _You can use all the same commands in both stages of your development life-cycle._

## Overview
For the absolute fastest way to get started with IoT Edge Dev, please see the [Quickstart](#quickstart) section below.

For a more detailed overview of IoT Edge Dev Tool including setup and commands, please see the [Wiki](https://github.com/Azure/iotedgedev/wiki).

## Quickstart
This quickstart will run a container, create a solution, setup Azure resources, build and deploy modules to your device, setup and start the Edge simulator and then monitor messages flowing into IoT Hub.

Here's a 3 minute video walk-through of this Quickstart:

[![Azure IoT Edge Dev Tool: Quickstart](assets/edgedevtoolquickstartsmall.png)](https://aka.ms/iotedgedevquickstart)

The only thing you need to install is Docker. All of the other dev dependencies are included in the container. 

1. **Install [Docker](https://docs.docker.com/engine/installation/)**

    - Open Docker Settings and setup a Shared Drive that you'll use to store your IoT Edge Solution files.
    - Windows    
        - Be sure to check whether you are running in Linux container mode or Windows container mode.
    - Linux
        - We've seen some issues with docker.io. If Edge doesn't run for you, then try installing Docker CE directly instead of via docker.io. Use the [CE install steps](https://docs.docker.com/engine/installation/linux/docker-ce/ubuntu/#install-docker-ce), or use the [convenience script](https://docs.docker.com/engine/installation/linux/docker-ce/ubuntu/#install-using-the-convenience-script).
        - By default, you need `sudo` to run `docker` commands. If you want to avoid this, please follow the [post-installation steps for Linux](https://docs.docker.com/install/linux/linux-postinstall/#manage-docker-as-a-non-root-user).

1. **Run the IoT Edge Dev Container**

    Before you run the container, you will need to create a local folder to store your IoT Edge solution files.
    
    **Windows**
    ```
    mkdir c:\temp\iotedge
    docker run -ti -v /var/run/docker.sock:/var/run/docker.sock -v c:/temp/iotedge:/home/iotedge microsoft/iotedgedev
    ```

    **Linux**
    ```
    sudo mkdir /home/iotedge
    docker run -ti -v /var/run/docker.sock:/var/run/docker.sock -v /home/iotedge:/home/iotedge microsoft/iotedgedev
    ```

1. **Initialize IoT Edge solution and setup Azure resources**

    `iotedgedev init`

    > `iotedgedev init` will run both `iotedgedev new .` and `iotedgedev iothub setup`, which will create a new solution and setup your Azure resources in a single command.
    
    > If you want to use your existing IoT Hub and IoT Edge device, you can run `iotedgedev new .`, and update the `.env` file with the IoT Hub connection string and IoT Edge device connection string. `iotedgedev new .` will add a default C# `filtermodule` to the solution. To customize this behavior, use `iotedgedev new . --module <module-name> --template <template>`

1. **Add modules to IoT Edge solution**

    `iotedgedev add <module-name> --template <template>`
    
    > Currently the available template values are `csharp`, `nodejs`, `python`, `csharpfunction`. We are working on supporting more templates.

1. **Build IoT Edge module images**

    `iotedgedev build`
 
1. **Setup the [IoT Edge Simulator]((https://pypi.org/project/iotedgehubdev/).)**

    `iotedgedev setup`

1. **Start the IoT Edge Simulator to run the solution**

    `iotedgedev start`
    > You can also combine setup and start with `iotedgedev start --setup`

1. **Monitor messages sent from IoT Edge Simulator to IoT Hub**

    `iotedgedev monitor`

1. **Stop the IoT Edge Simulator**

    `iotedgedev stop`

1. **Push IoT Edge module images**

    `iotedgedev push`

1. **Deploy modules to IoT Edge device**

    `iotedgedev deploy`
    > You can also combine push and deploy with `iotedgedev push --deploy`

1. **Monitor messages sent from IoT Edge Runtime to IoT Hub**

    `iotedgedev monitor`
## Resources
Please refer to the [Wiki](https://github.com/Azure/iotedgedev/wiki) for details on setup, usage, and troubleshooting.

Please refer to the [Contributing file](CONTRIBUTING.md) for details on contributing changes.
