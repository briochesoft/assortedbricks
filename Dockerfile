FROM python:3-slim

RUN adduser abricks

WORKDIR /home/abricks

COPY . .

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential=12.12 \
    && pip install --no-cache-dir -r requirements.txt \
    && apt-get --purge -y autoremove build-essential \
    && rm -rf /var/lib/apt/lists/*


USER abricks

HEALTHCHECK CMD bash -c "exec 6<> /dev/tcp/localhost/5000"

CMD [ "./run-assortedbricks" ]

EXPOSE 5000
