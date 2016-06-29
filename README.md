# celery single instance decorator
This decorator forces the task to have only one running instance at a time through locks set using Redis. Use with binded tasks (@celery.task(bind=True)) - adapted from @Robpol86 code in order to retry the task if the lock is already acquired.

