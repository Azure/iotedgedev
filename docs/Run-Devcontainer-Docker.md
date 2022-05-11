# Run the IoT Edge Dev Container with Docker

Before you run the container, you will need to create a local folder to store your IoT Edge solution files.

## Windows

```cmd
mkdir c:\temp\iotedge
docker run -ti -v /var/run/docker.sock:/var/run/docker.sock -v c:/temp/iotedge:/home/iotedge mcr.microsoft.com/iotedge/iotedgedev
```

## Linux

```bash
sudo mkdir /home/iotedge
sudo docker run -ti -v /var/run/docker.sock:/var/run/docker.sock -v ~/iotedge:/home/iotedge mcr.microsoft.com/iotedge/iotedgedev
```

## macOS

```bash
mkdir ~/iotedge
docker run -ti -v /var/run/docker.sock:/var/run/docker.sock -v ~/iotedge:/home/iotedge mcr.microsoft.com/iotedge/iotedgedev
```
