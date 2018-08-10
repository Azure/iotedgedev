param (
    [string]$interface = 'vEthernet (nat)'
 )

$ErrorActionPreference = "Stop"
 
#
# NOTE
# Make sure option "Expose daemon on tcp://localhost:2375 without TLS" is checked in Docker
# and also make sure that 
# "hosts": [ "tcp://0.0.0.0:2375" ]
# is added to your 
# C:\ProgramData\Docker\config\deamon.json
# file

#  Make sure firewall allows comminication via TCP 2375
if ((Get-NetFirewallRule -DisplayName "Docker Proxy" -ErrorAction Ignore) -eq $null)
{
    New-NetFirewallRule -DisplayName "Docker Proxy" -LocalPort 2375 -Action Allow -Protocol TCP
}

# Find IP Address used by Docker NAT
$docker_gateway = (Get-NetIPAddress -InterfaceAlias $interface -AddressFamily IPv4 | Select-Object IPAddress).IPAddress
$docker_host ="tcp://{0}:2375" -f $docker_gateway

# Get IoTEdgeDev source folder
$source_folder = Get-Location | Split-Path | Split-Path 

# Run Docker Container
docker run -it -e DOCKER_HOST=${docker_host} -v ${source_folder}:c:/home/iotedge/tool microsoft/iotedgedev:latest-windows