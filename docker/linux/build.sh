docker build . -f Dockerfile.deps -t yorek/iotedgedev-deps:ubuntu
cat Dockerfile | envsubst > Dockerfile.expanded
docker build . -f Dockerfile.expanded -t yorek/iotedgedev:ubuntu
