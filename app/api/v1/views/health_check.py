from fastapi import APIRouter, Depends
from starlette import status

from app.api.repositories.common import CRUD
from core.constants.response_messages import ResponseConstants
from core.middlewares.logger import logger
from utils.http_response import http_response

router = APIRouter()


@router.get("/health", status_code=status.HTTP_200_OK)
def health_check():
    return
