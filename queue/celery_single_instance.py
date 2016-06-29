from __future__ import absolute_import
from functools import wraps
from celery.utils.log import get_task_logger
import redis

logger = get_task_logger(__name__)


class OtherInstanceException(Exception):
    def __init__(self, text, *args):
        super(OtherInstanceException, self).__init__(text, *args)
        print text

def single_instance(func, lock_timeout=None):
    @wraps(func)
    def wrapped(self, *args, **kwargs):
        redis_instance = redis.Redis()
        ret_value, have_lock = None, False
        redis_key = 'celery:locks:{task_name}'.format(task_name=self.name)
        timeout_ = lock_timeout or self.soft_time_limit or self.time_limit or (60 * 5)
        lock = redis_instance.lock(redis_key, timeout=(int(timeout_) + 5))
        logger.debug('single_instance.wrapped({}.{}): Timeout {}s | Redis key {}'.format(func.__module__, func.func_name, timeout_, redis_key))
        
        try:
            have_lock = lock.acquire(blocking=False)
            if have_lock:
                logger.debug('single_instance.wrapped({}.{}): Got lock, running.'.format(func.__module__, func.func_name))
                ret_value = func(*args, **kwargs)
            else:
                logger.debug('single_instance.wrapped({}.{}): Another instance is running.'.format(func.__module__, func.func_name))
                self.retry(countdown=60, exc=OtherInstanceException("Cannot acquire lock for %s" % self.request.id), max_retries=10)

        finally:
            if have_lock:
                logger.debug('single_instance.wrapped({}.{}): Releasing lock.'.format(
                    func.__module__, func.func_name))
                lock.release()
        return ret_value

    return wrapped
