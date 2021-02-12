apt-get update && apt-get install curl
export OS_NAME=$(grep '^NAME=' /etc/os-release | cut -c 6-)
export OS_ID=$(grep '^ID=' /etc/os-release | cut -c 4-)
export OS_VERSION_ID=$(grep '^VERSION_ID=' /etc/os-release | cut -c 12-)
export OS_VERSION_CODENAME=$(grep '^VERSION_CODENAME=' /etc/os-release | cut -c 18-)

echo "OS_NAME = $(printenv OS_NAME)"
echo "OS_ID = $(printenv OS_ID)"
echo "OS_VERSION_ID = $(printenv OS_VERSION_ID)"
echo "OS_VERSION_CODENAME = $(printenv OS_VERSION_CODENAME)"

if [[ "$OSTYPE" == "linux-gnu" ]]; then
    if [[ "$OS_ID" == "ubuntu" ]]; then
        if [[ "$OS_VERSION_ID" == "\"16.04\"" ]]; then    
            curl https://packages.microsoft.com/config/ubuntu/16.04/multiarch/prod.list > ./microsoft-prod.list
        elif [[ "$OS_VERSION_ID" == "\"18.04\"" ]]; then
            curl https://packages.microsoft.com/config/ubuntu/18.04/multiarch/prod.list > ./microsoft-prod.list
        fi
    fi
elif [[ "$OSTYPE" == "linux-gnueabihf" ]]; then
    if [[ "$OS_ID" == "raspbian" ]]; then
        curl https://packages.microsoft.com/config/debian/stretch/multiarch/prod.list > ./microsoft-prod.list
    fi
else
    echo "Microsoft has no packages for this operating system."
fi

sudo cp ./microsoft-prod.list /etc/apt/sources.list.d/

curl https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > microsoft.gpg
sudo cp ./microsoft.gpg /etc/apt/trusted.gpg.d/

apt-get install moby-engine moby-cli

sudo apt-get update

apt-get install iotedge