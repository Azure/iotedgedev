# Quickstart

This quickstart will run a container, create a solution, setup Azure resources, build and deploy modules to your device, setup and start the IoT Edge simulator, monitor messages flowing into IoT Hub, and finally deploy to the IoT Edge runtime.

At the end of this quickstart, you should have the following:

- Development environment.
- IoT Hub deployed in your Azure subscription.
- A directory with the [IoT edge deployment manifest](https://docs.microsoft.com/en-us/azure/iot-edge/module-composition?view=iotedge-2020-11), [.env file](.env.tmp) with the environment variables needed for the `iotedgedev` tool, and the source file of a custom IoT edge module (`filtermodule`).
- The docker image of the `filtermodule`.
- Deploying the IoT edge modules defined in the manifest on a VM or IoT Edge simulator.
- Monitoring the messages sent to the IoT Hub.
- Cleaning up the docker containers and images.

## Pre-requisites

- Docker (see [Install Docker docs](environment-setup/install-docker) for details) and add user to `docker` Unix group (see [documentation](https://docs.docker.com/engine/install/linux-postinstall/)).

## Quickstart steps

1. Setup your environment

    There are three options to setup your environment:

    - Setup the development environment manually. Please follow the [Manual Development Machine Setup Wiki](environment-setup/manual-dev-machine-setup.md).
    - Starting the devcontainer in VS Code (see [Developing inside a Container](https://code.visualstudio.com/docs/remote/containers) for steps on how to do so).
    - Starting the devcontainer with Docker. Please follow the [Run the IoT Edge Dev Container with Docker docs](environment-setup/run-devcontainer-docker.md).

1. Initialize IoT Edge solution and setup Azure resources.

    ```sh
    iotedgedev init <foldername>
    ```

    > `iotedgedev init` will create a solution in a new folder and setup your Azure IoT Hub in a single command. The solution comes with a default C# module named `filtermodule`.

    <details>
    <summary>More information</summary>

    1. You will see structure of current folder like below:

    ```tree
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

    1. Open `.env` file, you will see the `IOTHUB_CONNECTION_STRING` and `DEVICE_CONNECTION_STRING` environment variables filled correctly.
    2. Open `deployment.template.json` file.
        1. You will see below section in the modules section:

        ```json
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

        1. Two default routes are added:

        ```json
        "routes": {
            "sensorTofiltermodule": "FROM /messages/modules/tempSensor/outputs/temperatureOutput INTO BrokeredEndpoint(\"/modules/filtermodule/inputs/input1\")",
            "filtermoduleToIoTHub": "FROM /messages/modules/filtermodule/outputs/* INTO $upstream"
        }
        ```

    3. You will see privacy statement like below:

        ```txt
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

3. Build IoT Edge module images.

    ```sh
    iotedgedev build
    ```

    > This step will build user modules in deployment.template.json targeting amd64 platform.

    <details>
    <summary>More information</summary>

    1. You will see a "BUILD COMPLETE" for each module and no error messages in the terminal output.
    2. Open `config/deployment.amd64.json` file, you will see the module image placeholders expanded correctly.
    3. Run `sudo docker image ls`, you will see the module images you just built.

    </details>

4. Run IoT Edge modules.

    Edge modules can be started in two different ways using `iotedgedev`:

    - Deploying them on a VM; please find the steps to do so in [Set up and start modules on a virtual machine](run-modules-on-vm);
    - or in your own development machine using the `iotedgedev` simulator; please follow [Set up and start the IoT Edge Simulator](run-modules-on-simulator).

5. Monitor messages sent from device to IoT Hub.

    ```sh
    iotedgedev monitor
    ```

    <details>
    <summary>More information</summary>

    1. You will see your expected messages sending to IoT Hub
    2. Stopping the monitor doesn't stop the simulator. It will continue running until it is explicitely stopped using `iotedgedev stop` and at that time all containers used by the simulator will be cleaned up.

    </details>

6. Stop docker containers and remove images.

    ```sh
    # stop containers started by the simulator
    iotedgedev stop
    # remove stopped containers
    iotedgedev docker clean -c
    # remove docker images
    iotedgedev docker clean -
    ```
