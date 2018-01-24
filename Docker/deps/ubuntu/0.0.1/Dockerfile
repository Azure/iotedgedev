ARG DEBIAN_FRONTEND=noninteractive
FROM ubuntu:16.04
RUN apt-get update

#curl
RUN apt-get install -y curl

#python/pip
RUN apt-get install -y python-pip

#donet
RUN curl https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > microsoft.gpg
RUN mv microsoft.gpg /etc/apt/trusted.gpg.d/microsoft.gpg
RUN sh -c 'echo "deb [arch=amd64] https://packages.microsoft.com/repos/microsoft-ubuntu-xenial-prod xenial main" > /etc/apt/sources.list.d/dotnetdev.list'
RUN apt-get install -y apt-utils
RUN apt-get install -y apt-transport-https
RUN apt-get update
RUN apt-get install -y dotnet-sdk-2.1.3

#az cli
RUN sh -c 'echo "deb [arch=amd64] https://packages.microsoft.com/repos/azure-cli/ wheezy main" > /etc/apt/sources.list.d/azure-cli.list'
RUN apt-key adv --keyserver packages.microsoft.com --recv-keys 52E16F86FEE04B979B07E28DB02C46DF417A0893
RUN apt-get update && apt-get install azure-cli

#az iot cli
RUN az extension add --name azure-cli-iot-ext

#clean any apt-get cache
RUN apt-get clean