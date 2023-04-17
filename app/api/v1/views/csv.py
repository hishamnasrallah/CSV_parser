from fastapi import APIRouter, Depends, status, Request, Query

from app.api.v1.dependancies.authorization import validate_authorization
from app.api.v1.serializers.csv import FileTaskConfigResponse, \
    FileTaskConfigRequest, DashboardResponse, \
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
def create_new_parser(request_body: FileTaskConfigRequest,
                      token=Depends(validate_authorization),
                      db: Session = Depends(CRUD().db_conn)):
    data = csv.create_config(request_body, token, db)
    return http_response(data=data, status=status.HTTP_201_CREATED,
                         message=ResponseConstants.CREATED_MSG)


@router.post("/mappers/{parser_id}/exscute/",
             response_model=FileTaskConfigResponse)
def execute_parser(parser_id: int,
                   token=Depends(validate_authorization),
                   db: Session = Depends(CRUD().db_conn)):
    data = csv.execute_mapper(token, parser_id, db)
    return http_response(data=data, status=status.HTTP_201_CREATED,
                         message=ResponseConstants.CREATED_MSG)


@router.put("/mappers/{parser_id}/", response_model=FileTaskConfigResponse)
def mapper_update(parser_id: int, request_body: FileTaskConfigRequest,
                  token=Depends(validate_authorization),
                  db: Session = Depends(CRUD().db_conn)):
    data = csv.update_config(request_body, parser_id, token, db)
    return http_response(data=data, status=status.HTTP_200_OK,
                         message=ResponseConstants.UPDATED_MSG)


@router.put("/mappers/{parser_id}/change-status/",
            response_model=FileTaskConfigResponse)
def change_mapper_status(parser_id: int,
                         token=Depends(validate_authorization),
                         db: Session = Depends(CRUD().db_conn)):
    data = csv.change_mapper_status(parser_id, token, db)
    return http_response(data=data, status=status.HTTP_200_OK,
                         message=ResponseConstants.UPDATED_MSG)


@router.get("/mappers/", response_model=DashboardResponse)
def get_parsers(request: Request, name: str = Query(None),
                token=Depends(validate_authorization),
                db: Session = Depends(CRUD().db_conn)):
    if name:
        data = csv.mapper_config_filter(token, name, db)
    else:
        data = csv.mappers_configs(token, db)
    return http_response(request=request, data=data, status=status.HTTP_200_OK,
                         message=ResponseConstants.RETRIEVED_MSG)


@router.get("/mapper/{parser_id}/", response_model=MapperDetailResponse)
def get_parser_details(parser_id: int, token=Depends(validate_authorization),
                       db: Session = Depends(CRUD().db_conn)):
    data = csv.mapper_details(token, parser_id, db)
    return http_response(data=data, status=status.HTTP_200_OK,
                         message=ResponseConstants.RETRIEVED_MSG)


@router.post("/mappers/{parser_id}/clone/",
             response_model=FileTaskConfigResponse)
def clone_parser(parser_id: int,
                 token=Depends(validate_authorization),
                 db: Session = Depends(CRUD().db_conn)):
    data = csv.clone_mapper(token, parser_id, db)
    return http_response(data=data, status=status.HTTP_201_CREATED,
                         message=ResponseConstants.CREATED_MSG)


@router.get("/mappers/filter/", response_model=FileTaskResponse)
def mapper_filter(request: Request, name: str,
                  token=Depends(validate_authorization),
                  db: Session = Depends(CRUD().db_conn)):
    data = csv.mapper_config_filter(token, name, db)

    return http_response(request=request, data=data, status=status.HTTP_200_OK,
                         message=ResponseConstants.RETRIEVED_MSG)


@router.get("/mapper/{parser_id}/debug/", response_model=DebugHistoryResponse)
def get_parser_history(request: Request, parser_id: int,
                       token=Depends(validate_authorization)):
    data = csv.mappers_history(token, parser_id)
    return http_response(request=request, data=data, status=status.HTTP_200_OK,
                         message=ResponseConstants.RETRIEVED_MSG)


@router.delete("/mapper/{parser_id}/")
def delete_parser(parser_id: int, token=Depends(validate_authorization),
                  db: Session = Depends(CRUD().db_conn)):
    data = csv.delete_config(parser_id, token, db)
    return http_response(data=data, status=status.HTTP_204_NO_CONTENT,
                         message=ResponseConstants.DELETED_MSG)
