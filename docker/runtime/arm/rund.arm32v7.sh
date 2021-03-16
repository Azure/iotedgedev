#!/bin/bash

echo '=> detecting IP'
export IP=$(ip addr show eth0 | grep "inet\b" | awk '{print $2}' | cut -d/ -f1)
export IOT_DEVICE_HOSTNAME="$IP"
export AGENT_IMAGE="mcr.microsoft.com/azureiotedge-agent:1.1@sha256:84d81e0527799e903fca9602c56efcbc43ce6f90eaeb7316fddc7d663d40d1b1"
#export IOTEDGE_LOG=edgelet=debug

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
    image: "$AGENT_IMAGE"
    auth: {}
hostname: "edgehub"
connect:
  management_uri: "http://$IOT_DEVICE_HOSTNAME:15580"
  workload_uri: "http://$IOT_DEVICE_HOSTNAME:15581"
listen:
  management_uri: "http://$IP:15580"
  workload_uri: "http://$IP:15581"
homedir: "/var/lib/iotedge"
moby_runtime:
  docker_uri: "/var/run/docker.sock"
  network: "azure-iot-edge"
EOF

cat /etc/iotedge/config.yaml

echo '=> running iotedge daemon'
exec iotedged -c /etc/iotedge/config.yaml

