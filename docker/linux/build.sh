export VERSION=$1
docker build -f Dockerfile.deps -t jongallant/iotedgedev:$1-deps-linux -t jongallant/iotedgedev:latest-deps-linux . 
cat Dockerfile | envsubst > Dockerfile.expanded
docker build -f Dockerfile.expanded -t jongallant/iotedgedev:$1-linux -t jongallant/iotedgedev:latest-linux .