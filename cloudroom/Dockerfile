FROM python:3.8-alpine

WORKDIR /usr/app

RUN apk update
RUN echo "http://dl-8.alpinelinux.org/alpine/edge/community" >> /etc/apk/repositories && \
    apk update && \
    apk add postgresql-dev g++ py3-lxml

COPY ./requirements.txt .

RUN pip install -U pip
RUN pip install -r requirements.txt

COPY . .
