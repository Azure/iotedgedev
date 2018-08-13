if (-not (Test-Path env:IOT_DEVICE_CONNSTR)) { 
    Write-Host "Cannot run IoT Edge container: IOT_DEVICE_CONNSTR is not set"
    Write-Host "Eg:"
    Write-Host "`$env:IOT_DEVICE_CONNSTR=`"HostName=iothub0730.azure-devices.net;DeviceId=myEdgeDevice;SharedAccessKey=zfD73oX3agHTlT0rOvjPnYTkxRPw/k3U0exEGBDWQ5A=`""
    exit
}

docker run `
    -i `
    -t `
    --rm `
    -v //var//run//docker.sock://var//run//docker.sock `
    -p 15580:15580 `
    -p 15581:15581 `
    --network bridge `
    --name iotedgec `
    -e IOT_DEVICE_CONNSTR=$IOT_DEVICE_CONNSTR `
    iot-edge-c