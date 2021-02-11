apt-get update && apt-get install -y --no-install-recommends \
apt-transport-https \
ca-certificates \
curl \
iptables \
iproute2 \
libcurl3 \
libffi-dev \
libssl1.0.0=1.0.2g-1ubuntu4.13 \
libssl-dev=1.0.2g-1ubuntu4.13 \
systemd && \
rm -rf /var/lib/apt/lists/*

# wget https://aka.ms/moby-engine-armhf-latest -o moby_engine.deb && dpkg -i ./moby_engine.deb && rm ./moby_engine.deb && \
# wget https://aka.ms/moby-cli-armhf-latest -o moby_cli.deb && dpkg -i ./moby_cli.deb && rm ./moby_cli.deb

# apt-get update && apt-get install -f

# wget https://aka.ms/libiothsm-std-linux-armhf-latest -o libiothsm-std.deb && dpkg -i ./libiothsm-std.deb && rm ./libiothsm-std.deb && \
# wget https://aka.ms/iotedged-linux-armhf-latest -o iotedge.deb && dpkg -i ./iotedge.deb && rm ./iotedge.deb

apt-get install moby-engine moby-cli

apt-get update && apt-get install -f

curl https://packages.microsoft.com/config/debian/stretch/multiarch/prod.list > ./microsoft-prod.list
sudo cp ./microsoft-prod.list /etc/apt/sources.list.d/
curl https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > microsoft.gpg
sudo cp ./microsoft.gpg /etc/apt/trusted.gpg.d/

apt-get update && apt-get install -f

apt-get install iotedge

cp rund.arm32v7.sh rund.sh

sed -i 's/\r//' ./rund.sh && \
chmod u+x rund.sh

cd /lib/arm-linux-gnueabihf/

ln -s libcrypto.so.1.0.0 libcrypto.so.1.0.2 && \
ln -s libssl.so.1.0.0 libssl.so.1.0.2

cd /

bash rund.sh