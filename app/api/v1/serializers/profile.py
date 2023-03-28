from typing import List

from core.serializers.base import BaseModel
from core.serializers.response import BaseResponse


class MapperProfile(BaseModel):
    profile_name: str
    server_connection_username: str
    server_connection_password: str
    profile_description: str
    base_server_url: str
    is_active: bool


class MapperProfileResponse(BaseResponse):
    data: List[MapperProfile]
