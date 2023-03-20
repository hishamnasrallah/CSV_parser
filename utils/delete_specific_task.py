from celery.result import AsyncResult
from loguru import logger


def cancel_task(tasks: list):
    from app.tasks import celery

    for task_id in tasks:
        task = AsyncResult(task_id, app=celery)
        if task.state == 'PENDING':
            task.revoke(terminate=True)
            logger.info(f"Task {task_id} has been revoked.")
        else:
            backend = celery.backend
            backend.forget(task_id)
            backend.delete(task_id)
            logger.info(f"Task {task_id} has been deleted from the result backend.")


