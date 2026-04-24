ARG BUILD_FROM=ghcr.io/home-assistant/amd64-base:latest
FROM $BUILD_FROM

RUN apk add --no-cache python3 tzdata

COPY run.sh /
COPY rootfs /

RUN chmod a+x /run.sh /usr/bin/sonoff_scheduler.py

CMD ["/run.sh"]
