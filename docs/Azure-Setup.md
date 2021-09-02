#### Automated Setup

The following will show you how to setup your Azure Resources via the CLI instead of using the Portal.

First, create a solution with the following command:

`iotedgedev new edgesolution1`

Then, `cd` into that solution:

`cd edgesolution`

Then, run the `iotedgedev iothub setup` command to setup your Azure Resources. This command will bring you through a series of prompts to create Azure Resources and retrieve your IoT Hub and Edge Device connection strings and save them to the `.env` file in the root of the project. All subsequent commands will use those environment variables.

Here are all the `iotedgedev iothub setup` command options:

> You can override all of these parameters with environment variables. Please see the .env file in your solution for details.

```
iotedgedev iothub setup
    --credentials USERNAME PASSWORD
    --service-principal USERNAME PASSWORD TENANT
    --subscription THE_SUBSCRIPTION_ID 
    --resource-group-location THE_RG_LOCATION
    --resource-group-name THE_RG_NAME 
    --iothub-sku THE_IOT_SKU 
    --iothub-name THE_IOT_NAME 
    --edge-device-id THE_EDGE_DEVICE_NAME
    --update-dotenv
```

You can use the following `az cli` command to create a service principal:

```
az ad sp create-for-rbac -n "iotedgedev01"
```

> Note: Running `iotedgedev iothub setup` without any other parameters will save you time from looking up the required parameter values. The command will help you choose the parameters in an interactive way.

Alternatively, you can deploy the IoT Hub **and** Container Registry with this **Deploy to Azure** template:

[![Azure Deployment](https://azuredeploy.net/deploybutton.png)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fazure%2Fiotedgedev%2Fmaster%2Fassets%2Fdeploy%2FARMDeployment%2Fazuredeploy.json)

> Note: If you do not need a Container Registry, or are planning to use a local registry, then you should run the **iotedgedev iothub setup** command instead of running this **Deploy to Azure** template, because the template includes a Container Registry.

#### Manual Setup
1. [**Create Azure IoT Hub**](https://docs.microsoft.com/en-us/azure/iot-hub/iot-hub-csharp-csharp-getstarted#create-an-iot-hub)
1. **Create Edge Device** using the Azure Portal
    - In your IoT Hub, click "IoT Edge", then click "Add IoT Edge Device"

1.  **Container Registry**
    When you develop for IoT Edge, you need to host your images in a container registry, which the IoT Edge runtime will fetch the modules images from when it starts. 

    > By default, the IoT Edge Dev Tool will use the Local Registry.

    We have tested the following options, but you can host your images on any Docker compatible registry host.

    1. Local Registry

        Set `CONTAINER_REGISTRY_SERVER` to `localhost:5000` and leave `CONTAINER_REGISTRY_USERNAME` and `CONTAINER_REGISTRY_PASSWORD` blank.

        ```
        CONTAINER_REGISTRY_SERVER="localhost:5000"
        ```

    1. Azure Container Registry

        You can create an [**Azure Container Registry**](https://docs.microsoft.com/en-us/azure/container-registry/container-registry-get-started-portal) and host your images there.
            - Make sure you enable Admin Access when you create the Azure Container Registry

        After created, open .env and set the following:

        ```
        CONTAINER_REGISTRY_SERVER="ACR URI" 
        CONTAINER_REGISTRY_USERNAME="ACR USERNAME"
        CONTAINER_REGISTRY_PASSWORD="ACR PASSWORD"
        ```

        Example:
        ```
        CONTAINER_REGISTRY_SERVER="jong.azurecr.io" 
        CONTAINER_REGISTRY_USERNAME="jong"
        CONTAINER_REGISTRY_PASSWORD="p@$$w0rd"
        ```

    1. Docker Hub

        You can also host your images on Docker Hub. Create a Docker Hub account and then open .env and enter the following:

        ```
        CONTAINER_REGISTRY_SERVER="DOCKER HUB USERNAME" 
        CONTAINER_REGISTRY_USERNAME="DOCKER HUB USERNAME"
        CONTAINER_REGISTRY_PASSWORD="DOCKER HUB PASSWORD"
        ```

        Example:

        ```
        CONTAINER_REGISTRY_SERVER="jongallant" 
        CONTAINER_REGISTRY_USERNAME="jongallant"
        CONTAINER_REGISTRY_PASSWORD="p@$$w0rd"
        ```