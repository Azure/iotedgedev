You can use the IoT Edge Dev Tool container to avoid having to install all the dependencies on your local dev machine. The only thing you need to install is Docker. All of the other dev dependencies are included in the container. Please see the [Quickstart](quickstart-with-IoT-Edge-Dev-Container) to learn more. 

To set up development machines manually instead of using the IoT Edge Dev Container, please see the [Manual Development Machine Setup Wiki](manual-Dev-Machine-Setup).

If you are using a separate Edge device, like a Raspberry Pi, you do not need to run all of these steps on your IoT Edge device, you can install and setup Edge runtime directly on the device. See the [Edge Device Setup](edge-device-setup) wiki page for more information on setting up your Edge device.

> Note: See the ["Test Coverage"](test-coverage) wiki page to see what the IoT Edge Dev Tool has been tested with.

1. **Initialize IoT Edge solution and setup Azure resources**

    `iotedgedev init`

    > `iotedgedev init` will run both `iotedgedev new .` and `iotedgedev iothub setup`, which will create a new solution and setup your Azure resources in a single command.
    
    > If you want to use your existing IoT Hub and IoT Edge device, you can run `iotedgedev new .`, and update the `.env` file with the IoT Hub connection string and IoT Edge device connection string.
    
    > `iotedgedev init` and `iotedgedev new .` will add a default C# module named `filtermodule` to the solution. To customize this behavior, append the parameters ` --module <module-name> --template <template>`.

1. **Add modules to IoT Edge solution**

    `iotedgedev add <module-name> --template <template>`
    
    > Currently the available template values are `c`, `csharp`, `java`, `nodejs`, `python`, `csharpfunction`. We are working on supporting more templates.

1. **Build IoT Edge module images**

    `sudo iotedgedev build`

    > You can avoid `sudo` if you are running IoT Edge Dev Tool outside Docker container, and:
    > * You are on Windows or macOS.
    > * You are on Linux, and you have followed the [post-installation steps for Linux](https://docs.docker.com/install/linux/linux-postinstall/#manage-docker-as-a-non-root-user) to allow running Docker commands without `sudo`.
 
1. **Setup the [IoT Edge Simulator]((https://pypi.org/project/iotedgehubdev/).)**

    `sudo iotedgedev setup`

    > IoT Edge Simulator does not support running Python and C modules yet. You'll need IoT Edge Runtime to run your Python and C modules.

    > You can avoid `sudo` if you are on Windows, and running IoT Edge Dev Tool outside Docker container.

1. **Start the IoT Edge Simulator to run the solution**

    `sudo iotedgedev start`

    > You can also combine setup and start with `sudo iotedgedev start --setup`

    > You can avoid `sudo` if you are running IoT Edge Dev Tool outside Docker container, and:
    > * You are on Windows or macOS.
    > * You are on Linux, and you have followed the [post-installation steps for Linux](https://docs.docker.com/install/linux/linux-postinstall/#manage-docker-as-a-non-root-user) to allow running Docker commands without `sudo`.

1. **Monitor messages sent from IoT Edge Simulator to IoT Hub**

    `iotedgedev monitor`

1. **Stop the IoT Edge Simulator**

    `sudo iotedgedev stop`

    > You can avoid `sudo` if you are running IoT Edge Dev Tool outside Docker container, and:
    > * You are on Windows or macOS.
    > * You are on Linux, and you have followed the [post-installation steps for Linux](https://docs.docker.com/install/linux/linux-postinstall/#manage-docker-as-a-non-root-user) to allow running Docker commands without `sudo`.

1. **Setup the IoT Edge Runtime**
    
    1. Copy the device connection string from the `DEVICE_CONNECTION_STRING` environment variable in the `.env` file, [Azure Portal](https://docs.microsoft.com/en-us/azure/iot-edge/how-to-register-device-portal#retrieve-the-connection-string), or [Azure CLI](https://docs.microsoft.com/en-us/azure/iot-edge/how-to-register-device-cli#retrieve-the-connection-string).
    1. Follow [Edge Device Setup](edge-device-setup) to setup and start the IoT Edge Runtime with the copied device connection string

1. **Push IoT Edge module images**

    `sudo iotedgedev push`

    > You can avoid `sudo` if you are running IoT Edge Dev Tool outside Docker container, and:
    > * You are on Windows or macOS.
    > * You are on Linux, and you have followed the [post-installation steps for Linux](https://docs.docker.com/install/linux/linux-postinstall/#manage-docker-as-a-non-root-user) to allow running Docker commands without `sudo`.

1. **Deploy modules to IoT Edge device**

    `iotedgedev deploy`
    > You can also combine push and deploy with `iotedgedev push --deploy`

1. **Monitor messages sent from IoT Edge Runtime to IoT Hub**

    `iotedgedev monitor`