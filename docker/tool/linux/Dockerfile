FROM iotedgedev-linux-base
ARG IOTEDGEDEV_VERSION
COPY iotedgedev-$IOTEDGEDEV_VERSION-py3-none-any.whl dist/iotedgedev-$IOTEDGEDEV_VERSION-py3-none-any.whl
RUN sudo -H pip3 install dist/iotedgedev-$IOTEDGEDEV_VERSION-py3-none-any.whl && \
    sudo rm -rf dist/
ENV LC_ALL C.UTF-8
ENV LANG C.UTF-8
