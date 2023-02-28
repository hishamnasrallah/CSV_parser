from app.api.models.csv import *

"""
Any model need to be add to the __all__ variable to be readable for alembic
and no need to modify env.py in alembic folder
"""

__all__ = ("ProcessConfig", "ProcessMapField", "FileReceiveHistory")
del globals()["BaseModelMixin"]
