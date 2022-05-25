
# Set up and start the IoT Edge Simulator

In order to run the modules defined in a deployment configuration (such as `config/deployment.amd64.json`) on your development machine using the `iotedgedev` simulator run the following command:

```sh
iotedgedev start --setup --file config/deployment.amd64.json
```

> The [IoT Edge Hub Simulator](https://github.com/Azure/iotedgehubdev) starts the containers defined in the IoT edge device manifest in your local machine.

<details>
<summary>More information</summary>

1. You will see an "IoT Edge Simulator has been started in solution mode." message at the end of the terminal output
2. Run ` docker ps`, you will see your modules running as well as an edgeHubDev container

</details>
