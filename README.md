# celery_single_instance
elery task decorator. Forces the task to have only one running instance at a time through   locks set using Redis. Use with binded tasks (@celery.task(bind=True)) - adapted from @Robpol86 code

