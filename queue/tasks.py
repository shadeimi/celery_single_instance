
from celery_single_instance import OtherInstanceException, single_instance
from celery import Celery
import time

app = Celery('queue', broker='amqp://guest@localhost//')

@app.task(bind=True)
@single_instance
def add(x, y):
    time.sleep(20)
    return x + y


# tasks.add.apply_async([2,3], queue='transient', propagate=True, serializer="json")
