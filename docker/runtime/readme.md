# Running Azure IoT Edge in a container

## Usage

### Build docker image

Make sure you have Docker installed and configured to be in Linux Container mode.

Build the docker image by running the `build-container.ps1` file. It will create an image tagged `iot-edge-c`.

Set the connection string to the IoT Edge device you want to connect to in the `run-container.ps1` file.

### Run docker image

Create and set the enviroment variable IOT_DEVICE_CONNSTR to your IoT Edge Device connection string.

Execute the `run-container.ps1` file. A container named `iotedgec` will be created and inside the `iotedged` daemon will be started. If everything is working correctly you will see the deamon output log.

The deamon will use the default ip address assigned by Docker to the container (most probably will be 172.17.0.2). The discovery is automatically done in the `rund.sh` script. If you have changed your Docker network configuration this script may not work as expected, as it looks specifically for `eth0`.

### Use IoT Edge CLI

Once the container is running, open another console and from there you can use 

    docker exec iotedgec iotedge -H http://<CONTAINER_IP>:15580 <command>

to interact with IoT Edge daemon. For example:

    docker exec iotedgec iotedge -H http://172.17.0.2:15580 list

to list the active IoT Edge modules.

To simplify usage a wrapper around the docker exec command is available via `iotedgew.ps1`. It can be used just as the original `iotedge`, and it will automatically forward all request to the docker container:

    .\iotedgew list

To get the IP address used by the `iotedgec` container you use the `inspect` command:

    docker inspect iotedgec -f "{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}"

### Terminate container

Just `ctrl-c` in the running container.

