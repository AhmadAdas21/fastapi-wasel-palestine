from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.report import Report, ReportAuditLog
from app.schemas.report_schema import (
    ReportCreate,
    ReportResponse,
    ReportModerationUpdate,
    ReportAuditLogResponse,
)

router = APIRouter()


def calculate_confidence_score(votes_up: int, votes_down: int) -> float:
    total_votes = votes_up + votes_down

    if total_votes == 0:
        return 0.0

    return round(votes_up / total_votes, 2)


def find_duplicate_report(db: Session, report_data: ReportCreate):
    thirty_minutes_ago = datetime.now(timezone.utc) - timedelta(minutes=30)

    return (
        db.query(Report)
        .filter(Report.category == report_data.category)
        .filter(Report.latitude == report_data.latitude)
        .filter(Report.longitude == report_data.longitude)
        .filter(Report.created_at >= thirty_minutes_ago)
        .first()
    )


@router.get("/", response_model=list[ReportResponse])
def get_reports(
    db: Session = Depends(get_db),
    category: str | None = None,
    status: str | None = None,
    sort_by: str = Query("created_at", pattern="^(id|created_at|category|status|confidence_score)$"),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
):
    query = db.query(Report)

    if category:
        query = query.filter(Report.category == category)

    if status:
        query = query.filter(Report.status == status)

    if sort_by == "id":
        query = query.order_by(Report.id)
    elif sort_by == "category":
        query = query.order_by(Report.category)
    elif sort_by == "status":
        query = query.order_by(Report.status)
    elif sort_by == "confidence_score":
        query = query.order_by(Report.confidence_score.desc())
    else:
        query = query.order_by(Report.created_at.desc())

    return query.offset(skip).limit(limit).all()


@router.get("/{report_id}", response_model=ReportResponse)
def get_report_by_id(
    report_id: int,
    db: Session = Depends(get_db),
):
    report = db.query(Report).filter(Report.id == report_id).first()

    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    return report


@router.post("/", response_model=ReportResponse)
def create_report(
    report_data: ReportCreate,
    db: Session = Depends(get_db),
):
    duplicate_report = find_duplicate_report(db, report_data)

    new_report = Report(**report_data.model_dump())

    if duplicate_report:
        new_report.status = "duplicate"
        new_report.duplicate_of_report_id = duplicate_report.id

    db.add(new_report)
    db.commit()
    db.refresh(new_report)

    audit_log = ReportAuditLog(
        report_id=new_report.id,
        action="create_report",
        old_status=None,
        new_status=new_report.status,
        note="Report submitted by citizen",
        performed_by=report_data.reporter_name or "anonymous",
    )

    db.add(audit_log)
    db.commit()

    return new_report


@router.patch("/{report_id}/moderate", response_model=ReportResponse)
def moderate_report(
    report_id: int,
    moderation_data: ReportModerationUpdate,
    db: Session = Depends(get_db),
):
    report = db.query(Report).filter(Report.id == report_id).first()

    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    old_status = report.status

    report.status = moderation_data.status
    report.moderator_note = moderation_data.moderator_note
    report.moderated_at = datetime.now(timezone.utc)

    audit_log = ReportAuditLog(
        report_id=report.id,
        action="moderate_report",
        old_status=old_status,
        new_status=report.status,
        note=moderation_data.moderator_note,
        performed_by=moderation_data.performed_by,
    )

    db.add(audit_log)
    db.commit()
    db.refresh(report)

    return report


@router.post("/{report_id}/vote", response_model=ReportResponse)
def vote_report(
    report_id: int,
    vote: str = Query(..., pattern="^(up|down)$"),
    db: Session = Depends(get_db),
):
    report = db.query(Report).filter(Report.id == report_id).first()

    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    if vote == "up":
        report.votes_up += 1
    else:
        report.votes_down += 1

    report.confidence_score = calculate_confidence_score(
        report.votes_up,
        report.votes_down,
    )

    audit_log = ReportAuditLog(
        report_id=report.id,
        action="vote_report",
        old_status=report.status,
        new_status=report.status,
        note=f"Vote added: {vote}",
        performed_by="community",
    )

    db.add(audit_log)
    db.commit()
    db.refresh(report)

    return report


@router.get("/{report_id}/audit", response_model=list[ReportAuditLogResponse])
def get_report_audit_logs(
    report_id: int,
    db: Session = Depends(get_db),
):
    report = db.query(Report).filter(Report.id == report_id).first()

    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    return (
        db.query(ReportAuditLog)
        .filter(ReportAuditLog.report_id == report_id)
        .order_by(ReportAuditLog.created_at.desc())
        .all()
    )