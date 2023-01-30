# import os
# import time
#
# from celery import Celery
#
#
# celery = Celery(__name__)
# celery.conf.broker_url = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379")
# celery.conf.result_backend = os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379")
#
#
# @celery.task(name="create_task")
# def create_task(task_type):
#     time.sleep(int(task_type) * 10)
#     return True


from celery import current_app as current_celery_app
from core.settings.base import settings



def create_celery():
    celery_app = current_celery_app
    # celery_app.config_from_object(settings.celery, namespace="CELERY")
    celery_app.conf.broker_url = settings.celery["CELERY_BROKER_URL"]  #os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379")
    celery_app.conf.result_backend = settings.celery["CELERY_RESULT_BACKEND"] #os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379")
    return celery_app



