# Quickstart

> To set up development machines manually instead of using the IoT Edge Dev Container, please see the [Manual Development Machine Setup Wiki](https://github.com/Azure/iotedgedev/wiki/manual-dev-machine-setup).

This quickstart will run a container, create a solution, setup Azure resources, build and deploy modules to your device, setup and start the IoT Edge simulator, monitor messages flowing into IoT Hub, and finally deploy to the IoT Edge runtime.

Using IoT Edge Dev Container is the absolute fastest way to get IoT Edge Dev Tool (aka `iotedgedev`) running on your dev machine.

You can use the IoT Edge Dev Tool container to avoid having to install all the dependencies on your local dev machine. The only thing you need to install is Docker. All of the other dev dependencies are included in the container.

<!-- Here's a 3 minute video walk-through of this Quickstart:

[![Azure IoT Edge Dev Tool: Quickstart](assets/edgedevtoolquickstartsmall.png)](https://aka.ms/iotedgedevquickstart) -->

The only thing you need to install is Docker. All of the other dev dependencies are included in the container.

1. **Install [Docker CE](https://docs.docker.com/install/)**

    - For Windows, please follow [the document](https://docs.docker.com/docker-for-windows/#shared-drives) to open Docker Settings and setup a Shared Drive.
    - For macOS, please follow [the document](https://docs.docker.com/docker-for-mac/#file-sharing) to choose local directories to share with your containers.

    Note: If the device is behind the proxy server, you can set the [proxy manually](https://docs.docker.com/network/proxy/#configure-the-docker-client)

2. **Run the IoT Edge Dev Container**

    Before you run the container, you will need to create a local folder to store your IoT Edge solution files.

    **Windows**

    ```sh
    mkdir c:\temp\iotedge
    docker run -ti -v /var/run/docker.sock:/var/run/docker.sock -v c:/temp/iotedge:/home/iotedge mcr.microsoft.com/iotedge/iotedgedev
    ```

    **Linux**

    ```sh
    sudo mkdir /home/iotedge
    sudo docker run -ti -v /var/run/docker.sock:/var/run/docker.sock -v ~/iotedge:/home/iotedge mcr.microsoft.com/iotedge/iotedgedev
    ```

    **macOS**

    ```sh
    mkdir ~/iotedge
    docker run -ti -v /var/run/docker.sock:/var/run/docker.sock -v ~/iotedge:/home/iotedge mcr.microsoft.com/iotedge/iotedgedev
    ```

## Set up solution

1. **Initialize IoT Edge solution and setup Azure resources**

    `iotedgedev init`

    > `iotedgedev init` will create a solution and setup your Azure IoT Hub in a single command. The solution comes with a default C# module named `filtermodule`.

    <details>
    <summary>More information</summary>

    1. You will see structure of current folder like below:

        ```text
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

        2. Two default routes are added:

            ```json
            "routes": {
                "sensorTofiltermodule": "FROM /messages/modules/tempSensor/outputs/temperatureOutput INTO BrokeredEndpoint(\"/modules/filtermodule/inputs/input1\")",
                "filtermoduleToIoTHub": "FROM /messages/modules/filtermodule/outputs/* INTO $upstream"
            }
            ```

    4. You will see privacy statement like below:

        ```text
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

2. **Build IoT Edge module images**

    `sudo iotedgedev build`

    > This step will build user modules in deployment.template.json targeting amd64 platform.

    <details>
    <summary>More information</summary>

    1. You will see a "BUILD COMPLETE" for each module and no error messages in the terminal output.
    1. Open `config/deployment.amd64.json` file, you will see the module image placeholders expanded correctly.
    1. Run `sudo docker image ls`, you will see the module images you just built.

    </details>

### Run Edge modules

#### Set up and start modules on a virtual machine

1. [**Set up virtual machine to run Azure IoT Edge**](https://docs.microsoft.com/en-us/azure/iot-edge/how-to-install-iot-edge-ubuntuvm)
2. **Create and configure an ACR (Azure Container Registry)**
   1. [Create an Azure Container Registry](https://docs.microsoft.com/en-us/azure/container-registry/container-registry-get-started-portal)
   2. Configure `.env` that was generated in the `iotedgedev init` step with the ACR by modifying these lines with appropriate values:

       ```sh
       CONTAINER_REGISTRY_SERVER="localhost:5000"
       CONTAINER_REGISTRY_USERNAME=""
       CONTAINER_REGISTRY_PASSWORD=""
       ```

3. **Push modules to ACR with**

    `iotedgedev push`

4. **Add registry credentials to deployment manifest**

    1. Replace generated `deployment.template.json` field `registryCredentials` with

        ```json
        "registryCredentials": {
              "privateAcr": {
                "username": "$CONTAINER_REGISTRY_USERNAME",
                "password": "$CONTAINER_REGISTRY_PASSWORD",
                "address": "$CONTAINER_REGISTRY_SERVER"
              }
            }
        ```

        > Note: `privateAcr` can be renamed to anything else
    2. Regenerate the `config/deployment.amd64.json`

        `iotedgedev genconfig`

5. **Deploy modules to device**

    `iotedgedev solution deploy`

6. **Monitor messages sent from the virtual machine to IoT Hub**

    `iotedgedev monitor`

7. **Troubleshooting**

    - Verify modules deployment status via executing:

        ```bash
        # Populate variables from .env
        edge_device_id=$(dotenv get DEVICE_CONNECTION_STRING |  grep -oP '(?<=DeviceId=).*(?=;Shared)')
        iot_hub_connection_string=$(dotenv get IOTHUB_CONNECTION_STRING)
        # Execute query
        az iot hub module-identity list --device-id $edge_device_id --login $iot_hub_connection_string
        ```

    - [Troubleshoot IoT Edge devices from the Azure portal](https://docs.microsoft.com/en-us/azure/iot-edge/troubleshoot-in-portal)
    - SSH into the virtual machine and follow [troubleshoot your IoT Edge device](https://docs.microsoft.com/en-us/azure/iot-edge/troubleshoot)

#### Set up and start the IoT Edge Simulator

1. **Setup and start the IoT Edge Simulator to run the solution**

    `sudo iotedgedev start --setup --file config/deployment.amd64.json`

    <details>
    <summary>More information</summary>

    1. You will see an "IoT Edge Simulator has been started in solution mode." message at the end of the terminal output
    2. Run `sudo docker ps`, you will see your modules running as well as an edgeHubDev container

    </details>

2. **Monitor messages sent from IoT Edge Simulator to IoT Hub**

    `iotedgedev monitor`
    <details>
    <summary>More information</summary>

    1. You will see your expected messages sending to IoT Hub
    2. Stopping the monitor doesn't stop the simulator. It will continue running until it is explicitly stopped using `iotedgedev stop` and at that time all containers used by the simulator will be cleaned up.

    </details>

3. **Docker containers/images management**
    1. The containers used by the simulator will be cleaned up when the simulator stops running `iotedgedev stop`
    2. All remaining containers can be cleaned up using `iotedgedev docker clean -c`
    3. All remaining images can be cleaned up using `iotedgedev docker clean -i`
