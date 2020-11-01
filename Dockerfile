FROM python:3.9-slim

WORKDIR /opt/app

RUN apt-get update && apt-get upgrade -y
RUN apt-get install -y --no-install-recommends g++ netcat

COPY ./requirements.txt .

RUN pip install -U pip
RUN pip install -Ur requirements.txt

COPY . .
