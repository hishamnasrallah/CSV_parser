from app.api.v1.views.health_check import router as beat_router
from app.api.v1.views.csv import router as parser_router

__all__ = ("parser_router", "beat_router")
