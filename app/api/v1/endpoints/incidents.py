from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.incident import Incident
from app.schemas.incident_schema import (
    IncidentCreate,
    IncidentUpdate,
    IncidentResponse
)


router = APIRouter()


@router.get("/", response_model=list[IncidentResponse])
def get_incidents(
    db: Session = Depends(get_db),
    category: str | None = None,
    severity: str | None = None,
    status: str | None = None,
    search: str | None = None,
    sort_by: str = Query("id", pattern="^(id|created_at|severity|category)$"),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100)
):
    query = db.query(Incident)

    if category:
        query = query.filter(Incident.category == category)

    if severity:
        query = query.filter(Incident.severity == severity)

    if status:
        query = query.filter(Incident.status == status)

    if search:
        query = query.filter(Incident.title.ilike(f"%{search}%"))

    if sort_by == "created_at":
        query = query.order_by(Incident.created_at.desc())
    elif sort_by == "severity":
        query = query.order_by(Incident.severity)
    elif sort_by == "category":
        query = query.order_by(Incident.category)
    else:
        query = query.order_by(Incident.id)

    incidents = query.offset(skip).limit(limit).all()

    return incidents


@router.get("/{incident_id}", response_model=IncidentResponse)
def get_incident_by_id(
    incident_id: int,
    db: Session = Depends(get_db)
):
    incident = db.query(Incident).filter(Incident.id == incident_id).first()

    if not incident:
        raise HTTPException(
            status_code=404,
            detail="Incident not found"
        )

    return incident


@router.post("/", response_model=IncidentResponse)
def create_incident(
    incident: IncidentCreate,
    db: Session = Depends(get_db)
):
    new_incident = Incident(**incident.model_dump())

    db.add(new_incident)
    db.commit()
    db.refresh(new_incident)

    return new_incident


@router.put("/{incident_id}", response_model=IncidentResponse)
def update_incident(
    incident_id: int,
    incident_data: IncidentUpdate,
    db: Session = Depends(get_db)
):
    incident = db.query(Incident).filter(Incident.id == incident_id).first()

    if not incident:
        raise HTTPException(
            status_code=404,
            detail="Incident not found"
        )

    update_data = incident_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(incident, field, value)

    db.commit()
    db.refresh(incident)

    return incident


@router.delete("/{incident_id}")
def delete_incident(
    incident_id: int,
    db: Session = Depends(get_db)
):
    incident = db.query(Incident).filter(Incident.id == incident_id).first()

    if not incident:
        raise HTTPException(
            status_code=404,
            detail="Incident not found"
        )

    db.delete(incident)
    db.commit()

    return {
        "message": "Incident deleted successfully"
    }