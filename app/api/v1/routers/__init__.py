from fastapi import APIRouter
from app.api.v1.views import parser_router, beat_router

api_router = APIRouter()
api_router.include_router(parser_router, tags=["parser"], prefix="/parser")
api_router.include_router(beat_router, tags=["beat"])
