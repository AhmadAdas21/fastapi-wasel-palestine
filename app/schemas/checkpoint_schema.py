from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, ConfigDict, Field


class CheckpointCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    city: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = None
    latitude: float
    longitude: float
    current_status: str = "open"


class CheckpointUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=100)
    city: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    current_status: Optional[str] = None


class CheckpointStatusHistoryCreate(BaseModel):
    new_status: str
    reason: Optional[str] = None
    changed_by: str = "system"


class CheckpointStatusHistoryResponse(BaseModel):
    id: int
    checkpoint_id: int
    old_status: Optional[str] = None
    new_status: str
    reason: Optional[str] = None
    changed_by: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CheckpointResponse(BaseModel):
    id: int
    name: str
    city: str
    description: Optional[str] = None
    latitude: float
    longitude: float
    current_status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CheckpointDetailsResponse(CheckpointResponse):
    status_history: List[CheckpointStatusHistoryResponse] = []