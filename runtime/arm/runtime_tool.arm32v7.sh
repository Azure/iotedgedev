apt-get update && apt-get install curl
export OS_NAME=$(grep '^NAME=' /etc/os-release | cut -c 6-)
export OS_ID=$(grep '^ID=' /etc/os-release | cut -c 4-)
export OS_VERSION_ID=$(grep '^VERSION_ID=' /etc/os-release | cut -c 12-)
export OS_VERSION_CODENAME=$(grep '^VERSION_CODENAME=' /etc/os-release | cut -c 18-)

printenv "$OS_NAME"
printenv "$OS_ID"
printenv "$OS_VERSION_ID"
printenv "$OS_VERSION_CODENAME"

# if [[ "$OSTYPE" == "linux-gnu"* ]]; then

# elif [[ "$OSTYPE" == "linux-gnueabihf"* ]]; then
# else
# fi
curl https://packages.microsoft.com/config/debian/stretch/multiarch/prod.list > ./microsoft-prod.list
# cat ./microsoft-prod.list >> /etc/apt/sources.list
sudo cp ./microsoft-prod.list /etc/apt/sources.list.d/

curl https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > microsoft.gpg
sudo cp ./microsoft.gpg /etc/apt/trusted.gpg.d/

apt-get install moby-engine moby-cli

sudo apt-get update

apt-get install iotedge