from datetime import datetime
from typing import Optional, Literal

from pydantic import BaseModel, ConfigDict, Field


ReportCategory = Literal[
    "closure",
    "delay",
    "accident",
    "weather_hazard",
    "checkpoint",
    "other",
]

ReportStatus = Literal[
    "pending",
    "verified",
    "rejected",
    "duplicate",
]


class ReportCreate(BaseModel):
    category: ReportCategory
    description: str = Field(..., min_length=10, max_length=500)
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    reporter_name: Optional[str] = Field(None, max_length=100)


class ReportResponse(BaseModel):
    id: int
    category: str
    description: str
    latitude: float
    longitude: float
    reporter_name: Optional[str] = None
    status: str
    confidence_score: float
    votes_up: int
    votes_down: int
    duplicate_of_report_id: Optional[int] = None
    created_at: datetime
    moderated_at: Optional[datetime] = None
    moderator_note: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class ReportModerationUpdate(BaseModel):
    status: ReportStatus
    moderator_note: Optional[str] = None
    performed_by: str = "admin"


class ReportAuditLogResponse(BaseModel):
    id: int
    report_id: int
    action: str
    old_status: Optional[str] = None
    new_status: Optional[str] = None
    note: Optional[str] = None
    performed_by: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)