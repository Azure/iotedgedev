IoT Edge Dev Tool is intended to help with IoT Edge development and doesn't necessarily need to be taken on as a dependency in production or integration environments, where you'll likely want to use the IoT Edge runtime directly. Please check below documents for the instructions on setting up IoT Edge runtime:
- [Linux X64](https://docs.microsoft.com/en-us/azure/iot-edge/how-to-install-iot-edge-linux)
- [Linux ARM32](https://docs.microsoft.com/en-us/azure/iot-edge/how-to-install-iot-edge-linux-arm)
- [Windows with Windows container](https://docs.microsoft.com/en-us/azure/iot-edge/how-to-install-iot-edge-windows-with-windows)
- [Windows with Linux container](https://docs.microsoft.com/en-us/azure/iot-edge/how-to-install-iot-edge-windows-with-linux)
- [IoT Core](https://docs.microsoft.com/en-us/azure/iot-edge/how-to-install-iot-core)

Having said that, there's nothing stopping you from deploying IoT Edge Dev Tool to your IoT Edge device. It may be helpful if you want to run the `iotedgedev docker clean` command to clean up Docker containers and images. Or if you want to run `iotedgedev docker log --show` to see all the log files on the device or `iotedgedev docker log --save` to output to the LOGS_PATH directory.

> Please note that you will need .NET Core SDK 2.1 to add C# modules and C# Function modules on a Raspberry Pi. Check [Manual Dev Machine Setup](environment-setup/manual-dev-machine-setup) to learn how to install.

### Raspberry Pi

#### Config Changes

If you are running on Raspberry Pi you need to use the arm32v7 Dockerfile. Open `deployment.template.json`, find the JSON dictionary for `filtermodule`, and replace `"image": "${MODULES.filtermodule.amd64}",` with `"image": "${MODULES.filtermodule.arm32v7}",`

#### Environment Variable Change

Open your `.env` file and add `arm32v7` to your `ACTIVE_DOCKER_PLATFORMS` setting. This will tell the IoT Edge Dev Tool to also build the arm32v7 images.

```sh
ACTIVE_DOCKER_PLATFORMS="amd64,arm32v7"
```
