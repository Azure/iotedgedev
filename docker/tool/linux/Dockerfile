FROM iotedgedev-linux-base
ARG IOTEDGEDEV_VERSION
COPY --chown=iotedgedev:iotedgedev iotedgedev-$IOTEDGEDEV_VERSION-py3-none-any.whl dist/iotedgedev-$IOTEDGEDEV_VERSION-py3-none-any.whl
RUN pip install --no-cache-dir dist/iotedgedev-$IOTEDGEDEV_VERSION-py3-none-any.whl && \
    rm -rf dist/
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8
