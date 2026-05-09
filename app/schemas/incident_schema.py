from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
class IncidentCreate(BaseModel):
    title:str=Field(...,min_length=3,max_length=100)
    description:Optional[str] = None

    category:str
    severity:str

    latitude:float
    longitude:float

class IncidentResponse(BaseModel):
        id :int
        title :str
        description:Optional[str] =None
        category:str
        severity:str
        status:str
        latitude:float
        longitude:float
        created_at:datetime


class Config:
        from_attributes=True