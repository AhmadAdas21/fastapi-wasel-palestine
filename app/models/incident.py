from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func

from app.db.database import Base
class Incident(Base):
    __tablename__="incidents"
    id =Column(Integer , primary_key=True, index=True)
    title =Column(String,nullable=False)
    desctiption=Column(String,nullable=True)
    category=Column(String,nullable=False)
    severity =Column(String,nullable=False)
    status=Column(String, default="open")
    latitude=Column(Float,nullable=False)
    
    longitude=Column(Float,nullable=False)   
    created_at = Column(DateTime(timezone=True), server_default=func.now())
  ## created_at=Column(DateTime(timezone=True), server_default=func.now())