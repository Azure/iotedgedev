The **Azure IoT Edge Dev Tool** enables you to do all of the following with simple one-line CLI commands.

1. **Start Container**:

    `docker run -it -v /var/run/docker.sock:/var/run/docker.sock -v c:/temp/iotedge:/home/iotedge microsoft/iotedgedev`

    This container includes all of the dependencies you need for IoT Edge development, including:

    - Docker
    - Python
    - Pip
    - Azure CLI
    - Git
    - .NET Core SDK
    - OpenJDK
    - Node.js
    - [C# module template](https://www.nuget.org/packages/Microsoft.Azure.IoT.Edge.Module/)
    - Maven (for scaffolding [Java modules](https://github.com/Microsoft/azure-maven-archetypes/tree/master/azure-iot-edge-archetype))
    - [Yeoman](http://yeoman.io/) and [Node.js module template](https://www.npmjs.com/package/generator-azure-iot-edge-module)
    - [Cookiecutter](https://cookiecutter.readthedocs.io/en/latest/) (for scaffolding [Python modules](https://github.com/Azure/cookiecutter-azure-iot-edge-module))
    - [C# Functions module template](https://www.nuget.org/packages/Microsoft.Azure.IoT.Edge.Function/)

    You can also directly install with: `pip install iotedgedev`
    
1. **Create Solution**: Create a new IoT Edge Solution that includes a sample module and all the the required configuration files.

    ```
    iotedgedev new edgesolution`
    cd edgesolution
    ```

1. **Setup Azure**: Creates or selects your Azure IoT Hub and Edge Device and updates your Environment Variables.

    `iotedgedev iothub setup`

    > This must be run from the root of your solution, so make sure you cd into the `edgesolution1` folder before you run this command.

1. **Build, Push & Deploy**: Build, Push and Deploy modules:

    `iotedgedev push --deploy`
    
    > This will run `iotedgedev build`, `iotedgedev push`, and `iotedgedev deploy` on deployment.template.json targeting amd64 platform. You can use the `--file` and `--platform` parameters to change this behavior.

    If your module is included in the `BYPASS_MODULES` environment variable, or not included in the deployment manifest template, then the `iotedgedev build` and `iotedgedev push` steps will be skipped.
    
1. **Setup**: Setup the IoT Edge Simulator (provided by the [iotedgehubdev](https://pypi.org/project/iotedgehubdev/) tool):

    `iotedgedev setup`

1. **Start**: Start IoT Edge Simulator:

    `iotedgedev start -f config/deployment.amd64.json`

1. **View Messages**: View Messages Sent from IoT Edge to IoT Hub:

    `iotedgedev monitor`

1. **View Logs**: View and Save Docker log files:

    `iotedgedev docker log`

1. **Setup Custom Registry**: Use a Custom Container Registry:

    `iotedgedev docker setup-registry`

Please see [Azure IoT Edge Dev Resources](https://github.com/Azure/iotedgedev) for links to official docs and other IoT Edge dev information.