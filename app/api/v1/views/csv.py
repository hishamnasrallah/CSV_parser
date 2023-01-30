from fastapi import APIRouter, Depends, status, Request, UploadFile, File

from app.api.v1.dependancies.authorization import validate_authorization
from app.api.v1.serializers.csv import FileTaskConfigResponse, FileTaskConfigRequest, DashboardResponse
from core.constants.response_messages import ResponseConstants
from utils.http_response import http_response
from utils.upload_manager import UploadHelper
from app.api.v1.repositories import csv
from sqlalchemy.orm import Session
from app.api.v1.repositories.common import CRUD

router = APIRouter(
    prefix='/csv',
    tags=[]
)


# @router.post("/upload", response_model=CSVFileResponse)
# def upload(request: Request, file: CSVFile = Depends(CSVFile.as_form), token=Depends(validate_authorization)):
#     print(token)
#
#     try:
#         _upload_helper = UploadHelper(upload_file=file)
#         result = _upload_helper.save_file()
#         return http_response(data=result,
#                              message=ResponseConstants.CREATED_MSG, status=status.HTTP_201_CREATED)
#     except Exception:
#         return {"message": "There was an error uploading the file"}


# @router.post("/file-process-config", response_model=CSVFileResponse)
# def upload(request: Request, file: CSVFile = Depends(CSVFile.as_form), token=Depends(validate_authorization)):
#     print(token)
#
#     try:
#         _upload_helper = UploadHelper(upload_file=file)
#         result = _upload_helper.save_file()
#         return http_response(data=result,
#                              message=ResponseConstants.CREATED_MSG, status=status.HTTP_201_CREATED)
#     except Exception:
#         return {"message": "There was an error uploading the file"}

@router.post("/file-process-config", response_model=FileTaskConfigResponse)
def create_new_file_process(request: Request, request_body: FileTaskConfigRequest,
                            token=Depends(validate_authorization),
                            db: Session = Depends(CRUD().db_conn)):

    data = csv.create_config(request_body, token,  db)

    return http_response(data=data, status=status.HTTP_201_CREATED,
                         message=ResponseConstants.CREATED_MSG)

# 1
@router.get("/dashboard", response_model=DashboardResponse)
def get_files_configs(request: Request, token=Depends(validate_authorization),
           db: Session = Depends(CRUD().db_conn)):
    # print(token,"adasdasd")

    data = csv.get_dashboard(token, db)
    return http_response(data=data, status=status.HTTP_200_OK,
                         message=ResponseConstants.RETRIEVED_MSG)


# 2 delete config
@router.delete("/dashboard/{id}", response_model=DashboardResponse)
def delete_config(request: Request, id: int, token=Depends(validate_authorization),
           db: Session = Depends(CRUD().db_conn)):

    data = csv.delete_config(id, token, db)
    return http_response(data=data, status=status.HTTP_200_OK,
                         message=ResponseConstants.RETRIEVED_MSG)


# 2 show history
@router.get("/dashboard/{file_id}", response_model=DashboardResponse)
def get_file_history(request: Request, file_id: int, token=Depends(validate_authorization),
           db: Session = Depends(CRUD().db_conn)):
    # print(token,"adasdasd")
    print(file_id)
    data = csv.get_file_process_history(file_id, db)
    return http_response(data=data, status=status.HTTP_200_OK,
                         message=ResponseConstants.RETRIEVED_MSG)


# 2 create new configuration
@router.post("/task", response_model=DashboardResponse)
def upload(request: Request, token=Depends(validate_authorization),
           db: Session = Depends(CRUD().db_conn)):
    # print(token,"adasdasd")

    data = csv.get_dashboard(token, db)
    return http_response(data=data, message=ResponseConstants.CREATED_MSG,
                         status=status.HTTP_201_CREATED)

