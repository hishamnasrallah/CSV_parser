from celery import current_app as current_celery_app
from core.settings.base import settings



def create_celery():
    celery_app = current_celery_app
    celery_app.conf.broker_url = settings.celery["CELERY_BROKER_URL"]
    celery_app.conf.result_backend = settings.celery["CELERY_RESULT_BACKEND"]
    celery_app.conf.task_serializer = 'json'
    celery_app.conf.result_serializer = 'json'
    celery_app.conf.accept_content = ['json']

    return celery_app



