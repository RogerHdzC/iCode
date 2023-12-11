FROM python:3.10-slim-bookworm

ENV PYTHONUNBUFFERED=1

WORKDIR /django

RUN apt-get update && apt-get install -y --no-install-recommends \
libpq-dev \
python3-psycopg2 \
graphviz \
&& \
apt-get clean && \
rm -rf /var/lib/apt/lists/*

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt
