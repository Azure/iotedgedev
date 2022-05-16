# Set up and start modules on a virtual machine

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

6. **Troubleshooting**

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
