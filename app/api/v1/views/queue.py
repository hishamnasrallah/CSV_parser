from fastapi import APIRouter
from starlette import status

from utils.empty_queues import empty_redis, empty_celery

router = APIRouter(
    prefix='/csv/queue',
    tags=[]
)


@router.get("/empty_redis", status_code=status.HTTP_200_OK)
def purge_redis():
    result = empty_redis()
    return result


@router.get("/empty_celery", status_code=status.HTTP_200_OK)
def purge_celery():
    result = empty_celery()
    return result
