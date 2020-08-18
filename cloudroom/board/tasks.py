from celery import task
from . import models


@task
def turn_pin_on(pins):
    pass # TODO
