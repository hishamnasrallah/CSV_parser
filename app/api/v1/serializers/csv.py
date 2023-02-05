from typing import List
from pydantic import Field
from core.serializers.base import BaseModel
from core.serializers.response import BaseResponse
from app.api.models import Frequency

# from utils.upload_manager import upload_file

# class CSVFile(BaseModel):
#     filename: str
#     # content_type: str
#     size: int
#
#     @staticmethod
#     def serialize(file: UploadFile):
#         return CSVFile(
#             filename=file.filename,
#             # content_type=file.content_type,
#             size=len(file.read())
#         )

class FileTaskConfig(BaseModel):
    file_name: str
    frequency: Frequency
    file_path: str


class FileTaskConfigRequest(BaseModel):
    # template_file_key: str
    mapper: dict
    file_name: str
    frequency: Frequency
    file_path: str
    process_id: int

    # @classmethod
    # async def as_form(cls, mapper: dict, map_name: str, frequency: Frequency, path: str, file: UploadFile = Form(),):
    #     try:
    #         ext = file.filename.split(".")[-1]
    #         # path = await upload_file(profile_img)
    #
    #         return file
    #     except Exception as e:
    #         print("Exception :", e)


class FileTaskConfigResponse(BaseResponse):
    data: List[FileTaskConfigRequest]


class Dashboard(BaseModel):
    file_name: str
    file_path: str
    frequency: Frequency


class DashboardResponse(BaseResponse):
    data: List[Dashboard]


class MapperDetail(BaseModel):
    configuration_info: Dashboard
    field_name: str
    map_field_name: str


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
