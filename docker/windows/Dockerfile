FROM iotedgedev-windows-base
ARG IOTEDGEDEV_VERSION
COPY iotedgedev-$IOTEDGEDEV_VERSION-py2.py3-none-any.whl dist/iotedgedev-latest-py2.py3-none-any.whl
RUN pip install dist/iotedgedev-latest-py2.py3-none-any.whl