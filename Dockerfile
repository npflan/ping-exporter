FROM alpine:3.4

RUN apk add --no-cache python3

RUN mkdir -p /opt/exporter/
WORKDIR /opt/exporter
COPY requirements.txt /opt/exporter/
COPY network_data.csv /opt/exporter/
RUN pip3 install -r requirements.txt

COPY app.py /opt/exporter/

ENTRYPOINT ["gunicorn", "-b 0.0.0.0:9120", "app:app"]
EXPOSE 9120
