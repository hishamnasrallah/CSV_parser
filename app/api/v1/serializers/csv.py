from typing import List, Optional
import datetime
from pydantic import Field, validator

from core.constants.regex import MAPPER_DESCRIPTION_VALIDATION_REGEX
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
        regex=MAPPER_DESCRIPTION_VALIDATION_REGEX,
        error_msg = "Only English text is allowed"

    )
    is_active: bool
    set_active_at: Optional[datetime.datetime] = None

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
        regex=MAPPER_DESCRIPTION_VALIDATION_REGEX,
        error_msg="Only English text is allowed"

    )
    is_active: bool
    set_active_at: Optional[datetime.datetime] = None
    @validator('set_active_at', always=True)
    def check_future_datetime(cls, v, values):
        if v is not None and v <= datetime.datetime.now():
            raise ValueError('Set active datetime must be in the future')
        return v


class FileTaskConfigBaseResponse(BaseModel):
    mapper: List[FieldMapper]
    file_name: str
    frequency: Frequency
    file_path: str
    process_id: int
    description: str = Field(
        ...,
        regex=MAPPER_DESCRIPTION_VALIDATION_REGEX,
        error_msg="Only English text is allowed"

    )
    is_active: bool
    set_active_at: Optional[datetime.datetime] = None

class FileTaskConfigResponse(BaseResponse):
    data: List[FileTaskConfigBaseResponse]


class Dashboard(BaseModel):
    file_name: str
    file_path: str
    frequency: Frequency
    process_id: int
    description: str = Field(
        ...,
        regex=MAPPER_DESCRIPTION_VALIDATION_REGEX,
        error_msg="Only English text is allowed"

    )
    is_active: bool
    set_active_at: Optional[datetime.datetime] = None

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
