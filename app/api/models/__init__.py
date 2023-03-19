from app.api.models.csv import *
from app.api.models.celery import *

"""
Any model need to be add to the __all__ variable to be readable for alembic
and no need to modify env.py in alembic folder
"""

__all__ = ("ProcessConfig", "ProcessMapField", "FileReceiveHistory", "MapperTask")
del globals()["BaseModelMixin"]
