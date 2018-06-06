# Azure IoT Edge Dev Tool

The **Azure IoT Edge Dev Tool** greatly simplifies [Azure IoT Edge](https:/azure.microsoft.com/en-us/services/iot-edge/) development down to simple commands driven by Environment Variables. 

 - It gets you started with IoT Edge development with the [IoT Edge Dev Container](#iot-edge-dev-container) and IoT Edge Solution Scaffolding that contains a sample module and all the required configuration files.
 - It speeds up your inner-loop dev (dev, debug, test) by reducing multi-step build & deploy processes into one-line CLI commands and well as drive your outer-loop CI/CD pipeline. _You can use all the same commands in both stages of your development life-cycle._

## Resources
Please refer to the [Wiki](https://github.com/Azure/iotedgedev/wiki) for details on setup, usage, and troubleshooting.

Please refer to the [Contributing file](CONTRIBUTING.MD) for details on contributing changes.
 
## Quickstart
Here is the absolute fastest way to get started with IoT Edge Dev. This quickstart will run a container, create a solution, setup Azure resources, build and deploy modules to your device, setup and start the Edge Runtime and then monitor messages flowing into IoT Hub.

Here's a 3 minute video walk-through of this Quickstart:

[![Azure IoT Edge Dev Tool: Quickstart](assets/edgedevtoolquickstartsmall.png)](https://aka.ms/iotedgedevquickstart)

The only thing you need to install is Docker. All of the other dev dependencies are included in the container. 

1. **Install [Docker](https://docs.docker.com/engine/installation/)**

    - Open Docker Settings and setup a Shared Drive that you'll use to store your IoT Edge Solution files.

1. **Run the Azure IoT Edge Dev Container**

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

1. **Initialize Edge Solution and Setup Azure Resources**

    `iotedgedev init`

    > 'iotedgedev init' will run both 'iotedgedev solution .' and 'iotedgedev azure', which will create a solution and setup your Azure resource in a single comamnd.

1. **Build & Push IoT Edge Modules**

    `iotedgedev push`

    > You can also combine build, push and deploy with `iotedgedev push --deploy`

1. **Deploy Modules to IoT Edge Device**

    `iotedgedev deploy`
    
1. **Start the IoT Edge Runtime**

    `iotedgedev start`

1. **Monitor Messages sent from IoT Edge to IoT Hub**

    `iotedgedev monitor`

## Overview
The **Azure IoT Edge Dev Tool** enables you to do all of the following with simple one-line CLI commands.

1. **Start Container**: 

    `docker run -it -v /var/run/docker.sock:/var/run/docker.sock -v c:/temp/iotedge:/home/iotedge microsoft/iotedgedev`

    This container includes all of the dependencies you need for IoT Edge development, including:

    - Docker
    - .NET Core SDK
    - Python
    - Pip
    - Azure CLI

    You can also directly install with: `pip install iotedgedev`   
    
1. **Create Solution**: Create a new IoT Edge Solution that includes a sample module and all the the required configuration files.

    `iotedgedev solution edgesolution1`

    `cd edgesolution1`

1. **Setup Azure**: Creates or selects your Azure IoT Hub and Edge Device and updates your Environment Variables.

    `iotedgedev azure`

    > This must be run from the root of your solution, so make sure you cd into the `edgesolution1` folder before you run this command.

1. **Build, Push & Deploy**: Build, Push and Deploy modules: 

    `iotedgedev push --deploy`
    
    > This will `dotnet build`, `publish`, `docker build, tag and push` and `deploy modules` to your IoT Edge device.

    If your module is not dotnet, then the dotnet build/publish steps will be skipped.
    
1. **Setup & Start**: Setup and Start the IoT Edge Runtime: 

    `iotedgedev start`

1. **View Messages**: View Messages Sent from IoT Edge to IoT Hub: 

    `iotedgedev monitor`

1. **View Logs**: View and Save Docker log files: 

    `iotedgedev docker --logs`

1. **Setup Custom Registry**: Use a Custom Container Registry: 

    `iotedgedev docker --setup-registry`

Please see [Azure IoT Edge Dev Resources](https://github.com/jonbgallant/azure-iot-edge-dev) for links to official docs and other IoT Edge dev information.