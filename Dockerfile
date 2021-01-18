FROM python:3.9-slim as base

WORKDIR /opt/app

RUN apt-get update && apt-get upgrade -y
RUN apt-get install -y --no-install-recommends g++ netcat

COPY ./requirements.txt .

RUN pip install -U pip
RUN pip install -Ur requirements.txt

COPY . .


FROM base AS celery-worker
CMD ["celery", "-A", "cloudroom", "beat", "-l", "INFO"]


FROM base AS celery-beat
CMD ["celery", "-A", "cloudroom", "worker", "-l", "INFO"]


FROM base AS django
ENTRYPOINT [ "./entrypoint.sh" ]
EXPOSE 8000
CMD ["./manage.py", "runserver", "0.0.0.0:8000"]


FROM django AS ci-django
RUN pip install -Ur requirements.ci.txt
