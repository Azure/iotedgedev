FROM iotedgedev-linux-base
ARG IOTEDGEDEV_VERSION
COPY iotedgedev-$IOTEDGEDEV_VERSION-py2.py3-none-any.whl dist/iotedgedev-$IOTEDGEDEV_VERSION-py2.py3-none-any.whl
RUN pip install dist/iotedgedev-$IOTEDGEDEV_VERSION-py2.py3-none-any.whl