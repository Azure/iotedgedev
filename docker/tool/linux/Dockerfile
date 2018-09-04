FROM iotedgedev-linux-base
ARG IOTEDGEDEV_VERSION
COPY iotedgedev-$IOTEDGEDEV_VERSION-py2.py3-none-any.whl dist/iotedgedev-$IOTEDGEDEV_VERSION-py2.py3-none-any.whl
RUN pip install dist/iotedgedev-$IOTEDGEDEV_VERSION-py2.py3-none-any.whl
RUN export LC_ALL=C.UTF-8 && \
    export LANG=C.UTF-8

RUN useradd -m iotedgedev && \
    echo 'iotedgedev ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers && \
    chown -R iotedgedev:iotedgedev .

USER iotedgedev