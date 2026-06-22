from fastapi import APIRouter

from app.api.v1.endpoints import incidents, checkpoints, reports, alerts

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

api_router.include_router(
    reports.router,
    prefix="/reports",
    tags=["Reports"],
)

api_router.include_router(
    alerts.router,
    prefix="/alerts",
    tags=["Alerts"],
)