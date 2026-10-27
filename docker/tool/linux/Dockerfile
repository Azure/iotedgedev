FROM iotedgedev-linux-base
ARG IOTEDGEDEV_VERSION
ARG PIP_INDEX_URL
COPY --chown=iotedgedev:iotedgedev iotedgedev-$IOTEDGEDEV_VERSION-py3-none-any.whl dist/iotedgedev-$IOTEDGEDEV_VERSION-py3-none-any.whl
RUN pip install --no-cache-dir dist/iotedgedev-$IOTEDGEDEV_VERSION-py3-none-any.whl \
        "lark-parser>=0.7.1,<0.8.0" ply decorator && \
    pip check && \
    rm -rf dist/
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8
