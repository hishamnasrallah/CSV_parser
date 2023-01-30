from typing import List, Optional

from pydantic import BaseModel

from core.serializers.response import BaseResponse


class CountryConfSchema(BaseModel):
    alpha_2: str
    alpha_3: str
    name: str
    description_ar: str
    description_en: str
    is_banned: bool
    is_active: bool
    phone_code: str
    note: str


class CountryConfGetSchema(CountryConfSchema):
    class Config:
        orm_mode = True


class CountryConfOptionalSch(BaseModel):
    alpha_2: Optional[str]
    alpha_3: Optional[str]
    name: Optional[str]
    description_ar: Optional[str]
    description_en: Optional[str]
    is_banned: Optional[bool]
    is_active: Optional[bool]
    phone_code: Optional[str]
    note: Optional[str]


class CountryResponseModel(BaseResponse):
    alpha_2: str
    alpha_3: str
    name: str
    description_ar: str
    description_en: str
    is_banned: bool
    is_active: bool
    phone_code: str
    note: str
# class ShowCountrySch(CountryConfSch):
#     alpha_3: str
#     name: str
#     flag: str
#
#     class Config:
#         orm_mode = True

