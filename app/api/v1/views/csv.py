from fastapi import APIRouter, Depends, status, Request

from app.api.v1.dependancies.authorization import validate_authorization
from app.api.v1.serializers.csv import FileTaskConfigResponse, FileTaskConfigRequest, DashboardResponse, \
    MapperDetailResponse, DebugHistoryResponse
from core.constants.response_messages import ResponseConstants
from utils.http_response import http_response
from app.api.repositories import csv
from sqlalchemy.orm import Session
from app.api.repositories.common import CRUD

router = APIRouter(
    prefix='/csv/v1',
    tags=[]
)


@router.post("/file-process-config", response_model=FileTaskConfigResponse)
def create_new_file_process(request: Request, request_body: FileTaskConfigRequest,
                            token=Depends(validate_authorization),
                            db: Session = Depends(CRUD().db_conn)):

    data = csv.create_config(request_body, token, db)
    return http_response(data=data, status=status.HTTP_201_CREATED,
                         message=ResponseConstants.CREATED_MSG)


# 1
@router.get("/mappers", response_model=DashboardResponse)
def get_mappers_configs(request: Request, token=Depends(validate_authorization),
           db: Session = Depends(CRUD().db_conn)):

    data = csv.mappers_configs(token, db)
    return http_response(data=data, status=status.HTTP_200_OK,
                         message=ResponseConstants.RETRIEVED_MSG)


@router.get("/mapper/{id}", response_model=MapperDetailResponse)
def get_mapper_details(request: Request, id:int, token=Depends(validate_authorization),
           db: Session = Depends(CRUD().db_conn)):

    data = csv.mapper_details(token, id, db)
    return http_response(data=data, status=status.HTTP_200_OK,
                         message=ResponseConstants.RETRIEVED_MSG)


@router.get("/mapper/{id}/debug", response_model=DebugHistoryResponse)
def get_mapper_history(request: Request, id:int, token=Depends(validate_authorization),
           db: Session = Depends(CRUD().db_conn)):

    data = csv.mappers_history(token, id, db)
    return http_response(data=data, status=status.HTTP_200_OK,
                         message=ResponseConstants.RETRIEVED_MSG)


# 2 delete config
@router.delete("/dashboard/{id}")
def delete_config(request: Request, id: int, token=Depends(validate_authorization),
           db: Session = Depends(CRUD().db_conn)):

    data = csv.delete_config(id, token, db)
    return http_response(data=data, status=status.HTTP_204_NO_CONTENT,
                         message=ResponseConstants.DELETED_MSG)


# 2 show history
# @router.get("/dashboard/{file_id}", response_model=DashboardResponse)
# def get_file_history(request: Request, file_id: int, token=Depends(validate_authorization),
#            db: Session = Depends(CRUD().db_conn)):
#     print(file_id)
#     data = csv.get_file_process_history(file_id, db)
#     return http_response(data=data, status=status.HTTP_200_OK,
#                          message=ResponseConstants.RETRIEVED_MSG)

# 2 get company's processes
# @router.get("/processes", response_model=DashboardResponse)
# def get_file_history(request: Request, token=Depends(validate_authorization),
#            db: Session = Depends(CRUD().db_conn)):
#     data = csv.get_company_processes(token, request)
#     return http_response(data=data, status=status.HTTP_200_OK,
#                          message=ResponseConstants.RETRIEVED_MSG)


# # 2 create new configuration
# @router.post("/task", response_model=DashboardResponse)
# def upload(request: Request, token=Depends(validate_authorization),
#            db: Session = Depends(CRUD().db_conn)):
#     # print(token,"adasdasd")
#
#     data = csv.get_dashboard(token, db)
#     return http_response(data=data, message=ResponseConstants.CREATED_MSG,
#                          status=status.HTTP_201_CREATED)

