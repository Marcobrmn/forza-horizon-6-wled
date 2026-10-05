FROM ghcr.io/home-assistant/base:latest
ARG BUILD_VERSION=1.1.2
ARG BUILD_ARCH=amd64
LABEL io.hass.version="${BUILD_VERSION}" io.hass.type="app" io.hass.arch="${BUILD_ARCH}"
RUN apk add --no-cache python3
COPY receiver.py /app/receiver.py
CMD ["python3", "-u", "/app/receiver.py"]
