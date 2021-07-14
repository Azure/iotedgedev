# Dependencies versions
ARG PYTHON_VERSION="3.7.10"

FROM python:${PYTHON_VERSION}-buster

# Dependencies versions
ARG DOCKER_COMPOSE_VERSION="1.29.2"
ARG COOKIECUTTER_VERSION="1.7.3"
ARG AZURE_CLI_VERSION="2.24.0-1~buster"
ARG NODE_VERSION="15.x"
ARG DOTNET_VERSION="5.0"
ARG JDK_VERIOSN="2:1.11-71"
ARG MAVEN_VERIOSN="3.6.0-1"

RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential && \
    apt-get install -y python2.7-dev libffi-dev libssl-dev

# Install python libraries
RUN pip install cookiecutter==${COOKIECUTTER_VERSION} docker-compose==${DOCKER_COMPOSE_VERSION} 

RUN \
    # Install the Azure CLI and IoT extension
    apt-get install -y ca-certificates curl apt-transport-https lsb-release gnupg && \
    curl -sL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor | tee /etc/apt/trusted.gpg.d/microsoft.gpg > /dev/null && \
    echo "deb [arch=amd64] https://packages.microsoft.com/repos/azure-cli/ $(lsb_release -cs) main" | tee /etc/apt/sources.list.d/azure-cli.list && \
    apt-get update && apt-get install -y azure-cli=${AZURE_CLI_VERSION} && \
    az extension add --name azure-iot --system && \
    az extension update --name azure-iot && \
    # Install Docker CE CLI
    apt-get install -y apt-transport-https ca-certificates curl gnupg-agent software-properties-common lsb-release && \
    curl -fsSL https://download.docker.com/linux/$(lsb_release -is | tr '[:upper:]' '[:lower:]')/gpg | apt-key add - 2>/dev/null && \
    add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/$(lsb_release -is | tr '[:upper:]' '[:lower:]') $(lsb_release -cs) stable" && \
    apt-get update && \
    apt-get install -y docker-ce-cli && \
    # Install node, npm, Yoeman, node.js modules
    curl -fsSL https://deb.nodesource.com/setup_${NODE_VERSION} | bash - && \
    apt-get install -y nodejs && \
    npm install -g yo && \
    npm i -g yo generator-azure-iot-edge-module && \
    cd ~ && \ 
    rm -rf /tmp/* && \
    # Install dotnet SDK
    wget https://packages.microsoft.com/config/debian/10/packages-microsoft-prod.deb -O packages-microsoft-prod.deb && \
    dpkg -i packages-microsoft-prod.deb && \
    rm packages-microsoft-prod.deb && \ 
    apt-get update && apt-get install -y apt-transport-https && \
    apt-get update && apt-get install -y dotnet-sdk-${DOTNET_VERSION} && \
    # Install Java JDK, Maven
    apt-get install -y default-jdk=${JDK_VERIOSN} && \
    apt-get install -y maven=${MAVEN_VERIOSN} && \
    #
    # Clean up
    apt-get autoremove -y && \
    apt-get clean -y && \
    rm -rf /var/lib/apt/lists/*

# Customize bash
RUN \
    # Git command prompt
    git clone https://github.com/magicmonty/bash-git-prompt.git ~/.bash-git-prompt --depth=1 && \
    echo "if [ -f \"$HOME/.bash-git-prompt/gitprompt.sh\" ]; then GIT_PROMPT_ONLY_IN_REPO=1 && source $HOME/.bash-git-prompt/gitprompt.sh; fi" >> "/root/.bashrc" && \
    # Install bash completion
    apt-get update && \
    apt-get -y install bash-completion && \
    echo "source /usr/share/bash-completion/bash_completion" >> ~/.bashrc 
