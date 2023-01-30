from fastapi import HTTPException, status
from fastapi.encoders import jsonable_encoder

from app.api.v1.repositories.common import CRUD
from app.api.v1.serializers.country import CountryConfSchema, CountryConfOptionalSch
from app.api.v1.models.country import CountryConf


def create(request: CountryConfSchema):
    request.alpha_2 = request.alpha_2.upper()
    new_country = CountryConf(**request.dict())
    operation = CRUD().add(new_country)
    return new_country.as_dict()


def get_all(db):
    countries = db.query(CountryConf).all()
    return countries


def show_detail(alpha_2: str, db):
    alpha_2 = alpha_2.upper()
    country = db.query(CountryConf).filter(CountryConf.alpha_2 == alpha_2).first()
    if not country:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'country with alpha_2 "{alpha_2}" not found')
    return country


def patch(alpha_2: str, request: CountryConfOptionalSch, db):
    alpha_2 = alpha_2.upper()
    country = db.query(CountryConf).filter(CountryConf.alpha_2 == alpha_2)
    if not country.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"country with alpha_2 {alpha_2} not found")
    else:
        stored_country_data = jsonable_encoder(country.first())
        new_data = request.dict()
        for i in new_data:
            if new_data[i] is not None:
                stored_country_data[i] = new_data[i]
        stored_country_data["alpha_2"] = stored_country_data["alpha_2"].upper()
        country.update(stored_country_data)
        db.commit()
        return stored_country_data


def destroy(alpha_2: str, db):
    alpha_2 = alpha_2.upper()
    country = db.query(CountryConf).filter(CountryConf.alpha_2 == alpha_2)

    if not country.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"country with alpha_2 {alpha_2} not found")
    else:
        country.delete(synchronize_session=False)
        db.commit()
