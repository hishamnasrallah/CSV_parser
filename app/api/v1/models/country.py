import datetime

from core.database.settings.base import Base

from sqlalchemy import Column, Integer, String, Boolean, DateTime

from json import dumps


class CountryConf(Base):
    __tablename__ = "countries"

    id = Column(Integer, autoincrement=True, primary_key=True, index=False, unique=True)
    alpha_2 = Column(String(2), unique=False, index=False, default=None)
    alpha_3 = Column(String(3), unique=False, index=False, default=None)
    name = Column(String)
    description_ar = Column(String, nullable=True)
    description_en = Column(String, nullable=True)
    is_banned = Column(Boolean, nullable=True)
    is_active = Column(Boolean)
    phone_code = Column(String(6))
    note = Column(String, nullable=True)
    created_at = Column(DateTime, unique=False, index=False, default=datetime.datetime.now())
    updated_at = Column(DateTime, unique=False, index=False, default=datetime.datetime.now())

    def as_dict(self):
        data = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        for i in data:
            if isinstance(data[i], (datetime.datetime, datetime.date)):
                data[i] = dumps(data[i], indent=4, sort_keys=True, default=str)
        return data
