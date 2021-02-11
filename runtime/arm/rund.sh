#!/bin/bash

echo '=> creating config.yaml'
cat <<EOF > /etc/iotedge/config.yaml
provisioning:
  source: "manual"
  device_connection_string: "$IOT_DEVICE_CONNSTR"
agent:
  name: "edgeAgent"
  type: "docker"
  env: {}
  config:
    image: "mcr.microsoft.com/azureiotedge-agent:1.0"
    auth: {}
hostname: "my_edge_host"
connect:
  management_uri: "unix:///var/run/iotedge/mgmt.sock"
  workload_uri: "unix:///var/run/iotedge/workload.sock"
listen:
  management_uri: "fd://iotedge.mgmt.socket"
  workload_uri: "fd://iotedge.socket"
homedir: "/var/lib/iotedge"
moby_runtime:
  uri: "unix:///var/run/docker.sock"
EOF

cat /etc/iotedge/config.yaml

echo '=> running iotedge daemon'
# exec iotedged -c /etc/iotedge/config.yaml
sudo systemctl restart iotedge
sudo sytemctl status iotedge
