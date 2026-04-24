ARG BUILD_FROM
FROM $BUILD_FROM

RUN apk add --no-cache python3 tzdata

COPY rootfs /

RUN chmod a+x /run.sh /usr/bin/sonoff_scheduler.py

CMD ["/run.sh"]
