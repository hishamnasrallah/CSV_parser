from celery.result import AsyncResult


def cancel_task(tasks: list):
    from app.tasks import celery

    for task_id in tasks:
        task = AsyncResult(task_id, app=celery)
        if task.state == 'PENDING':
            task.revoke(terminate=True)
            print(f"Task {task_id} has been revoked.")
        else:
            backend = celery.backend
            backend.forget(task_id)
            backend.delete(task_id)
            print(f"Task {task_id} has been deleted from the result backend.")

