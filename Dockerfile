FROM python:3-alpine

RUN pip install requests pytz

ADD src /opt/logreposit/solarlog-reader-service

WORKDIR /opt/logreposit/solarlog-reader-service

CMD [ "python", "-u", "./solarlog_reader_service.py" ]
