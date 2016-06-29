
from celery_single_instance import OtherInstance, single_instance
from celery import Celery
import pytest

app = Celery('queue', broker='amqp://guest@localhost//')

@app.task(bind=True)
@single_instance
def add(x, y):
    return x + y


@pytest.fixture(autouse=True, scope='session')
def register_tasks():
    celery.tasks.register(add)


def test_basic():
    """Test task to make sure it works before testing instance decorator."""
    expected = 8
    actual = add.apply(args=(4, 4)).get()
    assert expected == actual


def test_instance():
    """Test for exception to be raised."""
    # Prepare.
    redis = current_app.extensions['redis']['REDIS']
    redis_key = 'celery:locks:{task_name}'.format(task_name=add.name)
    lock = redis.lock(redis_key, timeout=1)
    have_lock = lock.acquire(blocking=False)
    assert True == bool(have_lock)
    # Test.
    with pytest.raises(OtherInstance):
        add.apply(args=(4, 4)).get()
    lock.release()

