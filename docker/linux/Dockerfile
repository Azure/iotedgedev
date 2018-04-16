FROM ubuntu:16.04
ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update && \
    apt-get install -y --no-install-recommends dialog apt-utils curl apt-transport-https python-pip libltdl-dev docker.io && \ 
    curl -sL https://deb.nodesource.com/setup_8.x | bash - && \
    apt-get install -y nodejs && \
    curl -O https://bootstrap.pypa.io/get-pip.py && python get-pip.py && \ 
    curl https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > microsoft.gpg && \ 
    mv microsoft.gpg /etc/apt/trusted.gpg.d/microsoft.gpg && \ 
    sh -c 'echo "deb [arch=amd64] https://packages.microsoft.com/repos/microsoft-ubuntu-xenial-prod xenial main" > /etc/apt/sources.list.d/dotnetdev.list' && \ 
    apt-get update && \ 
    apt-get install -y dotnet-sdk-2.1.3 && \
    AZ_REPO=$(lsb_release -cs) && \
    echo "deb [arch=amd64] https://packages.microsoft.com/repos/azure-cli/ $AZ_REPO main" | \
    tee /etc/apt/sources.list.d/azure-cli.list && \
    apt-key adv --keyserver packages.microsoft.com --recv-keys 52E16F86FEE04B979B07E28DB02C46DF417A0893 && \   
    apt-get update && apt-get install azure-cli && \
    az extension add --name azure-cli-iot-ext && \
    npm i -g iothub-explorer && \
    rm -rf /var/lib/apt/lists/*
RUN apt-get update && \
    apt-get install -y --no-install-recommends python-dev build-essential libssl-dev libffi-dev libxml2-dev libxslt1-dev zlib1g-dev
WORKDIR /home/iotedge
RUN pip install bumpversion==0.5.3 wheel==0.29.0 watchdog==0.8.3 flake8==2.6.0 tox==2.3.1 coverage==4.1 Sphinx==1.4.8 cryptography PyYAML==3.11 iotedgedev
ENV DEBIAN_FRONTEND teletype
