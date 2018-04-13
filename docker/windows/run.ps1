if ((Get-NetFirewallRule -DisplayName "Docker Proxy 2" -ErrorAction Ignore) -ne $null)
{
    New-NetFirewallRule -DisplayName "Docker Proxy" -LocalPort 2375 -Action Allow -Protocol TCP
}

$docker_gateway = (Get-NetIPAddress -InterfaceAlias 'vEthernet (nat) 2' -AddressFamily IPv4 | Select-Object IPAddress).IPAddress
$docker_host ="tcp://{0}:2375" -f $docker_gateway

docker run -it -e DOCKER_HOST=$docker_host iotdevedgecli:nanoserver