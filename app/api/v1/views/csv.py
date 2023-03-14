from fastapi import APIRouter, Depends, status, Request

from app.api.v1.dependancies.authorization import validate_authorization
from app.api.v1.serializers.csv import FileTaskConfigResponse, FileTaskConfigRequest, DashboardResponse, \
    MapperDetailResponse, DebugHistoryResponse, FileTaskResponse
from core.constants.response_messages import ResponseConstants
from utils.http_response import http_response
from app.api.repositories import csv
from sqlalchemy.orm import Session
from app.api.repositories.common import CRUD

router = APIRouter(
    prefix='/csv/v1',
    tags=[]
)


@router.post("/mappers/", response_model=FileTaskConfigResponse)
def create_new_file_process(request: Request, request_body: FileTaskConfigRequest,
                            token=Depends(validate_authorization),
                            db: Session = Depends(CRUD().db_conn)):

    data = csv.create_config(request_body, token, db)
    return http_response(data=data, status=status.HTTP_201_CREATED,
                         message=ResponseConstants.CREATED_MSG)

@router.post("/mappers/{id}/exscute/", response_model=FileTaskConfigResponse)
def create_new_file_process(request: Request, id:int,
                            token=Depends(validate_authorization),
                            db: Session = Depends(CRUD().db_conn)):

    data = csv.execute_mapper(token, id, db)
    return http_response(data=data, status=status.HTTP_201_CREATED,
                         message=ResponseConstants.CREATED_MSG)


@router.put("/mappers/{id}/", response_model=FileTaskConfigResponse)
def create_new_file_process(request: Request, id:int,  request_body: FileTaskConfigRequest,
                            token=Depends(validate_authorization),
                            db: Session = Depends(CRUD().db_conn)):

    data = csv.update_config(request_body, id, token, db)
    return http_response(data=data, status=status.HTTP_200_OK,
                         message=ResponseConstants.UPDATED_MSG)

@router.put("/mappers/{id}/change-status", response_model=FileTaskConfigResponse)
def change_mapper_status(request: Request, id:int,
                            token=Depends(validate_authorization),
                            db: Session = Depends(CRUD().db_conn)):

    data = csv.change_mapper_status(id, token, db)
    return http_response(data=data, status=status.HTTP_200_OK,
                         message=ResponseConstants.UPDATED_MSG)


@router.get("/mappers", response_model=DashboardResponse)
def get_mappers_configs(request: Request, token=Depends(validate_authorization),
           db: Session = Depends(CRUD().db_conn)):
    data = csv.mappers_configs(token, db)
    return http_response(request=request, data=data, status=status.HTTP_200_OK,
                         message=ResponseConstants.RETRIEVED_MSG)


@router.get("/mapper/{id}", response_model=MapperDetailResponse)
def get_mapper_details(request: Request, id:int, token=Depends(validate_authorization),
           db: Session = Depends(CRUD().db_conn)):

    data = csv.mapper_details(token, id, db)
    return http_response(data=data, status=status.HTTP_200_OK,
                         message=ResponseConstants.RETRIEVED_MSG)

@router.post("/mappers/{id}/clone/", response_model=FileTaskConfigResponse)
def create_new_file_process(request: Request, id:int,
                            token=Depends(validate_authorization),
                            db: Session = Depends(CRUD().db_conn)):

    data = csv.clone_mapper(token, id, db)
    return http_response(data=data, status=status.HTTP_201_CREATED,
                         message=ResponseConstants.CREATED_MSG)

@router.get("/mappers/filter", response_model=FileTaskResponse)
def mapper_filter(request: Request, file_name: str, token=Depends(validate_authorization),
           db: Session = Depends(CRUD().db_conn)):

    data = csv.mapper_config_filter(token, file_name, db)

    return http_response(request=request, data=data, status=status.HTTP_200_OK,
                         message=ResponseConstants.RETRIEVED_MSG)


@router.get("/mapper/{id}/debug", response_model=DebugHistoryResponse)
def get_mapper_history(request: Request, id:int, token=Depends(validate_authorization),
           db: Session = Depends(CRUD().db_conn)):

    data = csv.mappers_history(token, id, db)
    return http_response(request=request, data=data, status=status.HTTP_200_OK,
                         message=ResponseConstants.RETRIEVED_MSG)


@router.delete("/mapper/{id}")
def delete_config(request: Request, id: int, token=Depends(validate_authorization),
           db: Session = Depends(CRUD().db_conn)):

    data = csv.delete_config(id, token, db)
    return http_response(data=data, status=status.HTTP_204_NO_CONTENT,
                         message=ResponseConstants.DELETED_MSG)
