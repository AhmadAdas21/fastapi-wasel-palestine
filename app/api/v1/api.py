from fastapi import APIRouter

from app.api.v1.endpoints import incidents, checkpoints

api_router = APIRouter()

api_router.include_router(
    incidents.router,
    prefix="/incidents",
    tags=["Incidents"],
)

api_router.include_router(
    checkpoints.router,
    prefix="/checkpoints",
    tags=["Checkpoints"],
)