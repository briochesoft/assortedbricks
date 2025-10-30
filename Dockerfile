FROM python:3-slim

WORKDIR /usr/src/assortedbricks

COPY . .

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential=12.12 \
    && pip install --no-cache-dir -r requirements.txt \
    && apt-get --purge -y autoremove build-essential \
    && rm -rf /var/lib/apt/lists/*

CMD [ "./run-assortedbricks" ]

EXPOSE 5000
