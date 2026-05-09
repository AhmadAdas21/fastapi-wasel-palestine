from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import datetime
class IncidentCreate(BaseModel):
    title:str=Field(...,min_length=3,max_length=100)
    description:Optional[str] = None

    category:str
    severity:str

    latitude:float
    longitude:float
class IncidentUpdate(BaseModel):
    title:Optional[str] = Field(None,min_length=3,max_length=100)
    description:Optional[str] = None

    category:Optional[str] = None
    severity:Optional[str] = None
    status:Optional[str] = None

    latitude:Optional[float]=None
    longitude:Optional[float]=None

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
        model_config = ConfigDict(from_attributes=True)

