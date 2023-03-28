import datetime
from app.api.models.common import BaseModelMixin
from core.database.settings.base import Base
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, BigInteger
import enum
from json import dumps


class Profile(BaseModelMixin, Base):
    company_id = Column(Integer)
    profile_name = Column(String(255), nullable=False)
    server_connection_username = Column(String(255), nullable=False)
    server_connection_password = Column(String(255), nullable=False)
    profile_description = Column(String(256), nullable=False)
    base_server_url = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_deleted = Column(Boolean, default=False)


class MapperProfile(BaseModelMixin, Base):
    mapper_id = Column(Integer, index=True)
    profile_id = Column(Integer, index=True)

