from typing import List
import datetime
from pydantic import Field
from core.serializers.base import BaseModel
from core.serializers.response import BaseResponse
from app.api.models import Frequency


class FileTaskConfig(BaseModel):
    file_name: str
    frequency: Frequency
    file_path: str
    process_id: int
    description: str = Field(
        ...,
        regex="^[a-zA-Z ]*$",
        error_msg = "Only English text is allowed"

    )
    is_active: bool
    set_active_at: datetime.datetime

class FileTaskResponse(BaseResponse):
    data: List[FileTaskConfig]

class FieldMapper(BaseModel):
    field_name: str
    map_field_name: str
    is_ignored: bool


class FileTaskConfigRequest(BaseModel):
    mapper: List[FieldMapper]
    file_name: str
    frequency: Frequency
    file_path: str
    process_id: int
    description: str = Field(
        ...,
        regex="^[a-zA-Z ]*$"
    )
    is_active: bool
    set_active_at: datetime.datetime

class FileTaskConfigBaseResponse(BaseModel):
    mapper: List[FieldMapper]
    file_name: str
    frequency: Frequency
    file_path: str
    process_id: int
    description: str = Field(
        ...,
        regex="^[a-zA-Z ]*$"

    )
    is_active: bool
    set_active_at: datetime.datetime

class FileTaskConfigResponse(BaseResponse):
    data: List[FileTaskConfigBaseResponse]


class Dashboard(BaseModel):
    file_name: str
    file_path: str
    frequency: Frequency
    process_id: int
    description: str = Field(
        ...,
        regex="^[a-zA-Z ]*$"
    )
    is_active: bool
    set_active_at: datetime.datetime

class DashboardResponse(BaseResponse):
    data: List[Dashboard]


class MapperDetail(BaseModel):
    configuration_info: Dashboard
    field_name: str
    map_field_name: str
    is_ignored: bool


class MapperDetailResponse(BaseResponse):
    data: List[MapperDetail]


class DebugHistory(BaseModel):
    id: int
    file_id: int
    file_size_kb: int
    file_name_as_received: str
    task_id: str


class DebugHistoryResponse(BaseResponse):
    data: List[DebugHistory]


class FileProcessConfig(BaseModel):
    pass
