curl https://packages.microsoft.com/config/ubuntu/16.04/prod.list > ./microsoft-prod.list && \
cp ./microsoft-prod.list /etc/apt/sources.list.d/ && \
curl https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > microsoft.gpg && \
cp ./microsoft.gpg /etc/apt/trusted.gpg.d/ 
apt-get update && apt-get install -y --no-install-recommends \
moby-cli \
moby-engine && \ 
rm -rf /var/lib/apt/lists/*
apt-get update && apt-get install -y --no-install-recommends \    
iotedge && \ 
rm -rf /var/lib/apt/lists/*