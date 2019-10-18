# Get IoTEdgeDev source folder
$source_folder = Get-Location | Split-Path | Split-Path | Split-Path

# Run Docker Container
docker run -it -v //var//run//docker.sock://var//run//docker.sock -v ${source_folder}:/home/iotedge/tool mcr.microsoft.com/iotedge/iotedgedev:latest