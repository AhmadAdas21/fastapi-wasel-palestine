from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class AlertSubscriptionCreate(BaseModel):
    user_identifier: str = Field(..., min_length=3, max_length=100)
    area_name: str = Field(..., min_length=2, max_length=100)
    category: Optional[str] = None
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    radius_km: float = Field(5.0, gt=0, le=100)


class AlertSubscriptionResponse(BaseModel):
    id: int
    user_identifier: str
    area_name: str
    category: Optional[str] = None
    latitude: float
    longitude: float
    radius_km: float
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AlertRecordResponse(BaseModel):
    id: int
    subscription_id: int
    incident_id: int
    title: str
    message: str
    is_read: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)