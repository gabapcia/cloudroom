FROM python:3.8-alpine

WORKDIR /home/app

RUN apk update
RUN apk add postgresql-dev g++ libxslt-dev

COPY ./requirements.txt .

RUN pip install -U pip
RUN pip install -r requirements.txt

COPY . .