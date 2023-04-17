from typing import List, Optional
import datetime
import pydash
from pydantic import validator
from app.api.repositories.common import CRUD
from core.exceptions.csv import SetActiveDateMustBeInFuture
from core.exceptions.profile import ProfileDoesNotExistBadRequest, \
    ProfileDeletedError, ProfileIsInactive, \
    ProfileIsMandatory
from core.serializers.base import BaseModel
from core.serializers.response import BaseResponse
from app.api.models import Frequency, Profile


class FileTaskConfig(BaseModel):
    file_name: str
    frequency: Frequency
    file_path: str
    process_id: int
    description: str
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
    description: str
    is_active: bool
    set_active_at: Optional[datetime.datetime] = None
    profile_id: Optional[int] = None

    @validator('set_active_at', always=True)
    def check_future_datetime(cls, v):
        if v is not None and v <= datetime.datetime.now():
            field_name = pydash.camel_case('set_active_at')
            raise SetActiveDateMustBeInFuture(field_name=field_name)

        return v

    @validator('profile_id', always=True)
    def check_profile_id(cls, v, values):
        field_name = pydash.camel_case('profile_id')

        # Add validation to check if the profile is deleted or inactive
        if v:
            db = CRUD().db_conn()
            profile = db.query(Profile).filter(Profile.id == v).first()
            if not profile:
                raise ProfileDoesNotExistBadRequest(field_name=field_name)
            if profile.is_deleted:
                raise ProfileDeletedError(field_name=field_name)
            if not profile.is_active:
                raise ProfileIsInactive(field_name=field_name)
        else:
            if values.get('is_active') or values.get('set_active_at'):
                raise ProfileIsMandatory(field_name=field_name)
        return v


class FileTaskConfigBaseResponse(BaseModel):
    mapper: List[FieldMapper]
    file_name: str
    frequency: Frequency
    file_path: str
    process_id: int
    description: str
    is_active: bool
    set_active_at: Optional[datetime.datetime] = None


class FileTaskConfigResponse(BaseResponse):
    data: List[FileTaskConfigBaseResponse]


class Dashboard(BaseModel):
    file_name: str
    file_path: str
    frequency: Frequency
    process_id: int
    description: str
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
