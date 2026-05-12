from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.database import Base


class Checkpoint(Base):
    __tablename__ = "checkpoints"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, nullable=False, index=True)
    city = Column(String, nullable=False, index=True)
    description = Column(String, nullable=True)

    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)

    current_status = Column(String, default="open", nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    status_history = relationship(
        "CheckpointStatusHistory",
        back_populates="checkpoint",
        cascade="all, delete-orphan"
    )


class CheckpointStatusHistory(Base):
    __tablename__ = "checkpoint_status_history"

    id = Column(Integer, primary_key=True, index=True)

    checkpoint_id = Column(Integer, ForeignKey("checkpoints.id"), nullable=False)

    old_status = Column(String, nullable=True)
    new_status = Column(String, nullable=False)

    reason = Column(String, nullable=True)
    changed_by = Column(String, default="system")

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    checkpoint = relationship(
        "Checkpoint",
        back_populates="status_history"
    )