from typing import List, Optional
from fastapi import UploadFile, Form, Request
from core.serializers.base import BaseModel
from core.serializers.response import BaseResponse
from app.api.v1.models import Frequency


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
    frequency: Frequency = Frequency


class DashboardResponse(BaseResponse):
    data: List[Dashboard]


class FileProcessConfig(BaseModel):
    pass
