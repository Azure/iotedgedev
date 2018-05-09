FROM ubuntu:16.04
ENV DEBIAN_FRONTEND noninteractive
ENV DOTNETCORESDK_VERSION 2.1.4
RUN apt-get update && \
    apt-get install -y --no-install-recommends dialog apt-utils curl apt-transport-https python-pip python3-pip libltdl-dev docker.io && \ 
    curl -sL https://deb.nodesource.com/setup_8.x | bash - && \
    apt-get install -y nodejs && \
    alias python=python3 && \
    alias pip=pip3 
RUN curl https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > microsoft.gpg && \ 
    mv microsoft.gpg /etc/apt/trusted.gpg.d/microsoft.gpg && \ 
    sh -c 'echo "deb [arch=amd64] https://packages.microsoft.com/repos/microsoft-ubuntu-xenial-prod xenial main" > /etc/apt/sources.list.d/dotnetdev.list' && \ 
    apt-get update && \ 
    apt-get install -y dotnet-sdk-${DOTNETCORESDK_VERSION}
RUN AZ_REPO=$(lsb_release -cs) && \
    echo "deb [arch=amd64] https://packages.microsoft.com/repos/azure-cli/ $AZ_REPO main" | \
    tee /etc/apt/sources.list.d/azure-cli.list && \
    apt-key adv --keyserver packages.microsoft.com --recv-keys 52E16F86FEE04B979B07E28DB02C46DF417A0893 && \   
    apt-get update && apt-get install azure-cli
RUN az extension add --name azure-cli-iot-ext && \
    npm i -g iothub-explorer && npm i -g tree-kill && \
    apt-get update && \
    apt-get install -y --no-install-recommends python-dev build-essential libssl-dev libffi-dev libxml2-dev libxslt1-dev zlib1g-dev && \
    rm -rf /var/lib/apt/lists/*
RUN python -m pip install --upgrade pip    
RUN pip install setuptools
RUN pip --no-cache-dir install -U iotedgedev
WORKDIR /home/iotedge
COPY install-dev.sh /scripts/install-dev.sh
RUN sed -i 's/\r//' /scripts/install-dev.sh
ENV DEBIAN_FRONTEND teletype