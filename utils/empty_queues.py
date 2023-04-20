import redis
import os


def empty_redis():
    try:
        redis_url = os.environ.get('CELERY_BROKER_URL')
        ip_address = redis_url.split("//")[1].split(":")[0]
        new_x = ip_address.replace("/", "")
        r = redis.Redis(host=new_x, port=6379, db=0)
        keys = r.keys('*')
        r.delete(*keys)
        return True
    except:
        raise "failed to delete redis"


def empty_celery():
    try:
        cmd = 'celery -A app.tasks.celery purge -f'
        os.system(cmd)
        return True
    except:
        raise "failed to delete celery"
