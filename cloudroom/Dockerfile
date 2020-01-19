FROM python:3.8-alpine

WORKDIR /home/app

COPY . .

RUN apk update
RUN apk add postgresql-dev g++

RUN pip install -U pip
RUN pip install -r requirements.txt