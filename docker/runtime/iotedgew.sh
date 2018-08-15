container_ip=$(docker inspect iotedgec -f "{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}")
container_ip="http://$container_ip:15580"

docker exec iotedgec iotedge -H ${container_ip} "$@"
