apt-get update && apt-get install curl

curl https://packages.microsoft.com/config/debian/stretch/multiarch/prod.list > ./microsoft-prod.list
cat ./microsoft-prod.list >> /etc/apt/sources.list
curl https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > microsoft.gpg
sudo cp ./microsoft.gpg /etc/apt/trusted.gpg.d/

apt-get install moby-engine moby-cli

sudo apt-get update

apt-get install iotedge

cp ../../docker/runtime/arm/rund.arm32v7.sh rund.sh