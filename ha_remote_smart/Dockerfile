ARG BUILD_FROM
FROM $BUILD_FROM
LABEL org.opencontainers.image.source=https://github.com/Aculeasis/ha_remote_smart

RUN apk add --no-cache python3 py3-pip smartmontools

COPY run.sh /etc/services.d/ha_remote_smart/run
COPY requirements.txt /
COPY smart.py utils.py mqtt_adapters.py main.py /usr/bin/

RUN pip3 install --no-cache-dir --break-system-packages -r /requirements.txt

RUN chmod a+x /etc/services.d/ha_remote_smart/run
