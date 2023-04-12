from fastapi import APIRouter, Depends
from starlette import status

from app.api.repositories.common import CRUD
from core.constants.response_messages import ResponseConstants
from utils.http_response import http_response

router = APIRouter()


@router.get('/beat')
def health_check(db=Depends(CRUD().db_conn)):
    return http_response(message=ResponseConstants.RETRIEVED, status=200)


@router.get("/health", status_code=status.HTTP_200_OK)
def health_check():
    return
