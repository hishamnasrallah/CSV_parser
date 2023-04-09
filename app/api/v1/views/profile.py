
from fastapi import APIRouter, Depends, status, Request, Query

from app.api.v1.dependancies.authorization import validate_authorization
from app.api.v1.serializers.profile import MapperProfile, MapperProfileResponse
from core.constants.response_messages import ResponseConstants
from utils.http_response import http_response
from app.api.repositories import profile
from sqlalchemy.orm import Session
from app.api.repositories.common import CRUD

router = APIRouter(
    prefix='/profiles/v1',
    tags=[]
)


@router.post("/profile/", response_model=MapperProfileResponse)
def create_new_profile(request: Request, request_body: MapperProfile,
                            token=Depends(validate_authorization),
                            db: Session = Depends(CRUD().db_conn)):
    data = profile.create_profile(request_body, token, db)
    return http_response(data=data, status=status.HTTP_201_CREATED,
                         message=ResponseConstants.CREATED_MSG)


@router.get("/profile/{profile_id}/", response_model=MapperProfileResponse)
def get_profile_by_id(request: Request, profile_id: int, db: Session = Depends(CRUD().db_conn), token=Depends(validate_authorization)):
    company_id = token["company"]["id"]
    data = profile.get_profile(profile_id, company_id, db)
    return http_response(data=data, status=status.HTTP_200_OK,
                         message=ResponseConstants.RETRIEVED_MSG)


@router.get("/profiles/", response_model=MapperProfileResponse)
def get_profiles_by_company(request: Request, is_active: bool = Query(None), name: str = Query(None),
                            all:bool = Query(None), token=Depends(validate_authorization),
                            db: Session = Depends(CRUD().db_conn)):
    company_id = token["company"]["id"]
    data = profile.get_profiles_filter(company_id, db, name, is_active)
    return http_response(request=request, all=all, data=data, status=status.HTTP_200_OK,
                         message=ResponseConstants.RETRIEVED_MSG)


@router.put("/profile/{profile_id}/", response_model=MapperProfileResponse)
def update_profile_by_id(profile_id: int, request_body: MapperProfile,
                         token=Depends(validate_authorization),
                         db: Session = Depends(CRUD().db_conn)):
    company_id = token["company"]["id"]
    data = profile.update_profile(profile_id, company_id, request_body, db)
    return http_response(data=data, status=status.HTTP_200_OK,
                         message=ResponseConstants.UPDATED_MSG)

@router.delete("/profile/{profile_id}/")
def delete_profile_by_id(profile_id: int, db: Session = Depends(CRUD().db_conn),
                         token=Depends(validate_authorization)):
    company_id = token["company"]["id"]

    data = profile.delete_profile(profile_id, company_id, db)
    return http_response(data=data, status=status.HTTP_200_OK,
                         message=ResponseConstants.DELETED_MSG)


@router.put("/profile/{id}/change-status/", response_model=MapperProfile)
def change_profile_status(request: Request, id:int,
                            token=Depends(validate_authorization),
                            db: Session = Depends(CRUD().db_conn)):
    company_id = token["company"]["id"]

    data = profile.change_profile_status(id, company_id, db)
    return http_response(data=data, status=status.HTTP_200_OK,
                         message=ResponseConstants.UPDATED_MSG)