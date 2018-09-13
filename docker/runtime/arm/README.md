# Running IoT Edge Daemon on AARCH64/Arm64v8 devices

In order to run the edge daemon on 64-bit arm devices, we must
- Perform the edge daemon installation in a arm32v7 docker image
- run that container
- configure your edge device to use the arm32v7 docker images for hub and agent

## Caveats

- This will not work on systems such as cavium/thunderx as they don't have access to the arm32v7 instruction sets and lack a compatible binary interface.

- `docker manifest` is a preview feature, enable it following the instructions here: https://docs.docker.com/edge/engine/reference/commandline/manifest/

## Configure the Edge device

First we need to get the sha256 of the arm32v7 images.

```bash
sudo apt-get install jq

>sudo docker manifest inspect mcr.microsoft.com/azureiotedge-agent:1.0 | jq '.manifests[] | select(.platform | select(.architecture=="arm")).digest'
#sha256:3fdb80a6dfe1fbcbf11cfcea56dda79d1d779490c66d394a2b3f388d74ab0c26

sudo docker manifest inspect mcr.microsoft.com/azureiotedge-hub:1.0 | jq '.manifests[] | select(.platform | select(.architecture=="arm")).digest'
#sha256:05905d76abdf904fc47355d5774f740f448b730688c95fe88a70021d1a671ea4

sudo docker manifest inspect mcr.microsoft.com/azureiotedge-simulated-temperature-sensor:1.0  | jq '.manifests[] | select(.platform | select(.architecture=="arm")).digest'
#sha256:90a74961928e847ce5c2d58109510f16584bccfb81555df376aa01b9175eabe1
```

- Create an Edge device.
- From the Device Details page, click "Set Modules" at the top.
    - From the Set Modules page, click "Configure advanced Edge Runtime settings"
    - From the "Configure advanced Edge Runtime settings" view
    - For edge hub, enter image: mcr.microsoft.com/azureiotedge-hub:1.0@sha256:05905d76abdf904fc47355d5774f740f448b730688c95fe88a70021d1a671ea4
    - For edge agent, enter image: mcr.microsoft.com/azureiotedge-agent:1.0@sha256:3fdb80a6dfe1fbcbf11cfcea56dda79d1d779490c66d394a2b3f388d74ab0c26
    - Click Save
    - Click Add under "deployment modules"
        - Name: tempSensor
        - Image: mcr.microsoft.com/azureiotedge-simulated-temperature-sensor:1.0@sha256:90a74961928e847ce5c2d58109510f16584bccfb81555df376aa01b9175eabe1
        - Click Save
    - Click Next
    - Click Next
- Click Submit

## Build the docker image

```bash
./build.sh
# Edit run.sh with your edge device connection string
./run.sh
```

For usage, see the main readme under "Use IoT Edge tool".
