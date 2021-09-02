Here is the absolute fastest way to get IoT Edge Dev Tool (aka `iotedgedev`) running on your dev machine with the IoT Edge Dev Container.

You can use the IoT Edge Dev Tool container to avoid having to install all the dependencies on your local dev machine. The only thing you need to install is Docker. All of the other dev dependencies are included in the container. 

1. **Install [Docker CE](https://docs.docker.com/install/)**

    - For Windows, please follow [the document](https://docs.docker.com/docker-for-windows/#shared-drives) to open Docker Settings and setup a Shared Drive.
    - For macOS, please follow [the document](https://docs.docker.com/docker-for-mac/#file-sharing) to choose local directories to share with your containers.


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
    sudo docker run -ti -v /var/run/docker.sock:/var/run/docker.sock -v ~/iotedge:/home/iotedge microsoft/iotedgedev
    ```

    **macOS**
    ```
    mkdir ~/iotedge
    docker run -ti -v /var/run/docker.sock:/var/run/docker.sock -v ~/iotedge:/home/iotedge microsoft/iotedgedev
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
                "createOptions": ""
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

    > This step will build user modules in deployment.template.json targeting amd64 platform. You can use the `--file` and `--platform` parameters to change this behavior.

    <details>
    <summary>More information</summary>

    1. You will see a "BUILD COMPLETE" for each module and no error messages in the terminal output.
	2. Open `config/deployment.amd64.json` file, you will see the module image placeholders expanded correctly.
    3. Run `sudo docker image ls`, you will see the module images you just built.

    </details>

1. **Setup and start the IoT Edge Simulator to run the solution**

    `sudo iotedgedev start --setup --file config/deployment.amd64.json`

    > IoT Edge Simulator does not support running Python and C modules yet. You'll need IoT Edge Runtime to run your Python and C modules.

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

    </details>
