FROM ubuntu:16.04
RUN apt-get update && apt-get install -y --no-install-recommends \
    apt-transport-https \
    ca-certificates \
    curl \
    iproute2 \
    systemd  && \
    rm -rf /var/lib/apt/lists/*
RUN curl https://packages.microsoft.com/config/ubuntu/16.04/prod.list > ./microsoft-prod.list && \
    cp ./microsoft-prod.list /etc/apt/sources.list.d/ && \
    curl https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > microsoft.gpg && \
    cp ./microsoft.gpg /etc/apt/trusted.gpg.d/ 
RUN apt-get update && apt-get install -y --no-install-recommends \
    moby-cli \
    moby-engine && \ 
    rm -rf /var/lib/apt/lists/*
RUN apt-get update && apt-get install -y --no-install-recommends \    
    iotedge && \ 
    rm -rf /var/lib/apt/lists/*
COPY rund.sh rund.sh 
RUN sed -i 's/\r//' ./rund.sh && \
    chmod u+x rund.sh 
#ENTRYPOINT [ "bash" ]
ENTRYPOINT [ "./rund.sh" ]
