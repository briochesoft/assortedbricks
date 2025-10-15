FROM python:3-slim

WORKDIR /usr/src/assortedbricks

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "./run-assortedbricks" ]

EXPOSE 5000
