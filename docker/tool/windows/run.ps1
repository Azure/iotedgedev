$ErrorActionPreference = "Stop"


# Get IoTEdgeDev source folder
$source_folder = Get-Location | Split-Path | Split-Path 

# Use Docker's local named pipe instead of exposing the daemon over unauthenticated TCP.
docker run -it -e DOCKER_HOST=npipe:////./pipe/docker_engine --mount "type=npipe,source=\\.\pipe\docker_engine,target=\\.\pipe\docker_engine" -v ${source_folder}:c:/home/iotedge/tool microsoft/iotedgedev:latest-windows