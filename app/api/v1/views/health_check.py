from fastapi import APIRouter
from starlette import status

router = APIRouter()


@router.get("/health", status_code=status.HTTP_200_OK)
def health_check():
    return
