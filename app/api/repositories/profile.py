from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Query
from app.api.models import Profile, MapperProfile
from app.api.repositories.common import CRUD
from core.exceptions.profile import ProfileDoesNotExist


def create_profile(request_body, token, db):
    request_dict = request_body.dict()
    request_dict["company_id"] = token["company"]["id"]
    request_dict["is_deleted"] = False
    profile_rec = Profile(**request_dict)
    profile_rec = CRUD().add(profile_rec)
    response = jsonable_encoder(profile_rec)
    return response


def get_profile(profile_id: int, company_id, db):
    profile = db.query(Profile).filter(Profile.id == profile_id,
                                       Profile.company_id == company_id,
                                       Profile.is_deleted == False).first()
    if not profile:
        raise ProfileDoesNotExist
    return jsonable_encoder(profile)


def get_profiles_filter(company_id, db, name_contains=None, is_active=None):
    base_query: Query = db.query(Profile).filter(
        Profile.company_id == company_id,
        Profile.is_deleted == False
    )

    if is_active is not None:
        base_query = base_query.filter(Profile.is_active == is_active)

    if name_contains:
        base_query = base_query.filter(
            Profile.profile_name.ilike(f'%{name_contains}%')
        )

    profiles = base_query.all()
    return jsonable_encoder(profiles)


def update_profile(profile_id: int, company_id, request_body, db):
    profile = db.query(Profile).filter(Profile.id == profile_id,
                                       Profile.is_deleted == False,
                                       Profile.company_id == company_id).first()
    if not profile:
        raise ProfileDoesNotExist
    update_data = request_body.dict()
    for key, value in update_data.items():
        setattr(profile, key, value)
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return jsonable_encoder(profile)


def delete_profile(profile_id: int, company_id, db):
    profile = db.query(Profile).filter(Profile.id == profile_id,
                                       Profile.company_id == company_id,
                                       Profile.is_deleted == False).first()
    if not profile:
        raise ProfileDoesNotExist
    profile.is_deleted = True
    db.query(MapperProfile).filter(
        MapperProfile.profile_id == profile_id).delete()
    db.commit()
    return {"detail": "Profile deleted successfully"}


def change_profile_status(id, company_id, db):
    profile = db.query(Profile).filter(Profile.id == id,
                                       Profile.company_id == company_id,
                                       Profile.is_deleted == False)
    if not profile.first():
        raise ProfileDoesNotExist
    profile_obj = profile.first()
    # TODO: check if i have to deactivate all old mapper when deactivate
    #  here and if i should activate old mappers if i activate here
    if profile_obj.is_active:
        profile_obj.is_active = False
    elif not profile_obj.is_active:
        profile_obj.is_active = True
    else:
        profile_obj.is_active = True
    db.commit()
    return jsonable_encoder(profile_obj)
