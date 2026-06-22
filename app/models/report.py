from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.sql import func

from app.db.database import Base


class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    category = Column(String, nullable=False, index=True)
    description = Column(String, nullable=False)

    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)

    reporter_name = Column(String, nullable=True)

    status = Column(String, default="pending", nullable=False)
    confidence_score = Column(Float, default=0.0, nullable=False)
    votes_up = Column(Integer, default=0, nullable=False)
    votes_down = Column(Integer, default=0, nullable=False)

    duplicate_of_report_id = Column(Integer, ForeignKey("reports.id"), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    moderated_at = Column(DateTime(timezone=True), nullable=True)
    moderator_note = Column(String, nullable=True)


class ReportAuditLog(Base):
    __tablename__ = "report_audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("reports.id"), nullable=False)

    action = Column(String, nullable=False)
    old_status = Column(String, nullable=True)
    new_status = Column(String, nullable=True)
    note = Column(String, nullable=True)
    performed_by = Column(String, default="system", nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())