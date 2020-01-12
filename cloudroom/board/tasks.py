from celery import task


@task
def hello():
    print('Hello, world!')