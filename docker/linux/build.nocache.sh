export VERSION=$1
docker build --no-cache -f Dockerfile.deps -t jongallant/iotedgedev-deps:$1 -t jongallant/iotedgedev-deps:$1-linux -t jongallant/iotedgedev-deps:latest -t jongallant/iotedgedev-deps:latest-linux   . 
cat Dockerfile | envsubst > Dockerfile.expanded
docker build --no-cache -f Dockerfile.expanded -t jongallant/iotedgedev:$1 -t jongallant/iotedgedev:$1-linux -t jongallant/iotedgedev:latest -t jongallant/iotedgedev:latest-linux .
cat Dockerfile.dev | envsubst > Dockerfile.dev.expanded
docker build --no-cache -f Dockerfile.dev.expanded -t jongallant/iotedgedev-dev:$1 -t jongallant/iotedgedev-dev:$1-linux -t jongallant/iotedgedev-dev:latest -t jongallant/iotedgedev-dev:latest-linux .