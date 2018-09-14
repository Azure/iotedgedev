FROM arm32v7/ubuntu:16.04

RUN apt-get update && apt-get install -y --no-install-recommends \
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

RUN curl -L https://aka.ms/moby-engine-armhf-latest -o moby_engine.deb && dpkg -i ./moby_engine.deb && rm ./moby_engine.deb && \
    curl -L https://aka.ms/moby-cli-armhf-latest -o moby_cli.deb && dpkg -i ./moby_cli.deb && rm ./moby_cli.deb

RUN apt-get update && apt-get install -f

RUN curl -L https://aka.ms/libiothsm-std-linux-armhf-latest -o libiothsm-std.deb && dpkg -i ./libiothsm-std.deb && rm ./libiothsm-std.deb && \
    curl -L https://aka.ms/iotedged-linux-armhf-latest -o iotedge.deb && dpkg -i ./iotedge.deb && rm ./iotedge.deb

RUN apt-get update && apt-get install -f

COPY rund.arm32v7.sh rund.sh

RUN sed -i 's/\r//' ./rund.sh && \
    chmod u+x rund.sh

WORKDIR /lib/arm-linux-gnueabihf/

RUN ln -s libcrypto.so.1.0.0 libcrypto.so.1.0.2 && \
    ln -s libssl.so.1.0.0 libssl.so.1.0.2

WORKDIR /

ENTRYPOINT [ "./rund.sh" ]

