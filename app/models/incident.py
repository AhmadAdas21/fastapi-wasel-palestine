from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func

from app.db.database import Base
class Incident(Base):
    __tablename__="incidents"
    id =coloumn(Integer , primary_key=True, index=True)
    