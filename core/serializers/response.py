from pydantic import Field
from typing import Any

from core.serializers.base import BaseModel


class BaseResponse(BaseModel):
    """
    the base schema for http_response
    """
    status: int
    message_key: str = None
    message: str
    data: Any = None
    meta: dict = None
    request_id: str = Field(..., alias="request-id")
