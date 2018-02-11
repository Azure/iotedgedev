export VERSION=$1
docker build -f Dockerfile.deps -t jongallant/iotedgedev-deps:$1 -t jongallant/iotedgedev-deps:$1-linux -t jongallant/iotedgedev-deps:latest -t jongallant/iotedgedev-deps:latest-linux   . 
cat Dockerfile | envsubst > Dockerfile.expanded
docker build -f Dockerfile.expanded -t jongallant/iotedgedev:$1 -t jongallant/iotedgedev:$1-linux -t jongallant/iotedgedev:latest -t jongallant/iotedgedev:latest-linux .
