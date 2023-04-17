from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.sql import func


class BaseModelMixin:
    """
    this model used to be inherited using all models,
    so no need to add id, created_at, and updated_at column in the models.
    """

    id = Column(Integer, autoincrement=True, primary_key=True, index=True,
                unique=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(),
                        nullable=False)
